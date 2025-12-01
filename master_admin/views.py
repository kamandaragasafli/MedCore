"""
Master Admin Panel Views
- Dashboard with platform analytics
- Company management
- User management
- Impersonation/Tenant switching
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User

from subscription.models import Company, Subscription, UserProfile, SubscriptionPlan, Notification, NotificationTemplate
from .decorators import superuser_required
from django.views.decorators.http import require_http_methods


@superuser_required
def master_dashboard(request):
    """
    Master Admin Dashboard
    - Platform-wide analytics
    - Quick stats
    - Recent activity
    """
    
    # Company statistics
    total_companies = Company.objects.count()
    active_companies = Company.objects.filter(
        subscriptions__status='active',
        subscriptions__end_date__gte=timezone.now()
    ).distinct().count()
    
    trial_companies = Company.objects.filter(
        subscriptions__status='trial',
        subscriptions__end_date__gte=timezone.now()
    ).distinct().count()
    
    inactive_companies = total_companies - active_companies - trial_companies
    
    # User statistics
    total_users = User.objects.count()
    total_company_users = UserProfile.objects.count()
    superusers = User.objects.filter(is_superuser=True).count()
    
    # Recent companies (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_companies = Company.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    # Subscription statistics
    subscription_plans = SubscriptionPlan.objects.annotate(
        subscriber_count=Count('subscription', filter=Q(subscription__status='active'))
    )
    
    # Recent companies list
    latest_companies = Company.objects.order_by('-created_at')[:10]
    
    # Active subscriptions
    active_subscriptions = Subscription.objects.filter(
        status='active',
        end_date__gte=timezone.now()
    ).select_related('company', 'plan').order_by('-start_date')[:10]
    
    context = {
        'total_companies': total_companies,
        'active_companies': active_companies,
        'trial_companies': trial_companies,
        'inactive_companies': inactive_companies,
        'total_users': total_users,
        'total_company_users': total_company_users,
        'superusers': superusers,
        'recent_companies': recent_companies,
        'subscription_plans': subscription_plans,
        'latest_companies': latest_companies,
        'active_subscriptions': active_subscriptions,
    }
    
    return render(request, 'master_admin/dashboard.html', context)


@superuser_required
def company_list(request):
    """
    List all companies with detailed information
    - Search and filter
    - Status indicators
    - Quick actions
    """
    
    # Get all companies with related data
    companies = Company.objects.prefetch_related(
        'subscriptions',
        'user_profiles__user'
    ).order_by('-created_at')
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        companies = companies.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(phone__icontains=search_query)
        )
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        companies = companies.filter(
            subscriptions__status='active',
            subscriptions__end_date__gte=timezone.now()
        ).distinct()
    elif status_filter == 'trial':
        companies = companies.filter(
            subscriptions__status='trial',
            subscriptions__end_date__gte=timezone.now()
        ).distinct()
    elif status_filter == 'inactive':
        # Companies without active or trial subscriptions
        active_companies = Company.objects.filter(
            Q(subscriptions__status='active') | Q(subscriptions__status='trial'),
            subscriptions__end_date__gte=timezone.now()
        ).values_list('id', flat=True)
        companies = companies.exclude(id__in=active_companies)
    
    # Annotate with stats
    companies_data = []
    for company in companies:
        # Get active subscription
        active_sub = company.active_subscription
        
        # Get user count
        user_count = company.user_profiles.filter(is_active=True).count()
        
        companies_data.append({
            'company': company,
            'subscription': active_sub,
            'user_count': user_count,
            'status': 'active' if active_sub else 'inactive'
        })
    
    context = {
        'companies_data': companies_data,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'master_admin/company_list.html', context)


@superuser_required
def company_detail(request, company_id):
    """
    Detailed view of a specific company
    - Company info
    - Subscription history
    - Users
    - Statistics
    """
    
    company = get_object_or_404(Company, id=company_id)
    
    # Get all subscriptions
    subscriptions = company.subscriptions.all().order_by('-start_date')
    
    # Get all users
    users = company.user_profiles.select_related('user').all()
    
    # Get active subscription
    active_subscription = company.active_subscription
    
    context = {
        'company': company,
        'subscriptions': subscriptions,
        'users': users,
        'active_subscription': active_subscription,
        'user_count': users.count(),
    }
    
    return render(request, 'master_admin/company_detail.html', context)


@superuser_required
def switch_to_company(request, company_id):
    """
    Impersonate / Switch to company's system
    - Store current state
    - Switch database context
    - Redirect to company dashboard
    """
    
    company = get_object_or_404(Company, id=company_id)
    
    # Store master admin state in session
    request.session['master_admin_mode'] = True
    request.session['master_admin_original_company'] = request.company.id if hasattr(request, 'company') and request.company else None
    request.session['impersonating_company_id'] = company.id
    request.session['impersonating_company_name'] = company.name
    
    # Force set company context
    request.company = company
    
    messages.success(
        request,
        f'Siz indi {company.name} şirkətinin sisteminə daxil oldunuz. '
        f'Master Admin panelinə qayıtmaq üçün "Master Panelə Qayıt" düyməsinə basın.'
    )
    
    return redirect('core:dashboard')


@superuser_required
def exit_impersonation(request):
    """
    Exit company impersonation and return to Master Admin Panel
    """
    
    company_name = request.session.get('impersonating_company_name', 'şirkət')
    
    # Clear impersonation session data
    request.session.pop('master_admin_mode', None)
    request.session.pop('master_admin_original_company', None)
    request.session.pop('impersonating_company_id', None)
    request.session.pop('impersonating_company_name', None)
    
    messages.success(
        request,
        f'{company_name} sistemindən çıxış edildi. Master Admin panelinə qayıtdınız.'
    )
    
    return redirect('master_admin:dashboard')


@superuser_required
def platform_analytics(request):
    """
    Platform-wide analytics and statistics
    - User growth
    - Company growth
    - Revenue analytics
    - Usage statistics
    """
    
    # Time periods
    today = timezone.now()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    last_90_days = today - timedelta(days=90)
    
    # Company growth
    companies_last_7 = Company.objects.filter(created_at__gte=last_7_days).count()
    companies_last_30 = Company.objects.filter(created_at__gte=last_30_days).count()
    companies_last_90 = Company.objects.filter(created_at__gte=last_90_days).count()
    
    # User growth
    users_last_7 = UserProfile.objects.filter(joined_at__gte=last_7_days).count()
    users_last_30 = UserProfile.objects.filter(joined_at__gte=last_30_days).count()
    users_last_90 = UserProfile.objects.filter(joined_at__gte=last_90_days).count()
    
    # Subscription distribution
    subscription_distribution = {}
    for plan in SubscriptionPlan.objects.all():
        count = Subscription.objects.filter(
            plan=plan,
            status='active',
            end_date__gte=today
        ).count()
        subscription_distribution[plan.name] = count
    
    # Company status distribution
    total_companies = Company.objects.count()
    active_count = Company.objects.filter(
        subscriptions__status='active',
        subscriptions__end_date__gte=today
    ).distinct().count()
    trial_count = Company.objects.filter(
        subscriptions__status='trial',
        subscriptions__end_date__gte=today
    ).distinct().count()
    inactive_count = total_companies - active_count - trial_count
    
    # Monthly company registrations (last 12 months)
    monthly_registrations = []
    for i in range(11, -1, -1):
        month_start = today - timedelta(days=30*i)
        month_end = today - timedelta(days=30*(i-1)) if i > 0 else today
        count = Company.objects.filter(
            created_at__gte=month_start,
            created_at__lt=month_end
        ).count()
        monthly_registrations.append({
            'month': month_start.strftime('%b %Y'),
            'count': count
        })
    
    context = {
        'companies_last_7': companies_last_7,
        'companies_last_30': companies_last_30,
        'companies_last_90': companies_last_90,
        'users_last_7': users_last_7,
        'users_last_30': users_last_30,
        'users_last_90': users_last_90,
        'subscription_distribution': subscription_distribution,
        'active_count': active_count,
        'trial_count': trial_count,
        'inactive_count': inactive_count,
        'monthly_registrations': monthly_registrations,
    }
    
    return render(request, 'master_admin/analytics.html', context)


@superuser_required
def user_management(request):
    """
    Manage all platform users
    - Search users
    - View user details
    - Deactivate/activate users
    """
    
    users = UserProfile.objects.select_related('user', 'company').order_by('-joined_at')
    
    # Search
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(user__username__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )
    
    # Role filter
    role_filter = request.GET.get('role', '')
    if role_filter:
        users = users.filter(role=role_filter)
    
    context = {
        'users': users,
        'search_query': search_query,
        'role_filter': role_filter,
    }
    
    return render(request, 'master_admin/user_management.html', context)


@superuser_required
@require_http_methods(["GET", "POST"])
def send_notification(request, company_id=None):
    """
    Send notification to company/companies
    - Single company or multiple companies
    - Different notification types
    """
    
    if request.method == 'POST':
        # Get form data
        company_ids = request.POST.getlist('companies')
        title = request.POST.get('title', '').strip()
        message = request.POST.get('message', '').strip()
        notification_type = request.POST.get('notification_type', 'info')
        is_important = request.POST.get('is_important') == 'on'
        action_url = request.POST.get('action_url', '').strip()
        action_text = request.POST.get('action_text', '').strip()
        
        # Validation
        if not company_ids:
            messages.error(request, 'Ən azı bir şirkət seçilməlidir.')
            return redirect('master_admin:send_notification')
        
        if not title or not message:
            messages.error(request, 'Başlıq və mesaj mütləqdir.')
            return redirect('master_admin:send_notification')
        
        # Send notification to selected companies
        sent_count = 0
        for company_id in company_ids:
            try:
                company = Company.objects.get(id=company_id)
                Notification.objects.create(
                    company=company,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    is_important=is_important,
                    action_url=action_url if action_url else None,
                    action_text=action_text if action_text else None,
                    created_by=request.user
                )
                sent_count += 1
            except Company.DoesNotExist:
                continue
        
        messages.success(
            request, 
            f'{sent_count} şirkətə bildiriş göndərildi.'
        )
        
        # Redirect based on context
        if len(company_ids) == 1:
            return redirect('master_admin:company_detail', company_id=company_ids[0])
        else:
            return redirect('master_admin:send_notification')
    
    # GET request - show form
    companies = Company.objects.filter(is_active=True).order_by('name')
    
    # If company_id is provided, pre-select that company
    selected_company = None
    if company_id:
        try:
            selected_company = Company.objects.get(id=company_id)
        except Company.DoesNotExist:
            pass
    
    # Get notification templates
    templates = NotificationTemplate.objects.filter(is_active=True).order_by('name')
    
    # Check if template_id is provided in query params
    selected_template = None
    template_id = request.GET.get('template_id')
    if template_id:
        try:
            selected_template = NotificationTemplate.objects.get(id=template_id, is_active=True)
        except NotificationTemplate.DoesNotExist:
            pass
    
    context = {
        'companies': companies,
        'selected_company': selected_company,
        'templates': templates,
        'selected_template': selected_template,
    }
    
    return render(request, 'master_admin/send_notification.html', context)

