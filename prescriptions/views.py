from collections import OrderedDict
from datetime import datetime
from django.template.loader import render_to_string
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone

from subscription.decorators import subscription_required
from doctors.models import Doctor, DoctorPayment
from drugs.models import Drug
from regions.models import Region 
from .models import Prescription, PrescriptionItem  


@login_required
@subscription_required
def add_prescription(request):
    """Add new prescription/recipe"""
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Get form data
                region_id = request.POST.get('region_id')
                doctor_id = request.POST.get('doctor_id')
                date = request.POST.get('date')
           
                # Validation
                if not region_id:
                    messages.error(request, 'Bölgə seçilməlidir.')
                    return redirect('prescriptions:add')
                
                if not doctor_id or not date:
                    messages.error(request, 'Həkim və Tarix doldurulmalıdır.')
                    return redirect('prescriptions:add')
                
                # Collect drug quantities
                selected_drugs = []
                for key, value in request.POST.items():
                    if key.startswith('drug_'):
                        try:
                            drug_id = int(key.split('_')[1])
                            quantity = int(value) if value else 0
                        except (ValueError, IndexError):
                            continue
                        
                        if quantity > 0:
                            selected_drugs.append((drug_id, quantity))
                
                if not selected_drugs:
                    messages.error(request, 'Ən azı bir dərman üçün miqdar daxil edilməlidir.')
                    return redirect('prescriptions:add')
                
                # Get doctor
                doctor = Doctor.objects.get(id=doctor_id)
                region = Region.objects.get(id=region_id)
                
                # Create prescription
                prescription = Prescription.objects.create(
                    region=region,
                    doctor=doctor,
                    date=date
                )
                
                # Add drugs to prescription
                drug_ids = [drug_id for drug_id, _ in selected_drugs]
                drugs_map = {drug.id: drug for drug in Drug.objects.filter(id__in=drug_ids)}
                
                for drug_id, quantity in selected_drugs:
                    drug = drugs_map.get(drug_id)
                    if not drug:
                        continue
                    PrescriptionItem.objects.create(
                        prescription=prescription,
                        drug=drug,
                        quantity=quantity,
                        unit_price=drug.qiymet
                    )
                
                messages.success(request, f'Resept uğurla əlavə edildi! ({prescription.drug_count} dərman)')
                return redirect('prescriptions:add')
                
        except Region.DoesNotExist:
            messages.error(request, 'Bölgə tapılmadı.')
        except Doctor.DoesNotExist:
            messages.error(request, 'Həkim tapılmadı.')
        except Drug.DoesNotExist:
            messages.error(request, 'Dərman tapılmadı.')
        except Exception as e:
            messages.error(request, f'Xəta baş verdi: {str(e)}')
        
        return redirect('prescriptions:add')
    
    # GET request - show form
    drugs = Drug.objects.filter(is_active=True).order_by('ad')
    regions = Region.objects.all().order_by('name')
    
    # Safely load recent prescriptions without accessing problematic Decimal fields
    try:
        recent_prescriptions_qs = Prescription.objects.select_related(
            'region', 'doctor'
        ).order_by('-date')[:5]
        
        # Convert to list of dicts to avoid accessing PrescriptionItem with invalid Decimal data
        recent_prescriptions_list = []
        for prescription in recent_prescriptions_qs:
            try:
                # Safely get items count and basic info without loading Decimal fields
                from django.db.models import Count
                item_count = PrescriptionItem.objects.filter(
                    prescription_id=prescription.id
                ).count()
                
                # Get items with only safe fields
                items_list = []
                try:
                    items_qs = PrescriptionItem.objects.filter(
                        prescription_id=prescription.id
                    ).select_related('drug').only('id', 'quantity', 'drug__ad', 'drug__id')
                    
                    for item in items_qs:
                        try:
                            items_list.append({
                                'drug': {'ad': item.drug.ad if item.drug else '-'},
                                'quantity': item.quantity or 0,
                            })
                        except Exception:
                            continue
                except Exception:
                    pass
                
                recent_prescriptions_list.append({
                    'id': prescription.id,
                    'date': prescription.date,
                    'region': prescription.region,
                    'doctor': prescription.doctor,
                    'patient_name': getattr(prescription, 'patient_name', None),
                    'items': items_list,
                    'item_count': item_count,
                })
            except Exception:
                continue
        recent_prescriptions = recent_prescriptions_list
    except Exception:
        recent_prescriptions = []
    
    context = {
        'regions': regions,
        'drugs': drugs,
        'recent_prescriptions': recent_prescriptions,
    }
    
    return render(request, 'prescriptions/add.html', context)


