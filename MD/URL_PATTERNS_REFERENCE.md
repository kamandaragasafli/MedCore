# Django URL Patterns - Organized by Apps

This guide shows how to organize URLs across different Django apps.

---

## 📁 Project Structure

```
your_project/
├── core/               # Main app (Dashboard, Help)
├── doctors/            # Doctors management
├── payments/           # Payment management
├── datasiya/           # Data management
├── drugs/              # Drugs/Medications
├── registrations/      # Registrations
├── sales/              # Sales management
├── reports/            # Reports
├── locations/          # Regions and Hospitals
└── accounts/           # User accounts (Profile, Settings, Auth)
```

---

## 🔗 Main Project URLs (`project/urls.py`)

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('doctors/', include('doctors.urls')),
    path('payments/', include('payments.urls')),
    path('datasiya/', include('datasiya.urls')),
    path('drugs/', include('drugs.urls')),
    path('registrations/', include('registrations.urls')),
    path('sales/', include('sales.urls')),
    path('reports/', include('reports.urls')),
    path('locations/', include('locations.urls')),
    path('accounts/', include('accounts.urls')),
]
```

---

## 1️⃣ **Core App** (`core/urls.py`)

```python
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('help/', views.help_support, name='help'),
]
```

**Views** (`core/views.py`):
```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    """Main dashboard view"""
    return render(request, 'index.html')

@login_required
def help_support(request):
    """Help and support page"""
    return render(request, 'help.html')
```

---

## 2️⃣ **Doctors App** (`doctors/urls.py`)

```python
from django.urls import path
from . import views

app_name = 'doctors'

urlpatterns = [
    path('', views.doctor_list, name='list'),
    path('add/', views.add_doctor, name='add'),
    path('<int:pk>/', views.doctor_detail, name='detail'),
    path('<int:pk>/edit/', views.edit_doctor, name='edit'),
    path('<int:pk>/delete/', views.delete_doctor, name='delete'),
]
```

**Views** (`doctors/views.py`):
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Doctor
from .forms import DoctorForm

@login_required
def doctor_list(request):
    """List all doctors"""
    doctors = Doctor.objects.all()
    return render(request, 'doctors/list.html', {'doctors': doctors})

@login_required
def add_doctor(request):
    """Add new doctor"""
    if request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('doctors:list')
    else:
        form = DoctorForm()
    return render(request, 'doctors/add.html', {'form': form})

@login_required
def doctor_detail(request, pk):
    """View doctor details"""
    doctor = get_object_or_404(Doctor, pk=pk)
    return render(request, 'doctors/detail.html', {'doctor': doctor})

@login_required
def edit_doctor(request, pk):
    """Edit doctor information"""
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            return redirect('doctors:detail', pk=pk)
    else:
        form = DoctorForm(instance=doctor)
    return render(request, 'doctors/edit.html', {'form': form, 'doctor': doctor})

@login_required
def delete_doctor(request, pk):
    """Delete doctor"""
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        doctor.delete()
        return redirect('doctors:list')
    return render(request, 'doctors/delete_confirm.html', {'doctor': doctor})
```

---

## 3️⃣ **Payments App** (`payments/urls.py`)

```python
from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='list'),
    path('add/', views.add_payment, name='add'),
    path('<int:pk>/', views.payment_detail, name='detail'),
]
```

**Views** (`payments/views.py`):
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Payment
from .forms import PaymentForm

@login_required
def payment_list(request):
    """List all payments"""
    payments = Payment.objects.all().order_by('-date')
    return render(request, 'payments/list.html', {'payments': payments})

