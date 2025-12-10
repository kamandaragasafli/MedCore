# Production Setup Guide

## Changes Made

### 1. Contract Agreement System
- Added `ContractAgreement` model to track user acceptance of terms
- Created contract view that displays after registration
- Users must agree to contract before accessing admin panel
- Contract agreement is tracked with IP address and timestamp

### 2. Payment Required (No Free Trial)
- Changed subscription status from 'trial' to 'active' on registration
- All subscriptions now require payment
- Removed free trial period

### 3. Registration Flow
- After registration → Contract page → Admin panel
- Contract must be agreed before accessing any protected pages
- Contract decorator added to enforce agreement

### 4. Data Cleanup Command
- Created management command: `clean_default_data`
- Removes all default/seed data (doctors, drugs, prescriptions, sales, archived reports)
- Use before production deployment

## Setup Steps

### Step 1: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 2: Clean Default Data
```bash
python manage.py clean_default_data --confirm
```

**WARNING**: This will delete ALL data from the database including:
- All doctors
- All drugs
- All prescriptions
- All sales
- All archived reports

### Step 3: Create Superuser (if needed)
```bash
python manage.py createsuperuser
```

### Step 4: Update Settings for Production

Edit `config/settings.py`:

1. **Change SECRET_KEY**:
   ```python
   SECRET_KEY = 'your-production-secret-key-here'
   ```

2. **Set DEBUG to False**:
   ```python
   DEBUG = False
   ```

3. **Set ALLOWED_HOSTS**:
   ```python
   ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
   ```

4. **Update Session Cookie Settings**:
   ```python
   SESSION_COOKIE_SECURE = True  # Requires HTTPS
   CSRF_COOKIE_SECURE = True     # Requires HTTPS
   ```

5. **Configure Database** (if using PostgreSQL/MySQL):
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'your_db_name',
           'USER': 'your_db_user',
           'PASSWORD': 'your_db_password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

6. **Configure Static Files** (for production):
   ```python
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   ```

   Then run:
   ```bash
   python manage.py collectstatic
   ```

## Registration Flow

1. User visits `/subscription/plans/`
2. Selects a plan and clicks "Başla"
3. Fills registration form at `/subscription/register/`
4. After registration, redirected to `/subscription/contract/`
5. User must read and agree to contract
6. After agreement, redirected to `/admin/` (Django admin panel)

## Contract Agreement

- Contract text is stored in `ContractAgreement.contract_text`
- Default contract text is in `subscription/views.py` → `get_default_contract_text()`
- You can customize the contract text in the admin panel
- Each agreement is tracked with:
  - User who agreed
  - Company
  - IP address
  - Timestamp
  - Contract version

## Middleware Protection

The `TenantMiddleware` now checks for contract agreement on all protected pages except:
- `/subscription/contract/`
- `/subscription/plans/`
- `/subscription/register/`
- `/admin/`
- `/master-admin/`

## Decorators

- `@contract_required` - Requires contract agreement
- `@subscription_required` - Requires active subscription
- Both can be used together on views

## Admin Panel

All models are registered in Django admin:
- Company
- SubscriptionPlan
- Subscription
- UserProfile
- ContractAgreement (NEW)

## Notes

- The system is now ready for production use
- All default data should be cleaned before going live
- Make sure to update SECRET_KEY and DEBUG settings
- Configure proper database for production
- Set up HTTPS for secure cookie settings
- Configure static file serving (nginx, Apache, or cloud storage)

