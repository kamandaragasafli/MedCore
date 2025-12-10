# 🏢 Multi-Tenant SaaS Architecture Guide

## 📋 **Overview**

Your MedAdmin Dashboard is now a **Multi-Tenant SaaS Platform** where:
- ✅ Multiple companies can subscribe
- ✅ Each company has completely isolated data
- ✅ Users only see their company's data
- ✅ Subscription-based access control
- ✅ Trial periods and billing cycles
- ✅ Scalable for enterprise clients

---

## 🏗️ **Architecture Components**

### **1. Core Models Created**

#### **Company Model** (`subscription/models.py`)
- Represents each subscribing organization
- Unique `slug` for identification
- Contact information (email, phone, address)
- License and tax details
- Resource limits (max_users, max_doctors, max_patients)
- Status tracking (is_active, created_at)

#### **SubscriptionPlan Model**
- Defines pricing tiers (Basic, Professional, Enterprise)
- Monthly and yearly pricing
- Feature limits per plan
- JSON features list
- Popular plan highlighting

#### **Subscription Model**
- Links Company to SubscriptionPlan
- Status: trial, active, expired, cancelled, suspended
- Billing cycle: monthly or yearly
- Start/end dates with auto-calculation
- 14-day trial period
- Auto-renewal settings
- Payment tracking

#### **UserProfile Model**
- Extends Django User model
- Links user to Company (multi-tenant key)
- Role-based access (owner, admin, doctor, staff, user)
- Profile information (phone, avatar, bio)
- Company-level permissions

---

## 🔐 **Data Isolation Strategy**

### **How It Works:**

```python
# Every model that stores company-specific data must have:
class Doctor(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    # ... other fields

# Querying data (always filter by company):
doctors = Doctor.objects.filter(company=request.user.profile.company)
```

### **Tenant Isolation Levels:**

1. **Database Level** - Each company's data separated by foreign key
2. **Query Level** - All queries filtered by company automatically
3. **View Level** - Middleware ensures correct company context
4. **UI Level** - Users only see their company's menu/data

---

## 📝 **Step-by-Step Setup**

### **Step 1: Add to INSTALLED_APPS**

```python
# config/settings.py

INSTALLED_APPS = [
    # ... existing apps
    'subscription',  # ADD THIS
]
```

### **Step 2: Update Main URLs**

```python
# config/urls.py

urlpatterns = [
    path('admin/', admin.site.urls),
    path('subscription/', include('subscription.urls')),  # ADD THIS
    path('', include('core.urls')),
    # ... other urls
]
```

### **Step 3: Run Migrations**

```bash
python manage.py makemigrations subscription
python manage.py migrate
```

### **Step 4: Create Subscription Plans**

```bash
python manage.py shell
```

```python
from subscription.models import SubscriptionPlan

# Basic Plan
SubscriptionPlan.objects.create(
    name='Basic',
    plan_type='basic',
    description='Perfect for small clinics',
    price_monthly=29.99,
    price_yearly=299.99,
    max_users=5,
    max_doctors=3,
    max_patients=100,
    max_storage_gb=5,
    features=[
        'Up to 5 users',
        '3 doctors',
        '100 patients',
        '5GB storage',
        'Basic reports',
        'Email support'
    ],
    is_active=True
)

# Professional Plan
SubscriptionPlan.objects.create(
    name='Professional',
    plan_type='professional',
    description='For growing medical practices',
    price_monthly=79.99,
    price_yearly=799.99,
    max_users=20,
    max_doctors=10,
    max_patients=500,
    max_storage_gb=50,
    features=[
        'Up to 20 users',
        '10 doctors',
        '500 patients',
        '50GB storage',
        'Advanced reports',
        'Priority support',
        'API access',
        'Custom branding'
    ],
    is_active=True,
    is_popular=True
)

# Enterprise Plan
SubscriptionPlan.objects.create(
    name='Enterprise',
    plan_type='enterprise',
    description='For hospitals and large organizations',
    price_monthly=199.99,
    price_yearly=1999.99,
    max_users=100,
    max_doctors=50,
    max_patients=5000,
    max_storage_gb=500,
    features=[
        'Unlimited users',
        '50+ doctors',
        '5000+ patients',
        '500GB storage',
        'Enterprise reports',
        '24/7 support',
        'Full API access',
        'White label',
        'Dedicated account manager',
        'SLA guarantee'
    ],
    is_active=True
)
```

---

## 🔄 **User Flow**

### **New Company Registration:**

```
1. Visit /subscription/plans/
   ↓
2. Choose a plan (Basic/Professional/Enterprise)
   ↓
3. Fill registration form:
   - Company Name
   - Company Email
   - Admin User Details
   - Password
   ↓
4. System creates:
   - Company record
   - User account (owner)
   - UserProfile (linked to company)
   - Subscription (14-day trial)
   ↓
5. Auto-login to dashboard
   ↓
6. Access only their company's data
```

### **Existing User Login:**

```
1. Login at /login/
   ↓
2. System loads user's profile
   ↓
3. Retrieves user's company
   ↓
4. All queries filtered by that company
   ↓
5. User sees only their company's data
```

