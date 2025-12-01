from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from subscription.decorators import subscription_required, contract_required
from subscription.models import Notification
from doctors.models import Doctor


def login_view(request):
    """Login view"""
    # Redirect to dashboard if already logged in
    if request.user.is_authenticated:
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
            
            # Redirect to next page or dashboard
            next_url = request.GET.get('next', 'core:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password. Please try again.')
    
    return render(request, 'auth/login.html')


def logout_view(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('core:login')


@login_required
@subscription_required
@contract_required
def dashboard(request):
    """Render the main dashboard based on subscription plan."""
    if not hasattr(request, 'company') or not request.company:
        messages.error(request, 'Şirkət məlumatı tapılmadı.')
        return redirect('core:login')
    
    # Get active subscription and plan
    subscription = request.company.active_subscription
    plan_type = 'basic'  # Default
    
    if subscription and subscription.plan:
        plan_type = subscription.plan.plan_type
    
    # Get statistics based on plan level
    from doctors.models import Doctor
    from prescriptions.models import Prescription
    from sales.models import Sale
    from drugs.models import Drug
    from django.utils import timezone
    from datetime import timedelta
    from decimal import Decimal
    
    # Basic stats (available for all plans)
    total_doctors = Doctor.objects.count()
    total_drugs = Drug.objects.filter(is_active=True).count()
    
    # Get date ranges
    today = timezone.now().date()
    last_30_days = today - timedelta(days=30)
    last_7_days = today - timedelta(days=7)
    
    # Prescription stats
    total_prescriptions = Prescription.objects.count()
    prescriptions_last_30 = Prescription.objects.filter(date__gte=last_30_days).count()
    prescriptions_last_7 = Prescription.objects.filter(date__gte=last_7_days).count()
    
    # Sales stats (for professional and enterprise)
    total_sales = 0
    sales_last_30 = 0
    sales_revenue = Decimal('0.00')
    if plan_type in ['professional', 'enterprise']:
        total_sales = Sale.objects.count()
        sales_last_30 = Sale.objects.filter(date__gte=last_30_days).count()
        # Calculate revenue from sales (sum from SaleItem using F expressions)
        from django.db.models import Sum, F
        from sales.models import SaleItem
        revenue_result = SaleItem.objects.aggregate(
            total=Sum(F('quantity') * F('unit_price'))
        )
        sales_revenue = revenue_result['total'] or Decimal('0.00')
    
    # Recent prescriptions - safely handle potential DecimalField errors
    try:
        recent_prescriptions_qs = Prescription.objects.select_related(
            'doctor', 'region'
        ).order_by('-date')[:5]
        
        # Convert to list of dicts to avoid accessing problematic properties
        recent_prescriptions_list = []
        for prescription in recent_prescriptions_qs:
            try:
                # Safely calculate drug_count without accessing items
                from prescriptions.models import PrescriptionItem
                drug_count = PrescriptionItem.objects.filter(
                    prescription_id=prescription.id
                ).count()
                
                # Safely calculate total_amount - handle invalid Decimal values
                from django.db.models import Sum, F, Q
                try:
                    # Filter out items with invalid unit_price
                    total_result = PrescriptionItem.objects.filter(
                        prescription_id=prescription.id
                    ).exclude(
                        Q(unit_price__isnull=True) | Q(unit_price='')
                    ).aggregate(
                        total=Sum(F('quantity') * F('unit_price'))
                    )
                    total_amount = total_result['total'] or Decimal('0.00')
                except (TypeError, ValueError):
                    # If aggregation fails due to invalid data, calculate manually
                    total_amount = Decimal('0.00')
                    try:
                        items = PrescriptionItem.objects.filter(
                            prescription_id=prescription.id
                        ).only('quantity', 'unit_price')
                        for item in items:
                            try:
                                if item.unit_price and item.quantity:
                                    total_amount += Decimal(str(item.unit_price)) * Decimal(str(item.quantity))
                            except (TypeError, ValueError, AttributeError):
                                continue
                    except Exception:
                        total_amount = Decimal('0.00')
                
                recent_prescriptions_list.append({
                    'id': prescription.id,
                    'date': prescription.date,
                    'is_active': prescription.is_active,
                    'doctor': prescription.doctor,
                    'region': prescription.region,
                    'drug_count': drug_count,
                    'total_amount': total_amount,
                })
            except Exception:
                # Skip problematic prescriptions
                continue
        recent_prescriptions = recent_prescriptions_list
    except Exception:
        # If there's an error, return empty list
        recent_prescriptions = []
    
    # Top doctors by prescription count (for professional and enterprise)
    top_doctors = []
    if plan_type in ['professional', 'enterprise']:
        from django.db.models import Count
        try:
            # Get top doctors - use select_related to avoid N+1 queries, but don't access items
            top_doctors_qs = Doctor.objects.select_related('region').annotate(
                prescription_count=Count('prescriptions', distinct=True)
            ).order_by('-prescription_count')[:5]
            
            # Convert to list to avoid queryset evaluation issues with related data
            top_doctors_list = []
            for doctor in top_doctors_qs:
                try:
                    # Safely access region without triggering related queries
                    region_data = None
                    if doctor.region_id:
                        try:
                            region_data = {
                                'id': doctor.region.id,
                                'name': doctor.region.name,
                            }
                        except Exception:
                            pass
                    
                    top_doctors_list.append({
                        'id': doctor.id,
                        'ad': doctor.ad,
                        'code': doctor.code,
                        'region': region_data,
                        'prescription_count': doctor.prescription_count or 0,
                    })
                except Exception:
                    continue
            top_doctors = top_doctors_list
        except Exception:
            top_doctors = []
    
    # Monthly prescription trend (for enterprise)
    monthly_trend = []
    if plan_type == 'enterprise':
        from django.db.models import Count
        from django.db.models.functions import TruncMonth
        
        try:
            monthly_trend = Prescription.objects.annotate(
                month=TruncMonth('date')
            ).values('month').annotate(
                count=Count('id')
            ).order_by('month')[:12]
        except Exception:
            monthly_trend = []
    
    # Region distribution (for enterprise)
    region_stats = []
    if plan_type == 'enterprise':
        from django.db.models import Count
        from regions.models import Region
        
        region_stats = Region.objects.annotate(
            prescription_count=Count('prescriptions')
        ).order_by('-prescription_count')[:5]
    
    context = {
        'plan_type': plan_type,
        'subscription': subscription,
        # Basic stats
        'total_doctors': total_doctors,
        'total_drugs': total_drugs,
        'total_prescriptions': total_prescriptions,
        'prescriptions_last_30': prescriptions_last_30,
        'prescriptions_last_7': prescriptions_last_7,
        # Professional/Enterprise stats
        'total_sales': total_sales,
        'sales_last_30': sales_last_30,
        'sales_revenue': sales_revenue,
        # Lists
        'recent_prescriptions': recent_prescriptions,
        'top_doctors': top_doctors,
        'monthly_trend': monthly_trend,
        'region_stats': region_stats,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def profile(request):
    """Render the profile page."""
    return render(request, 'profile.html')


@login_required
def help_support(request):
    """Help and support page"""
    return render(request, 'help.html')


@login_required
@subscription_required
@contract_required
def settings(request):
    """Settings page"""
    doctors_count = Doctor.objects.count() if hasattr(request, 'company') else 0
    
    context = {
        'doctors_count': doctors_count,
    }
    return render(request, 'settings.html', context)


@login_required
@subscription_required
@contract_required
def notifications(request):
    """View all notifications for the company"""
    if not hasattr(request, 'company') or not request.company:
        messages.error(request, 'Şirkət məlumatı tapılmadı.')
        return redirect('core:dashboard')
    
    # Get all notifications for this company
    notifications_list = Notification.objects.filter(
        company=request.company
    ).order_by('-created_at')
    
    # Filter by read status
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'unread':
        notifications_list = notifications_list.filter(is_read=False)
    elif filter_type == 'read':
        notifications_list = notifications_list.filter(is_read=True)
    elif filter_type == 'important':
        notifications_list = notifications_list.filter(is_important=True)
    
    # Mark as read if requested
    if request.GET.get('mark_read'):
        notification_id = request.GET.get('mark_read')
        try:
            notification = Notification.objects.get(
                id=notification_id,
                company=request.company
            )
            notification.mark_as_read()
            messages.success(request, 'Bildiriş oxunmuş kimi işarələndi.')
            return redirect('core:notifications')
        except Notification.DoesNotExist:
            messages.error(request, 'Bildiriş tapılmadı.')
    
    context = {
        'notifications': notifications_list,
        'filter_type': filter_type,
        'unread_count': Notification.objects.filter(
            company=request.company,
            is_read=False
        ).count(),
    }
    
    return render(request, 'notifications.html', context)


@login_required
@subscription_required
@contract_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read (AJAX endpoint)"""
    if not hasattr(request, 'company') or not request.company:
        return JsonResponse({'success': False, 'error': 'Company not found'}, status=400)
    
    try:
        notification = Notification.objects.get(
            id=notification_id,
            company=request.company
        )
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'}, status=404)


@login_required
@subscription_required
@contract_required
def get_notification_count(request):
    """Get unread notification count (AJAX endpoint)"""
    if not hasattr(request, 'company') or not request.company:
        return JsonResponse({'count': 0})
    
    count = Notification.objects.filter(
        company=request.company,
        is_read=False
    ).count()
    
    return JsonResponse({'count': count})
