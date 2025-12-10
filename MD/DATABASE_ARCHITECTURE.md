# Database Architecture - Multi-Tenant SaaS

## Overview
This system uses a **multi-tenant architecture** with **separate databases per company**. Data is separated into two categories: **Master Data** and **Tenant Data**.

---

## Database Types

### 1. Default Database (Master Database)
**Location**: `db.sqlite3`

**Purpose**: Stores shared data that's common across all companies

**Models (Apps)**:
- ✅ `subscription` - Companies, subscription plans, user profiles
- ✅ `auth` - Django users and authentication
- ✅ `contenttypes` - Django content types
- ✅ `sessions` - User sessions
- ✅ `admin` - Django admin logs
- ✅ `regions` - **Shared reference data**:
  - Region (Bölgələr)
  - City (Şəhərlər)
  - Clinic (Klinikalar)
  - Specialization (İxtisaslar)
- ✅ `master_admin` - Master admin panel data

**Access**: 
- Superuser via `/admin/`
- Master admin via `/master-admin/`

---

### 2. Tenant Databases (Company Databases)
**Location**: `databases/tenant_<company_slug>.db`

**Purpose**: Store company-specific data that's completely isolated from other companies

**Models (Apps)**:
- ✅ `doctors` - Company's doctors
- ✅ `patients` - Company's patients (if exists)
- ✅ `appointments` - Company's appointments (if exists)
- ✅ `reports` - Company's reports
- ✅ `sales` - Company's sales data
- ✅ `payments` - Company's payment records (if exists)

**Access**:
- Company users via web interface (e.g., `/doctors/`)
- Each company only sees their own data

---

## Database Router Configuration

File: `subscription/db_router.py`

```python
MASTER_APPS = [
    'subscription',
    'auth', 
    'contenttypes',
    'sessions',
    'admin',
    'regions',      # ← Shared reference data
    'master_admin'  # ← Master admin panel
]
```

### How It Works:

1. **Read/Write Operations**:
   - If model is in `MASTER_APPS` → Use **default database**
   - Otherwise → Use **tenant database** (set by middleware)

2. **Migrations**:
   - Master apps → Only migrate to **default database**
   - Tenant apps → Only migrate to **tenant databases**

3. **Relations**:
   - Master ↔ Master: ✅ Allowed
   - Tenant ↔ Tenant (same DB): ✅ Allowed
   - Master ↔ Tenant: ⚠️ Via Foreign Key (Doctor → Region, Doctor → City, etc.)

---

## Why This Architecture?

### Master Data (regions, cities, clinics, specializations):
- ✅ **Shared across all companies** - Everyone uses the same geographical and medical reference data
- ✅ **Centrally managed** - Admin updates once, all companies benefit
- ✅ **Consistent** - No duplicate or conflicting data
- ✅ **Efficient** - No need to copy reference data to each tenant

### Tenant Data (doctors, patients, appointments):
- ✅ **Complete isolation** - Company A cannot see Company B's data
- ✅ **Security** - Each company has a separate database file
- ✅ **Scalability** - Can move tenant databases to different servers
- ✅ **Data ownership** - Each company owns their data completely

---

## Data Flow Examples

### Example 1: Adding a Doctor

1. User logs in → Middleware sets tenant database
2. User visits `/doctors/add/`
3. Form shows:
   - **Regions** (from default database)
   - **Cities** (from default database, filtered by region)
   - **Clinics** (from default database)
   - **Specializations** (from default database)
4. User submits form
5. Doctor is saved to **tenant database** with references to master data

### Example 2: Accessing Admin Panel

1. Superuser logs in to `/admin/`
2. Can manage:
   - Companies and subscriptions
   - Regions, cities, clinics (shared data)
   - User accounts
3. **Cannot see doctors** (doctors are tenant-specific)
4. Doctors are managed through the web interface at `/doctors/`

### Example 3: Master Admin Impersonation

1. Superuser accesses `/master-admin/`
2. Clicks "Enter Company System" for Company X
3. Middleware switches to Company X's database
4. Superuser can now see Company X's doctors at `/doctors/`
5. Clicks "Exit Impersonation" to return to master admin

---

## Admin Panel Structure

### Django Admin (`/admin/`) - Superuser Only
**Can Manage**:
- ✅ Companies (Subscription app)
- ✅ Subscription Plans
- ✅ Users and Permissions
- ✅ Regions, Cities, Clinics (Master reference data)
- ✅ Specializations

**Cannot Manage**:
- ❌ Doctors (tenant-specific)
- ❌ Patients (tenant-specific)
- ❌ Appointments (tenant-specific)

### Master Admin Panel (`/master-admin/`) - Superuser Only
**Features**:
- View all companies
- Platform-wide analytics
- Impersonate any company
- Access company-specific data
- System monitoring

### Company Web Interface - Company Users
**Features**:
- Manage their own doctors at `/doctors/`
- Manage patients, appointments, etc.
- View reports and analytics
- Manage company settings

---

## Migration Commands

### Migrate Master Database:
```bash
python manage.py migrate
```
This migrates: subscription, auth, regions, master_admin, etc.

### Migrate Tenant Databases:
```bash
python manage.py migrate_tenants
```
This migrates: doctors, patients, appointments, reports, sales, etc.

### Create New Tenant Database:
```bash
python manage.py create_tenant_db <company_slug>
```

---

## Current Database Structure

### Default Database (db.sqlite3):
```
Tables:
- subscription_company
- subscription_subscriptionplan
- subscription_subscription
- subscription_userprofile
- auth_user
- auth_group
- auth_permission
- regions_region         ← Shared
- regions_city           ← Shared
- regions_clinic         ← Shared
- regions_specialization ← Shared
- master_admin_*
```

### Tenant Databases (databases/tenant_*.db):
```
Tables:
- doctors_doctor
- patients_patient (if exists)
- appointments_appointment (if exists)
- reports_*
- sales_*
```

---

## Key Points

1. **Regions, Cities, Clinics, Specializations** = Master Data (shared)
2. **Doctors, Patients, Appointments** = Tenant Data (isolated)
3. **Django Admin** = Only for master data management
4. **Company Interface** = For tenant-specific data management
5. **Master Admin** = For platform oversight and impersonation

---

## Troubleshooting

### Error: "no such table: regions_region"
**Cause**: Regions app not in MASTER_APPS  
**Fix**: Add `'regions'` to MASTER_APPS in db_router.py

### Error: "no such column: doctors_doctor.code"
**Cause**: Trying to access doctors from default database  
**Fix**: Don't register Doctor in Django admin (it's tenant-specific)

### Error: Doctor has no region/city/clinic data
**Cause**: Master data not populated  
**Fix**: Add regions, cities, clinics via `/admin/regions/`

---

## Best Practices

1. ✅ Always use middleware to set tenant context
2. ✅ Test with multiple tenant databases
3. ✅ Backup tenant databases separately
4. ✅ Populate master data before adding company data
5. ✅ Use Master Admin for cross-company viewing only
6. ✅ Keep tenant data completely isolated
7. ✅ Document which apps are master vs tenant

---

## Future Considerations

- PostgreSQL migration: Can use schemas instead of separate files
- Database sharding: Distribute tenant databases across multiple servers
- Read replicas: For better performance
- Automated backups: Per-tenant backup strategy
- Data export: Allow companies to export their data