@login_required
@subscription_required
def prescription_list(request):
    """List all prescriptions with filterable monthly summary"""

    filters = _build_filters(request)
    doctor_summary, stats = _get_filtered_summary(filters, request)
    regions = _get_regions()
    drugs = _get_drugs()
    region_lookup = {str(region.id): region for region in regions}

    context = {
        'doctor_summary': doctor_summary,
        'drugs': drugs,
        'regions': regions,
        'region_lookup': region_lookup,
        'filters': filters,
        'stats': stats,
        'selected_region_label': _get_selected_region_label(filters, region_lookup),
        'region_selected': bool(filters['region']),
    }

    return render(request, 'prescriptions/list.html', context)


@login_required
@subscription_required
def prescription_monthly_report(request):
    from django.db.models import Sum

    # Filter by month if provided
    month = request.GET.get('month')
    year = request.GET.get('year')
    drugs = Drug.objects.filter(is_active=True).order_by('ad')


    if not month:
        month = timezone.now().month
    if not year:
        year = timezone.now().year

    # Filter prescriptions by date
    prescriptions = Prescription.objects.filter(
        date__month=month,
        date__year=year
    ).select_related('doctor').prefetch_related('items__drug')

    # Prepare doctor-based summary
    doctor_summary = {}

    for p in prescriptions:
        doc = p.doctor

        if doc.id not in doctor_summary:
            doctor_summary[doc.id] = {
                'doctor': doc,
                'drugs': {},
                'total_amount': 0
            }

        for item in p.items.all():
            drug_name = item.drug.ad

            # Count quantity (sum)
            doctor_summary[doc.id]['drugs'][drug_name] = (
                doctor_summary[doc.id]['drugs'].get(drug_name, 0) + item.quantity
            )

            # Total price
            doctor_summary[doc.id]['total_amount'] += item.quantity * item.unit_price

    context = {
        'month': month,
        'year': year,
        'doctor_summary': doctor_summary.values(),
        'drugs': drugs,
    }

    return render(request, 'prescriptions/list.html', context)



@login_required
@subscription_required
def doctors_by_region(request, region_id):
    """Return doctors for a given region"""
    doctors = Doctor.objects.filter(region_id=region_id, is_active=True).order_by('ad')
    data = [
        {
            'id': doctor.id,
            'name': doctor.ad,
            'code': doctor.code
        }
        for doctor in doctors
    ]
    return JsonResponse({'doctors': data})

@login_required
@subscription_required
def filter_prescriptions_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Yalnız POST müraciətinə icazə verilir.'}, status=405)

    filters = _build_filters(request)
    doctor_summary, stats = _get_filtered_summary(filters, request)
    regions = _get_regions()
    region_lookup = {str(region.id): region for region in regions}

    context = {
        'doctor_summary': doctor_summary,
        'stats': stats,
        'drugs': _get_drugs(),
        'selected_region_label': _get_selected_region_label(filters, region_lookup),
        'region_selected': bool(filters['region']),
    }

    html = render_to_string("prescriptions/table_partial.html", context, request=request)
    return JsonResponse({"html": html})


def _build_filters(request):
    data = request.POST if request.method == 'POST' else request.GET
    return {
        'region': (data.get('region') or '').strip(),
        'start_date': (data.get('start_date') or '').strip(),
        'end_date': (data.get('end_date') or '').strip(),
        'doctor': (data.get('doctor') or '').strip(),
    }


