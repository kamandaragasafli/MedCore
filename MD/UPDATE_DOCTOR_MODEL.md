# 🔧 Update Doctor Model for Multi-Tenancy

## ✅ Issue Fixed

The subscription decorator now works! The problem was that `active_subscription` only looked for `status='active'`, but trial subscriptions have `status='trial'`.

**Fixed in:** `subscription/models.py` - Updated `active_subscription` property to include both active and trial subscriptions.

---

## 📝 Next Step: Add Company to Doctor Model

To enable full multi-tenancy (each company sees only their doctors), follow these steps:

### **Step 1: Update Doctor Model**

Edit `doctors/models.py`:

```python
from django.db import models
from subscription.models import Company  # ADD THIS

class Doctor(models.Model):
    # ADD THIS - Multi-tenant key
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='doctors',
        null=True,  # Allow null during migration
        blank=True
    )
    
    # Existing fields
    ad = models.CharField(max_length=100, verbose_name='Name')
    ixtisas = models.CharField(max_length=100, verbose_name='Specialization')
    email = models.EmailField()
    telefon = models.CharField(max_length=20, verbose_name='Phone')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        # Make email unique per company (not globally)
        unique_together = ['company', 'email']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.ad} - {self.ixtisas}"
```

### **Step 2: Create Migration**

```bash
python manage.py makemigrations doctors
```

You'll be prompted for a default value. Choose option 1 and enter any number (like 1).

### **Step 3: Run Migration**

```bash
python manage.py migrate doctors
```

### **Step 4: Assign Existing Doctors to Companies (If Any)**

If you have existing doctors in the database:

```bash
python manage.py shell
```

Then:

```python
from subscription.models import Company
from doctors.models import Doctor

# Get the first company (or specific one)
company = Company.objects.first()

# Assign all existing doctors to this company
Doctor.objects.filter(company__isnull=True).update(company=company)

# Exit
exit()
```

### **Step 5: Make Company Required**

Edit `doctors/models.py` again and remove `null=True, blank=True`:

```python
company = models.ForeignKey(
    Company,
    on_delete=models.CASCADE,
    related_name='doctors'
    # No null=True, blank=True
)
```

Then:

```bash
python manage.py makemigrations doctors
python manage.py migrate doctors
```

### **Step 6: Update Views**

The views are already prepared! Just uncomment the line in `doctors/views.py`:

```python
@login_required
@subscription_required
def doctor_list(request):
    """List all doctors from user's company"""
    doctors = Doctor.objects.filter(company=request.company)  # UNCOMMENT THIS
    # doctors = Doctor.objects.all()  # REMOVE THIS
    return render(request, 'doctors/list.html', {'doctors': doctors})
```

### **Step 7: Update Add Doctor View**

Edit `doctors/views.py`:

```python
from django.contrib import messages
from django.shortcuts import redirect

@login_required
@subscription_required
def add_doctor(request):
    """Add new doctor with limit checking"""
    company = request.company
    
    # Check if company reached doctor limit
    current_doctors = company.doctors.count()
    if current_doctors >= company.max_doctors:
        messages.error(
            request,
            f'You have reached your plan limit of {company.max_doctors} doctors. '
            'Please upgrade your plan to add more.'
        )
        return redirect('subscription:plans')
    
    if request.method == 'POST':
        # Create doctor
        Doctor.objects.create(
            company=company,  # IMPORTANT - Always set company
            ad=request.POST.get('ad'),
            ixtisas=request.POST.get('ixtisas'),
            email=request.POST.get('email'),
            telefon=request.POST.get('telefon'),
        )
        messages.success(request, 'Doctor added successfully!')
        return redirect('doctors:list')
    
    context = {
        'doctors_count': current_doctors,
        'doctors_limit': company.max_doctors,
        'remaining': company.max_doctors - current_doctors,
    }
    return render(request, 'doctors/add.html', context)
```

---

## 🔄 Apply Same Pattern to All Models

Do the same for:
- ✅ **Patient** model
- ✅ **Appointment** model
- ✅ **Payment** model
- ✅ **Drug** model
- ✅ **Sale** model
- ✅ **Report** model
- ✅ **Region** model
- ✅ **Hospital** model

---

## 🎯 Testing Multi-Tenancy

### **Test 1: Single Company**

1. Login to your account
2. Go to `/doctors/` - should work now!
3. Add a doctor
4. Verify it appears in the list

### **Test 2: Multiple Companies**

1. Open incognito/private window
2. Register a second company at `/subscription/register/`
3. Add doctors to this company
4. Switch back to first company
5. Verify each company sees only their own doctors

### **Test 3: Limits**

1. Check your subscription plan's doctor limit
2. Try to add more doctors than allowed
3. Should see error message and redirect to upgrade page

---

## ✅ Summary

- ✅ **Fixed**: Subscription decorator now recognizes trial subscriptions
- ✅ **Fixed**: Views now use both `@login_required` and `@subscription_required`
- 🔲 **Next**: Add `company` field to Doctor model
- 🔲 **Next**: Update views to filter by company
- 🔲 **Next**: Implement limit checking

---

## 🚀 You're Ready!

Try accessing `/doctors/` now - it should work! 

Once you add the `company` field to the Doctor model, you'll have full multi-tenant isolation.