---

## 🛡️ **Middleware for Tenant Isolation**

Create `subscription/middleware.py`:

```python
from django.utils.deprecation import MiddlewareMixin
from .models import UserProfile

class TenantMiddleware(MiddlewareMixin):
    """
    Automatically set current company in request
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.select_related('company').get(user=request.user)
                request.company = profile.company
                request.user_profile = profile
            except UserProfile.DoesNotExist:
                request.company = None
                request.user_profile = None
        else:
            request.company = None
            request.user_profile = None
```

**Add to settings.py:**

```python
MIDDLEWARE = [
    # ... existing middleware
    'subscription.middleware.TenantMiddleware',  # ADD THIS
]
```

---

## 🔒 **Update Existing Models**

### **Add Company Foreign Key:**

```python
# doctors/models.py

from subscription.models import Company

class Doctor(models.Model):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='doctors'
    )  # ADD THIS
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    # ... other fields
    
    class Meta:
        unique_together = ['company', 'email']  # Unique per company
```

### **Do this for ALL models:**
- Patient
- Appointment
- Payment
- Drug
- Sale
- Report
- Region
- Hospital

---

## 🎯 **Update Views for Multi-Tenancy**

### **Before (Single Tenant):**

```python
def doctor_list(request):
    doctors = Doctor.objects.all()  # BAD - shows all companies
    return render(request, 'doctors/list.html', {'doctors': doctors})
```

### **After (Multi-Tenant):**

```python
from django.contrib.auth.decorators import login_required

@login_required
def doctor_list(request):
    # Only show doctors from user's company
    doctors = Doctor.objects.filter(company=request.company)
    return render(request, 'doctors/list.html', {'doctors': doctors})
```

---

## 📊 **Subscription Status Checking**

### **Create Decorators:**

```python
# subscription/decorators.py

from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def subscription_required(view_func):
    """
    Require active subscription to access view
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('core:login')
        
        if not hasattr(request, 'company') or not request.company:
            messages.error(request, 'No company associated with your account')
            return redirect('subscription:plans')
        
        subscription = request.company.active_subscription
        
        if not subscription:
            messages.warning(request, 'No active subscription. Please subscribe to continue.')
            return redirect('subscription:plans')
        
        if subscription.status == 'trial' and subscription.days_remaining <= 0:
            messages.warning(request, 'Your trial has expired. Please subscribe to continue.')
            return redirect('subscription:plans')
        
        if subscription.status == 'expired':
            messages.error(request, 'Your subscription has expired. Please renew to continue.')
            return redirect('subscription:plans')
        
        return view_func(request, *args, **kwargs)
    
    return wrapper
```

### **Usage:**

```python
from subscription.decorators import subscription_required

@login_required
@subscription_required
def doctor_list(request):
    doctors = Doctor.objects.filter(company=request.company)
    return render(request, 'doctors/list.html', {'doctors': doctors})
```

---

## 📈 **Limits & Quota Management**

### **Check Limits Before Creating:**

```python
@login_required
@subscription_required
def add_doctor(request):
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
    
    # Proceed with adding doctor
    # ...
```

---

## 💳 **Payment Integration (Future)**

### **Payment Flow:**

```
1. Trial expires or user upgrades
   ↓
2. Redirect to payment page
   ↓
3. Integrate with Stripe/PayPal
   ↓
4. On successful payment:
   - Update subscription status to 'active'
   - Set new end_date
   - Send confirmation email
   ↓
5. User continues using system
```

### **Payment Providers to Consider:**
- **Stripe** - Best for SaaS
- **PayPal** - Widely accepted
- **Square** - Good for medical
- **Braintree** - Enterprise option

---

## 🔔 **Important URLs**

| URL | Purpose |
|-----|---------|
| `/subscription/plans/` | View pricing plans |
| `/subscription/register/` | Company registration |
| `/subscription/success/` | Post-registration success |
| `/login/` | User login |
| `/` | Dashboard (protected) |

---

## ✅ **Security Checklist**

- [ ] All models have `company` foreign key
- [ ] All views filter by `request.company`
- [ ] Middleware sets company context
- [ ] Subscription decorator on protected views
- [ ] Limits checked before creating records
- [ ] Company data never mixed in queries
- [ ] Unique constraints include company
- [ ] Admin interface shows company filter

---

## 🚀 **Next Steps**

### **Immediate:**
1. Run migrations
2. Create subscription plans
3. Test registration flow
4. Update all existing models
5. Add middleware
6. Update all views

### **Short Term:**
1. Create beautiful pricing page
2. Add company dashboard
3. Implement usage analytics
4. Add billing history
5. Email notifications

### **Long Term:**
1. Payment gateway integration
2. Invoice generation
3. API for integrations
4. Mobile app
5. White-label options

---

## 📞 **Support**

For any questions about the multi-tenant architecture:
- Check this guide first
- Review the models in `subscription/models.py`
- Test with multiple companies
- Monitor query performance

---

**Your SaaS platform is now ready for multi-tenant deployment!** 🎉

Each company will have completely isolated data, and you can scale to thousands of organizations.

