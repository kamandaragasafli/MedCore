"""
Example script showing how to add company field to existing models
and migrate existing data.

IMPORTANT: This is a reference example. 
Adapt it to your specific models and needs.
"""

# Step 1: Update your model file
# =============================

# Before:
"""
class Doctor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
"""

# After:
"""
from subscription.models import Company

class Doctor(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='doctors',
        null=True,  # Allow null during migration
        blank=True
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    
    class Meta:
        unique_together = ['company', 'email']  # Make unique per company
"""

# Step 2: Create migration
# ========================

"""
python manage.py makemigrations doctors
"""

# Step 3: Run migration
# ====================

"""
python manage.py migrate doctors
"""

# Step 4: Assign existing data to a company (optional)
# ===================================================

"""
python manage.py shell
"""

# In shell:
"""
from subscription.models import Company
from doctors.models import Doctor

# Create a default company for existing data
default_company = Company.objects.create(
    name='Default Company',
    slug='default-company',
    email='admin@default.com',
    is_active=True
)

# Assign all existing doctors to this company
Doctor.objects.all().update(company=default_company)
"""

# Step 5: Make company field required
# ==================================

# Update model again:
"""
class Doctor(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='doctors'
        # Remove null=True, blank=True
    )
    # ... rest of fields
"""

# Create and run migration:
"""
python manage.py makemigrations doctors
python manage.py migrate doctors
"""

# ===========================================
# COMPLETE EXAMPLE: Update All Your Models
# ===========================================

print("""
Models to Update:
================

1. doctors/models.py - Doctor
2. patients/models.py - Patient  
3. appointments/models.py - Appointment
4. payments/models.py - Payment
5. drugs/models.py - Drug
6. sales/models.py - Sale
7. reports/models.py - Report
8. region/models.py - Region
9. hospitals/models.py - Hospital

For each model:
--------------
1. Add company foreign key
2. Make migrations
3. Run migrations
4. Assign existing data to default company
5. Update views to filter by company
6. Update forms to set company automatically

Example View Update:
-------------------

# Before:
def doctor_list(request):
    doctors = Doctor.objects.all()
    return render(request, 'doctors/list.html', {'doctors': doctors})

# After:
from django.contrib.auth.decorators import login_required
from subscription.decorators import subscription_required

@login_required
@subscription_required
def doctor_list(request):
    doctors = Doctor.objects.filter(company=request.company)
    return render(request, 'doctors/list.html', {'doctors': doctors})


Example Create View Update:
---------------------------

# Before:
def add_doctor(request):
    if request.method == 'POST':
        Doctor.objects.create(
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
        )
        return redirect('doctors:list')
    return render(request, 'doctors/add.html')

# After:
@login_required
@subscription_required
def add_doctor(request):
    company = request.company
    
    # Check limits
    if company.doctors.count() >= company.max_doctors:
        messages.error(request, 'Doctor limit reached. Please upgrade.')
        return redirect('subscription:plans')
    
    if request.method == 'POST':
        Doctor.objects.create(
            company=company,  # Always set company!
            first_name=request.POST['first_name'],
            last_name=request.POST['last_name'],
        )
        return redirect('doctors:list')
    return render(request, 'doctors/add.html')


Quick Commands:
==============

# 1. Make all migrations
python manage.py makemigrations

# 2. Run all migrations  
python manage.py migrate

# 3. Initialize plans
python initialize_plans.py

# 4. Create superuser
python manage.py createsuperuser

# 5. Run server
python manage.py runserver

# 6. Access admin
http://localhost:8000/admin/

# 7. Test pricing page
http://localhost:8000/subscription/plans/

# 8. Test registration
http://localhost:8000/subscription/register/
""")

