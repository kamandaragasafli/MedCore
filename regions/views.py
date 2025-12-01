from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Region, City, Clinic, Specialization


@login_required
def region_list(request):
    """List all regions"""
    regions = Region.objects.all()
    return render(request, 'regions/list.html', {'regions': regions})


@login_required
def add_region(request):
    """Add a new region"""
    if request.method == 'POST':
        name = request.POST.get('name')
        code = request.POST.get('code')
        
        if name and code:
            try:
                Region.objects.create(
                    name=name,
                    code=code
                )
                messages.success(request, 'Bölgə uğurla əlavə edildi!')
                return redirect('regions:list')
            except Exception as e:
                messages.error(request, f'Xəta: {str(e)}')
        else:
            messages.error(request, 'Zəhmət olmasa bütün məcburi sahələri doldurun!')
    
    return render(request, 'regions/add.html')


@login_required
def city_list(request):
    """List all cities"""
    cities = City.objects.select_related('region').all()
    return render(request, 'regions/city_list.html', {'cities': cities})


@login_required
def add_city(request):
    """Add a new city"""
    if request.method == 'POST':
        name = request.POST.get('name')
        region_id = request.POST.get('region')
        
        if name and region_id:
            try:
                City.objects.create(
                    name=name,
                    region_id=region_id
                )
                messages.success(request, 'Şəhər uğurla əlavə edildi!')
                return redirect('regions:city_list')
            except Exception as e:
                messages.error(request, f'Xəta: {str(e)}')
        else:
            messages.error(request, 'Zəhmət olmasa bütün məcburi sahələri doldurun!')
    
    regions = Region.objects.all()
    return render(request, 'regions/add_city.html', {'regions': regions})


@login_required
def clinic_list(request):
    """List all clinics"""
    clinics = Clinic.objects.select_related('city__region').all()
    return render(request, 'regions/clinic_list.html', {'clinics': clinics})


@login_required
def add_clinic(request):
    """Add a new clinic"""
    if request.method == 'POST':
        name = request.POST.get('name')
        region_id = request.POST.get('region')
        city_id = request.POST.get('city')
        address = request.POST.get('address')
        phone = request.POST.get('phone', '')
        clinic_type = request.POST.get('type', 'clinic')
        
        if name and region_id and city_id and address:
            try:
                Clinic.objects.create(
                    name=name,
                    region_id=region_id,
                    city_id=city_id,
                    address=address,
                    phone=phone,
                    type=clinic_type
                )
                messages.success(request, 'Klinika uğurla əlavə edildi!')
                return redirect('regions:clinic_list')
            except Exception as e:
                messages.error(request, f'Xəta: {str(e)}')
        else:
            messages.error(request, 'Zəhmət olmasa bütün məcburi sahələri doldurun!')
    
    regions = Region.objects.all()
    cities = City.objects.select_related('region').all()
    return render(request, 'regions/add_clinic.html', {'regions': regions, 'cities': cities})


@login_required
def specialization_list(request):
    """List all specializations"""
    specializations = Specialization.objects.all()
    return render(request, 'regions/specialization_list.html', {'specializations': specializations})


@login_required
def add_specialization(request):
    """Add a new specialization"""
    if request.method == 'POST':
        name = request.POST.get('name')
        
        if name:
            try:
                Specialization.objects.create(
                    name=name
                )
                messages.success(request, 'İxtisas uğurla əlavə edildi!')
                return redirect('regions:specialization_list')
            except Exception as e:
                messages.error(request, f'Xəta: {str(e)}')
        else:
            messages.error(request, 'Zəhmət olmasa bütün məcburi sahələri doldurun!')
    
    return render(request, 'regions/add_specialization.html')
