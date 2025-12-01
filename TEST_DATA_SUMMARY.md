# Test Data Population Summary

## ✅ Successfully Created Test Data

### 📊 Overview
- **Total Doctors Created**: 80 doctors
  - **Solvey Company**: 40 doctors
  - **Proto Company**: 40 doctors

### 🏥 Regional Clinics Added

Each company now has **7-8 clinics** across different regions:

#### Bakı Region (BAK)
1. **Bakı Mərkəzi Klinika** - Clinic
   - Address: Nəsimi rayonu, 28 May küç. 15
   - Phone: +994 12 555 0000

2. **Respublika Xəstəxanası** - Hospital
   - Address: Yasamal rayonu, Ə. Rəcəbli küç. 32
   - Phone: +994 12 555 1111

3. **Təbabət Mərkəzi №3** - Medical Center
   - Address: Nərimanov rayonu, S. Vəzirov küç. 10
   - Phone: +994 12 555 2222

#### Sumqayıt Region (SMQ)
4. **Sumqayıt Şəhər Poliklinikası** - Polyclinic
   - Address: Sumqayıt şəhəri, 17-ci mikrorayon
   - Phone: +994 18 555 3333

#### Gəncə Region (GAN)
5. **Gəncə Mərkəzi Xəstəxana** - Hospital
   - Address: Gəncə şəhəri, Nizami küç. 25
   - Phone: +994 22 555 4444

6. **Gəncə Diaqnostika Mərkəzi** - Medical Center
   - Address: Gəncə şəhəri, Heydər Əliyev prospekti 45
   - Phone: +994 22 555 5555

#### Abşeron Region (ABS)
7. **Abşeron Rayon Klinikası** - Clinic
   - Address: Abşeron rayonu, Xırdalan şəhəri
   - Phone: +994 12 555 6666

### 👨‍⚕️ Doctor Test Data Characteristics

Each of the 40 doctors per company has:

#### Basic Information
- **Name**: Realistic Azerbaijani names (e.g., Məmmədov Əli, Əzizova Aysel)
- **Code**: Auto-generated unique 6-character code (e.g., YWGTFY, Q2J9T6)
- **Gender**: Random (Male/Female)
- **Phone**: Random Azerbaijani phone number format (+994 XX XXX XX XX)
- **Email**: 70% have email addresses (random@example.com)

#### Location
- **Region**: Random from 5 regions (Bakı, Gəncə, Sumqayıt, Mingəçevir, Abşeron)
- **City**: Random city from selected region
- **Clinic**: Random clinic from selected region

#### Professional Data
- **Specialization**: Random from 10 specializations:
  - Terapevt
  - Kardioloq
  - Nevroloq
  - Pediatr
  - Cərrah
  - Ortoped
  - Dermatoloq
  - Endokrinoloq
  - Uşaq həkimi
  - Ginekoloq
  
- **Category**: Random (A, B, or C)
- **Degree**: Random (VIP, I, II, or III)

#### Financial Data
- **Previous Debt** (evvelki_borc): Random from -5,000 to 5,000 AZN
- **Calculated Amount** (hesablanmish_miqdar): Random from 0 to 10,000 AZN
- **Deleted Amount** (silinen_miqdar): Random from 0 to 5,000 AZN
- **Final Debt** (yekun_borc): Auto-calculated (Previous + Calculated - Deleted)

#### Other
- **Registration Date** (datasiya): Random date within last 2 years
- **Status**: 75% active, 25% inactive
- **Created Date**: Timestamp of creation

## 📋 Example Test Doctors

### Solvey Company Examples:
1. **Məmmədov Əli** (YWGTFY)
   - Terapevt, Category A, Degree VIP
   - Bakı Mərkəzi Klinika

2. **Əliyeva Günel** (A7K2P9)
   - Kardioloq, Category B, Degree I
   - Respublika Xəstəxanası

3. **Həsənov Vəli** (X5M7N2)
   - Cərrah, Category A, Degree VIP
   - Gəncə Mərkəzi Xəstəxana