def _parse_date(value, request=None):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        if request:
            messages.error(request, 'Tarix formatı yanlışdır. YYYY-MM-DD olaraq daxil edin.')
        return None


def _get_filtered_summary(filters, request=None):
    parse_request = request if request is not None and request.method == 'GET' else None
    start_date = _parse_date(filters['start_date'], request=parse_request)
    end_date = _parse_date(filters['end_date'], request=parse_request)

    if not filters['region']:
        return [], {'doctor_count': 0, 'total_amount': 0, 'total_quantity': 0}

    doctor_qs = (
        Doctor.objects
        .select_related('region')
        .filter(region_id=filters['region'])
    )

    if filters['doctor']:
        doctor_qs = doctor_qs.filter(
            Q(ad__icontains=filters['doctor']) |
            Q(code__icontains=filters['doctor'])
        )

    doctor_qs = doctor_qs.order_by('ad')

    doctor_summary = OrderedDict()

    for doctor in doctor_qs:
        doctor_summary[doctor.id] = {
            'doctor': doctor,
            'region': doctor.region,
            'drugs': {},
            'total_amount': 0,
            'total_quantity': 0,
            'last_date': None,
        }

    if not doctor_summary:
        return [], {'doctor_count': 0, 'total_amount': 0, 'total_quantity': 0}

    doctor_ids = list(doctor_summary.keys())

    prescriptions = (
        Prescription.objects
        .select_related('doctor', 'region')
        .prefetch_related('items__drug')
        .filter(doctor_id__in=doctor_ids)
        .order_by('-date')
    )

    if start_date:
        prescriptions = prescriptions.filter(date__gte=start_date)

    if end_date:
        prescriptions = prescriptions.filter(date__lte=end_date)

    for prescription in prescriptions:
        summary = doctor_summary.get(prescription.doctor_id)
        if not summary:
            continue

        if prescription.date and (not summary['last_date'] or prescription.date > summary['last_date']):
            summary['last_date'] = prescription.date

        for item in prescription.items.all():
            drug_name = item.drug.ad
            summary['drugs'][drug_name] = summary['drugs'].get(drug_name, 0) + item.quantity
            summary['total_quantity'] += item.quantity
            summary['total_amount'] += item.quantity * item.unit_price

    summary_list = list(doctor_summary.values())
    _attach_last_payments(summary_list)

    stats = {
        'doctor_count': len(summary_list),
        'total_amount': sum(entry['total_amount'] for entry in summary_list),
        'total_quantity': sum(entry['total_quantity'] for entry in summary_list),
    }

    return summary_list, stats


def _attach_last_payments(summary_list, limit=1):
    if not summary_list:
        return

    doctor_ids = [entry['doctor'].id for entry in summary_list if entry.get('doctor')]
    if not doctor_ids:
        return

    payments_map = {doctor_id: [] for doctor_id in doctor_ids}
    payments = (
        DoctorPayment.objects
        .select_related('doctor')
        .filter(doctor_id__in=doctor_ids)
        .order_by('doctor_id', '-date', '-created_at')
    )

    for payment in payments:
        bucket = payments_map.get(payment.doctor_id)
        if bucket is None:
            continue
        if len(bucket) < limit:
            bucket.append(payment)

    for entry in summary_list:
        entry['last_payments'] = payments_map.get(entry['doctor'].id, [])


def _get_regions():
    return Region.objects.order_by('name')


def _get_drugs():
    return Drug.objects.filter(is_active=True).order_by('ad')


def _get_selected_region_label(filters, region_lookup):
    selected = region_lookup.get(filters['region'])
    return selected.name if selected else ''


def _get_last_payments(doctor):
    try:
        return DoctorPayment.objects.filter(doctor=doctor).order_by('-date')[:3].values('date', 'amount')
        
    except Exception as e:
        return []
    return []