@login_required
def add_payment(request):
    """Add new payment"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('payments:list')
    else:
        form = PaymentForm()
    return render(request, 'payments/add.html', {'form': form})

@login_required
def payment_detail(request, pk):
    """View payment details"""
    payment = get_object_or_404(Payment, pk=pk)
    return render(request, 'payments/detail.html', {'payment': payment})
```

---

## 4️⃣ **Datasiya App** (`datasiya/urls.py`)

```python
from django.urls import path
from . import views

app_name = 'datasiya'

urlpatterns = [
    path('', views.datasiya_index, name='index'),
]
```

**Views** (`datasiya/views.py`):
```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def datasiya_index(request):
    """Data management dashboard"""
    return render(request, 'datasiya/index.html')
```

---

## 5️⃣ **Drugs App** (`drugs/urls.py`)

```python
from django.urls import path
from . import views

app_name = 'drugs'

urlpatterns = [
    path('', views.drug_list, name='list'),
    path('add/', views.add_drug, name='add'),
    path('<int:pk>/', views.drug_detail, name='detail'),
]
```

**Views** (`drugs/views.py`):
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Drug
from .forms import DrugForm

@login_required
def drug_list(request):
    """List all drugs"""
    drugs = Drug.objects.all()
    return render(request, 'drugs/list.html', {'drugs': drugs})

@login_required
def add_drug(request):
    """Add new drug"""
    if request.method == 'POST':
        form = DrugForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('drugs:list')
    else:
        form = DrugForm()
    return render(request, 'drugs/add.html', {'form': form})

@login_required
def drug_detail(request, pk):
    """View drug details"""
    drug = get_object_or_404(Drug, pk=pk)
    return render(request, 'drugs/detail.html', {'drug': drug})
```

---

## 6️⃣ **Registrations App** (`registrations/urls.py`)

```python
from django.urls import path
from . import views

app_name = 'registrations'

urlpatterns = [
    path('add/', views.add_registration, name='add'),
    path('monthly/', views.monthly_registrations, name='monthly'),
]
```

**Views** (`registrations/views.py`):
```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Registration
from .forms import RegistrationForm

@login_required
def add_registration(request):
    """Add new registration"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('registrations:monthly')
    else:
        form = RegistrationForm()
    return render(request, 'registrations/add.html', {'form': form})

@login_required
def monthly_registrations(request):
    """View monthly registrations"""
    registrations = Registration.objects.all().order_by('-date')
    return render(request, 'registrations/monthly.html', {'registrations': registrations})
```

---

## 7️⃣ **Sales App** (`sales/urls.py`)

```python
from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    path('', views.sale_list, name='list'),
    path('add/', views.add_sale, name='add'),
    path('<int:pk>/', views.sale_detail, name='detail'),
]
```

**Views** (`sales/views.py`):
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Sale
from .forms import SaleForm

@login_required
def sale_list(request):
    """List all sales"""
    sales = Sale.objects.all().order_by('-date')
    return render(request, 'sales/list.html', {'sales': sales})

@login_required
def add_sale(request):
    """Add new sale"""
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sales:list')
    else:
        form = SaleForm()
    return render(request, 'sales/add.html', {'form': form})

@login_required
def sale_detail(request, pk):
    """View sale details"""
    sale = get_object_or_404(Sale, pk=pk)
    return render(request, 'sales/detail.html', {'sale': sale})
```

---

## 8️⃣ **Reports App** (`reports/urls.py`)

```python
from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('monthly/', views.monthly_report, name='monthly'),
    path('old/', views.old_report, name='old'),
]
```

**Views** (`reports/views.py`):
```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def monthly_report(request):
    """Monthly reports"""
    return render(request, 'reports/monthly.html')

@login_required
def old_report(request):
    """Old reports archive"""
    return render(request, 'reports/old.html')
```

---

## 9️⃣ **Locations App** (`locations/urls.py`)

```python
from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('regions/', views.region_list, name='regions'),
    path('hospitals/', views.hospital_list, name='hospitals'),
]
```

**Views** (`locations/views.py`):
```python
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Region, Hospital

@login_required
def region_list(request):
    """List all regions"""
    regions = Region.objects.all()
    return render(request, 'locations/regions.html', {'regions': regions})

@login_required
def hospital_list(request):
    """List all hospitals"""
    hospitals = Hospital.objects.all()
    return render(request, 'locations/hospitals.html', {'hospitals': hospitals})
```

---

