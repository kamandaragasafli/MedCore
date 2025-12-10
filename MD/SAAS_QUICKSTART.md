# 🚀 SaaS Multi-Tenant Quick Start Guide

## Step-by-Step Setup Instructions

### **1. Run Migrations**

```bash
python manage.py makemigrations
python manage.py migrate
```

This will create all the necessary database tables for:
- Company
- SubscriptionPlan
- Subscription
- UserProfile

---

### **2. Initialize Subscription Plans**

```bash
python initialize_plans.py
```

This will create three subscription plans:
- **Basic**: $29.99/month
- **Professional**: $79.99/month (Popular)
- **Enterprise**: $199.99/month

---

### **3. Create a Superuser (Optional)**

```bash
python manage.py createsuperuser
```

Use this to access Django admin at `/admin/`

---

### **4. Test the System**

#### **A. View Pricing Plans**
```
http://localhost:8000/subscription/plans/
```

#### **B. Register a Company**
```
http://localhost:8000/subscription/register/
```

Fill in:
- Company information
- Admin user details
- Select a plan
- Choose billing cycle

#### **C. Login**
```
http://localhost:8000/login/
```

After registration, you'll be auto-logged in and redirected to dashboard.

---

## 📊 Available URLs

| URL | Description |
|-----|-------------|
| `/subscription/plans/` | View all subscription plans |
| `/subscription/register/` | Register a new company |
| `/login/` | User login |
| `/logout/` | User logout |
| `/` | Dashboard (requires login + subscription) |
| `/admin/` | Django admin panel |

---

## 🔧 Update Existing Models for Multi-Tenancy

### **Example: Update Doctor Model**

```python
# doctors/models.py

from django.db import models
from subscription.models import Company

class Doctor(models.Model):
    # ADD THIS - Multi-tenant key
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='doctors'
    )
    
    # Existing fields
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    specialization = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    
    class Meta:
        # Ensure email is unique per company
        unique_together = ['company', 'email']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company.name}"
```

**Then run:**
```bash
python manage.py makemigrations doctors
python manage.py migrate doctors
```

---

### **Example: Update Doctor Views**

```python
# doctors/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from subscription.decorators import subscription_required
from .models import Doctor

@login_required
@subscription_required
def doctor_list(request):
    """Show only doctors from user's company"""
    doctors = Doctor.objects.filter(company=request.company)
    
    context = {
        'doctors': doctors,
        'company': request.company,
    }
    return render(request, 'doctors/list.html', context)


@login_required
@subscription_required
def add_doctor(request):
    """Add new doctor with limit checking"""
    company = request.company
    
    # Check if limit reached
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
        doctor = Doctor.objects.create(
            company=company,  # IMPORTANT - Always set company
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            email=request.POST.get('email'),
            # ... other fields
        )
        
        messages.success(request, 'Doctor added successfully!')
        return redirect('doctors:list')
    
    return render(request, 'doctors/add.html')
```

---

## 🔒 Apply to All Models

Update these models with `company` foreign key:
- ✅ **Doctor** (doctors/models.py)
- ✅ **Patient** (patients/models.py)
- ✅ **Appointment** (appointments/models.py)
- ✅ **Payment** (payments/models.py)
- ✅ **Drug** (drugs/models.py)
- ✅ **Sale** (sales/models.py)
- ✅ **Report** (reports/models.py)
- ✅ **Region** (region/models.py)
- ✅ **Hospital** (hospitals/models.py)

---

## 📋 Checklist

- [ ] Migrations run successfully
- [ ] Subscription plans created
- [ ] Can access pricing page
- [ ] Can register a company
- [ ] Registration creates company + user + profile
- [ ] 14-day trial starts automatically
- [ ] Can login and access dashboard
- [ ] Middleware sets `request.company`
- [ ] All models have company foreign key
- [ ] All views filter by company
- [ ] Limits enforced (users, doctors, patients)

---

## 🎯 Testing Multi-Tenancy

### **Test 1: Register Two Companies**

1. Register Company A (e.g., "City Hospital")
2. Logout
3. Register Company B (e.g., "County Clinic")
4. Add data (doctors, patients) to Company B
5. Logout and login as Company A
6. Verify you ONLY see Company A's data

### **Test 2: Check Limits**

1. Login as a company with Basic plan (3 doctors max)
2. Try to add 4th doctor
3. Should show error and redirect to upgrade page

### **Test 3: Trial Expiry**

1. In Django admin, find the subscription
2. Set `end_date` to yesterday
3. Try to access dashboard
4. Should redirect to subscription plans

---

## 🆘 Troubleshooting

### **Issue: "No company associated with your account"**

**Solution:**
```python
# In Django shell
python manage.py shell

from django.contrib.auth.models import User
from subscription.models import UserProfile, Company

user = User.objects.get(username='your_username')
company = Company.objects.first()

UserProfile.objects.create(
    user=user,
    company=company,
    role='owner'
)
```

### **Issue: Middleware not working**

**Check:**
1. `TenantMiddleware` is in `MIDDLEWARE` list in settings.py
2. It's AFTER `AuthenticationMiddleware`

### **Issue: No plans showing**

**Run:**
```bash
python initialize_plans.py
```

---

## 🎨 Customize Plans

Edit `initialize_plans.py` to change:
- Prices
- Limits (users, doctors, patients)
- Features list
- Plan names

Then run:
```bash
python initialize_plans.py
```

---

## 💳 Payment Integration (Coming Soon)

When ready to add payments:
1. Sign up for Stripe/PayPal
2. Add payment form to registration
3. Process payment on subscription create
4. Set subscription status to 'active' after payment
5. Handle renewals and failures

---

## 🔔 Email Notifications (Coming Soon)

Setup email for:
- Welcome email on registration
- Trial expiry warning (7 days, 3 days, 1 day)
- Subscription expired
- Payment failed
- Invitation emails for new users

---

## ✅ You're Ready!

Your multi-tenant SaaS platform is now set up! Each company will have:
- ✅ Isolated data
- ✅ Subscription management
- ✅ Resource limits
- ✅ Trial period
- ✅ Role-based access

**Next Steps:**
1. Update all your models with company foreign key
2. Update all views to filter by company
3. Add subscription checks to protected views
4. Implement payment gateway
5. Set up email notifications

---

**Need help?** Check `SAAS_MULTI_TENANT_GUIDE.md` for detailed architecture information.

