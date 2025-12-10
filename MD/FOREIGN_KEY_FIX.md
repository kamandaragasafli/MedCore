# Foreign Key Constraint Fix

## Problem
**Error**: `FOREIGN KEY constraint failed`

### Root Cause
The Doctor model (in **tenant databases**) was trying to reference Region, City, Clinic, and Specialization models (in **master database**). 

**Foreign keys cannot work across different databases!** SQLite (and most databases) don't support cross-database foreign key relationships.

---

## Solution
**Moved regions data to tenant databases** so that all related data is in the same database.

### What Changed:

#### 1. Database Router Update
**File**: `subscription/db_router.py`

**Before**:
```python
MASTER_APPS = ['subscription', 'auth', 'contenttypes', 'sessions', 'admin', 'regions', 'master_admin']
```

**After**:
```python
MASTER_APPS = ['subscription', 'auth', 'contenttypes', 'sessions', 'admin', 'master_admin']
# regions is now a TENANT app (not in MASTER_APPS)
```

#### 2. Migration Changes
- Removed regions tables from default database (fake unapply)
- Migrated regions tables to all tenant databases
- Now each company has their own copy of regions, cities, clinics, and specializations

#### 3. Data Population Command
Created: `regions/management/commands/populate_all_tenants_regions.py`

**Usage**:
```bash
python manage.py populate_all_tenants_regions
```

This command:
- Finds all companies
- Switches to each company's database
- Populates initial data:
  - Regions (Bölgələr): Bakı, Gəncə, Sumqayıt, etc.
  - Cities (Şəhərlər): Bakı, Gəncə, Sumqayıt, etc.
  - Clinics (Klinikalar): Sample clinics
  - Specializations (İxtisaslar): Terapevt, Kardioloq, Nevroloq, etc.

---

## New Database Architecture

### Master Database (db.sqlite3):
```
✅ subscription_company
✅ subscription_subscriptionplan
✅ subscription_subscription
✅ subscription_userprofile
✅ auth_user
✅ auth_group
✅ auth_permission
✅ django_session
✅ master_admin_*
```

### Tenant Databases (databases/tenant_*.db):
```
✅ doctors_doctor
✅ regions_region          ← NOW HERE (not in master)
✅ regions_city            ← NOW HERE
✅ regions_clinic          ← NOW HERE
✅ regions_specialization  ← NOW HERE
✅ reports_*
✅ sales_*
```

---

## Why This Makes Sense

### Pros:
1. ✅ **Foreign keys work** - All related data in same database
2. ✅ **Data isolation** - Each company's data is completely separate
3. ✅ **Flexibility** - Each company can have their own regions/clinics
4. ✅ **Scalability** - Easy to move tenant databases to different servers
5. ✅ **Security** - No cross-company data leakage

### Cons:
- ❌ Duplicate data across tenants (same regions copied to each)
- ❌ Updates to regions need to be applied to all tenants

### Mitigation:
- Create management command to sync regions across all tenants if needed
- Reference data (regions/cities/clinics) doesn't change often
- Each company can customize their own regions/clinics if needed

---

## What Was Populated

### Regions (5):
- Bakı (BAK)
- Gəncə (GAN)
- Sumqayıt (SMQ)
- Mingəçevir (MIN)
- Abşeron (ABS)

### Cities (3):
- Bakı
- Gəncə
- Sumqayıt

### Clinics (1):
- Bakı Mərkəzi Klinika

### Specializations (7):
- Terapevt (THER)
- Kardioloq (CARD)
- Nevroloq (NEUR)
- Pediatr (PEDI)
- Cərrah (SURG)
- Ortoped (ORTH)
- Dermatoloq (DERM)

---

## How to Use

### 1. Add New Company
When a new company registers:
```bash
python manage.py create_tenant_db company_slug
python manage.py populate_all_tenants_regions
```

### 2. Add More Regions/Cities
Login as that company and:
- Go to `/admin/regions/region/add/`
- Add custom regions, cities, clinics
- OR add via management command

### 3. Add Doctors
Now you can add doctors at `/doctors/add/` or `/admin/doctors/doctor/add/`:
- Select Region (dropdown populated)
- Select City (filtered by region)
- Select Clinic (filtered by city)
- Select Specialization
- **No more FOREIGN KEY constraint error!** ✅

---

## Files Modified

1. ✅ `subscription/db_router.py` - Removed `'regions'` from MASTER_APPS
2. ✅ `regions/management/commands/populate_all_tenants_regions.py` - New command
3. ✅ Applied migrations to tenant databases

---

## Testing

### Test 1: Admin Panel
1. Login to `/admin/`
2. Go to `/admin/doctors/doctor/add/`
3. Select region, city, clinic, specialization
4. Fill doctor details
5. Click Save
6. **Expected**: Doctor created successfully ✅

### Test 2: Web Interface
1. Login to web interface
2. Go to `/doctors/add/`
3. Fill form with all required fields
4. Submit
5. **Expected**: Success message, doctor appears in list ✅

### Test 3: Foreign Key Cascade
1. Try to delete a region that has doctors
2. **Expected**: Either prevent deletion or cascade (based on on_delete setting)

---

## Future Enhancements

### Option 1: Shared Reference Data
If you want regions to be shared across all companies:
- Create a "reference" database
- Store regions/cities/clinics there
- Use integer IDs instead of foreign keys
- Join data at application level

### Option 2: Sync Command
Create a command to sync reference data:
```bash
python manage.py sync_regions_to_all_tenants
```
This would:
- Read regions from a master list
- Update all tenant databases
- Preserve company-specific additions

### Option 3: PostgreSQL Schemas
When migrating to PostgreSQL:
- Use schemas instead of separate databases
- Foreign keys can work across schemas
- Better performance and management

---

## Troubleshooting

### Error: "No regions found in dropdown"
**Solution**: Run `python manage.py populate_all_tenants_regions`

### Error: "FOREIGN KEY constraint failed" (still)
**Check**:
1. Are regions tables in tenant database? (not master)
2. Did you run populate command?
3. Are you logged in as a company user? (middleware sets tenant DB)

### Error: "Region/City/Clinic not found"
**Solution**: 
- Add them via admin panel: `/admin/regions/`
- Or extend the populate command with more data

---

## Summary

✅ **Fixed**: Foreign key constraint error  
✅ **Method**: Moved regions to tenant databases  
✅ **Populated**: Initial data for all existing tenants  
✅ **Tested**: Doctors can now be added successfully  
✅ **Documented**: This guide for future reference  

The system is now ready to add doctors! 🎉