## 🔟 **Accounts App** (`accounts/urls.py`)

```python
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Profile & Settings
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('notifications/', views.notifications, name='notifications'),
]
```

**Views** (`accounts/views.py`):
```python
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

@login_required
def profile(request):
    """User profile page"""
    return render(request, 'accounts/profile.html')

@login_required
def settings(request):
    """User settings page"""
    return render(request, 'accounts/settings.html')

@login_required
def notifications(request):
    """User notifications page"""
    return render(request, 'accounts/notifications.html')

def logout_view(request):
    """Logout user"""
    logout(request)
    return redirect('accounts:login')
```

---

## 📋 **URL Namespace Summary**

### Used in base.html:

| Feature | App Namespace | URL Name | Full URL Tag |
|---------|--------------|----------|--------------|
| Dashboard | `core` | `dashboard` | `{% url 'core:dashboard' %}` |
| Doctors List | `doctors` | `list` | `{% url 'doctors:list' %}` |
| Add Doctor | `doctors` | `add` | `{% url 'doctors:add' %}` |
| Payments List | `payments` | `list` | `{% url 'payments:list' %}` |
| Add Payment | `payments` | `add` | `{% url 'payments:add' %}` |
| Datasiya | `datasiya` | `index` | `{% url 'datasiya:index' %}` |
| Drugs List | `drugs` | `list` | `{% url 'drugs:list' %}` |
| Add Registration | `registrations` | `add` | `{% url 'registrations:add' %}` |
| Monthly Registrations | `registrations` | `monthly` | `{% url 'registrations:monthly' %}` |
| Sales List | `sales` | `list` | `{% url 'sales:list' %}` |
| Add Sale | `sales` | `add` | `{% url 'sales:add' %}` |
| Monthly Report | `reports` | `monthly` | `{% url 'reports:monthly' %}` |
| Old Report | `reports` | `old` | `{% url 'reports:old' %}` |
| Profile | `accounts` | `profile` | `{% url 'accounts:profile' %}` |
| Settings | `accounts` | `settings` | `{% url 'accounts:settings' %}` |
| Notifications | `accounts` | `notifications` | `{% url 'accounts:notifications' %}` |
| Logout | `accounts` | `logout` | `{% url 'accounts:logout' %}` |
| Regions | `locations` | `regions` | `{% url 'locations:regions' %}` |
| Hospitals | `locations` | `hospitals` | `{% url 'locations:hospitals' %}` |
| Help | `core` | `help` | `{% url 'core:help' %}` |

---

## 🚀 **Quick Setup Commands**

```bash
# Create all apps
python manage.py startapp doctors
python manage.py startapp payments
python manage.py startapp datasiya
python manage.py startapp drugs
python manage.py startapp registrations
python manage.py startapp sales
python manage.py startapp reports
python manage.py startapp locations
python manage.py startapp accounts
```

**Add to `settings.py` INSTALLED_APPS:**
```python
INSTALLED_APPS = [
    # ... default apps
    'core',
    'doctors',
    'payments',
    'datasiya',
    'drugs',
    'registrations',
    'sales',
    'reports',
    'locations',
    'accounts',
]
```

---

## ✅ **Active State Blocks**

Use these in your child templates:
```python
{% block active_dashboard %}{% endblock %}
{% block active_doctors %}{% endblock %}
{% block active_add_doctor %}{% endblock %}
{% block active_payments %}{% endblock %}
{% block active_add_payment %}{% endblock %}
{% block active_datasiya %}{% endblock %}
{% block active_drugs %}{% endblock %}
{% block active_add_registration %}{% endblock %}
{% block active_spellings %}{% endblock %}
{% block active_sales %}{% endblock %}
{% block active_add_sale %}{% endblock %}
{% block active_reports %}{% endblock %}
{% block active_old_report %}{% endblock %}
{% block active_profile %}{% endblock %}
{% block active_regions %}{% endblock %}
{% block active_hospital %}{% endblock %}
```

---

**Now your URLs are properly organized by their respective apps!** 🎉