### Proto Company Examples:
1. **Əzizova Şahnaz** (Q2J9T6)
   - Nevroloq, Category C, Degree II
   - Sumqayıt Şəhər Poliklinikası

2. **Hüseynov Elxan** (K8P3Q9)
   - Pediatr, Category A, Degree I
   - Təbabət Mərkəzi №3

## 🔍 How to View Test Data

### Via Admin Panel
1. Login as company admin (Solvey MMC or Proto MMC)
2. Go to: `http://127.0.0.1:8000/admin/doctors/doctor/`
3. You'll see 40+ doctors (40 test + any previously created)

### Via Web Interface
1. Login as company user
2. Go to: `http://127.0.0.1:8000/doctors/`
3. Browse the full list with filters and search

### Filter Options
- **By Region**: Bakı, Gəncə, Sumqayıt, Mingəçevir, Abşeron
- **By Clinic**: 7-8 different clinics per company
- **By Specialization**: 10 different specializations
- **By Category**: A, B, C
- **By Degree**: VIP, I, II, III
- **By Status**: Active/Inactive

## 📊 Database Statistics

### Solvey Company (tenant_solvey.sqlite3)
- **Doctors**: 41 (1 original + 40 test)
- **Regions**: 5
- **Cities**: 4
- **Clinics**: 8
- **Specializations**: 11

### Proto Company (tenant_proto.sqlite3)
- **Doctors**: 41 (1 original + 40 test)
- **Regions**: 5
- **Cities**: 3
- **Clinics**: 7
- **Specializations**: 10

## 🎯 Use Cases for Test Data

### 1. List Page Testing
- Test pagination (25 doctors per page)
- Test sorting by different fields
- Test filtering by region, clinic, specialization
- Test search functionality

### 2. Financial Reports
- Test debt calculations
- Test positive/negative balances
- Test total debt summaries
- Test financial analytics

### 3. Regional Distribution
- View doctors across different regions
- Analyze clinic distribution
- Test location-based filtering

### 4. Professional Analytics
- Specialization distribution
- Category breakdown (A/B/C)
- Degree distribution (VIP/I/II/III)

### 5. Data Isolation Testing
- Verify Solvey cannot see Proto's doctors
- Verify Proto cannot see Solvey's doctors
- Test multi-tenant security

## 🛠️ Management Commands

### Populate Test Doctors (Run Anytime)
```bash
python manage.py populate_test_doctors
```
Creates 40 test doctors per company with realistic data.

### Populate Regions & Clinics
```bash
python manage.py populate_all_tenants_regions
```
Adds initial regions, cities, clinics, and specializations to all tenant databases.

### Fix Duplicate Codes
```bash
python manage.py fix_doctor_codes
```
Fixes any doctors with duplicate or default codes.

### Update Company Owners to Staff
```bash
python manage.py update_company_owners_staff
```
Gives company owners access to admin panel.

## ⚠️ Important Notes

1. **Test Data Only**: These are test doctors for development/testing purposes
2. **Isolated Data**: Each company has their own separate 40 doctors
3. **Realistic Names**: Uses actual Azerbaijani names for realistic testing
4. **Random Data**: Financial and location data is randomly generated
5. **Can Re-run**: You can delete test data and re-run the command to generate fresh data

## 🗑️ Cleaning Test Data

If you want to remove all test doctors and start fresh:

```python
# In Django shell or create a management command
from doctors.models import Doctor
from subscription.db_router import set_tenant_db, clear_tenant_db

# For Solvey
set_tenant_db('tenant_solvey')
Doctor.objects.all().delete()
clear_tenant_db()

# For Proto
set_tenant_db('tenant_proto')
Doctor.objects.all().delete()
clear_tenant_db()
```

Then run `python manage.py populate_test_doctors` again.

## ✅ Success!

The system now has comprehensive test data for development and testing:
- ✅ 80 doctors across 2 companies
- ✅ 7-8 regional clinics per company
- ✅ Realistic Azerbaijani names and data
- ✅ Complete data isolation between companies
- ✅ Ready for UI/UX testing and feature development

