# Doctor Management System - Models Documentation

## Overview
This document describes the comprehensive doctor management system with related models for regions, cities, clinics, and specializations.

## Models

### 1. Doctor Model (`doctors/models.py`)

The main doctor model with all professional and financial information.

#### Fields:

**Basic Information:**
- `ad` (CharField): Doctor's full name
- `code` (CharField): Unique 6-character code (auto-generated if not provided)
- `telefon` (CharField): Phone number
- `email` (EmailField): Email address (optional)
- `gender` (CharField): Gender (male/female/other)

**Location & Organization:**
- `region` (ForeignKey → Region): Doctor's region
- `city` (ForeignKey → City): Doctor's city
- `clinic` (ForeignKey → Clinic): Doctor's clinic/hospital

**Professional Information:**
- `ixtisas` (ForeignKey → Specialization): Medical specialization
- `category` (CharField): Category (A, B, or C)
- `degree` (CharField): Degree level (VIP, I, II, or III)

**Financial Information:**
- `evvelki_borc` (DecimalField): Previous debt
- `hesablanmish_miqdar` (DecimalField): Calculated amount
- `silinen_miqdar` (DecimalField): Deleted/Removed amount
- `yekun_borc` (DecimalField): Final debt (auto-calculated)

**Dates & Status:**
- `datasiya` (DateField): Registration date
- `created_at` (DateTimeField): Creation timestamp
- `updated_at` (DateTimeField): Last update timestamp
- `is_active` (BooleanField): Active status

#### Auto-calculated Fields:

**Final Debt Calculation:**
```python
yekun_borc = evvelki_borc + hesablanmish_miqdar - silinen_miqdar
```

**Code Generation:**
- If not provided, a unique 6-character alphanumeric code is auto-generated
- Format: Uppercase letters + digits (e.g., "A3B5C7")

#### Properties:

- `full_address`: Returns complete address including clinic, city, and region
- `debt_status`: Returns debt status ("Borclu", "Artıq ödəniş", or "Borc yoxdur")

---

### 2. Region Model (`regions/models.py`)

Represents geographical regions.

#### Fields:
- `name` (CharField): Region name
- `code` (CharField): Unique region code
- `description` (TextField): Optional description
- `created_at` (DateTimeField): Creation timestamp
- `updated_at` (DateTimeField): Last update timestamp

#### Relationships:
- **One-to-Many** with City: A region can have multiple cities
- **One-to-Many** with Doctor: A region can have multiple doctors

---

### 3. City Model (`regions/models.py`)

Represents cities within regions.

#### Fields:
- `name` (CharField): City name
- `region` (ForeignKey → Region): Parent region
- `code` (CharField): Unique city code
- `population` (IntegerField): City population (optional)
- `created_at` (DateTimeField): Creation timestamp
- `updated_at` (DateTimeField): Last update timestamp

#### Relationships:
- **Many-to-One** with Region: Each city belongs to one region
- **One-to-Many** with Clinic: A city can have multiple clinics
- **One-to-Many** with Doctor: A city can have multiple doctors

---

### 4. Clinic Model (`regions/models.py`)

Represents hospitals, clinics, and medical centers.

#### Fields:
- `name` (CharField): Clinic name
- `code` (CharField): Unique clinic code
- `city` (ForeignKey → City): City where clinic is located
- `address` (TextField): Full address
- `phone` (CharField): Contact phone
- `email` (EmailField): Contact email
- `type` (CharField): Clinic type (hospital/clinic/polyclinic/medical_center)
- `is_active` (BooleanField): Active status
- `created_at` (DateTimeField): Creation timestamp
- `updated_at` (DateTimeField): Last update timestamp

#### Clinic Types:
- `hospital`: Xəstəxana
- `clinic`: Klinika
- `polyclinic`: Poliklinika
- `medical_center`: Tibb Mərkəzi

#### Relationships:
- **Many-to-One** with City: Each clinic belongs to one city
- **One-to-Many** with Doctor: A clinic can have multiple doctors

---

### 5. Specialization Model (`regions/models.py`)

Represents medical specializations.

#### Fields:
- `name` (CharField): Specialization name
- `code` (CharField): Unique specialization code
- `description` (TextField): Optional description
- `is_active` (BooleanField): Active status
- `created_at` (DateTimeField): Creation timestamp
- `updated_at` (DateTimeField): Last update timestamp

#### Relationships:
- **One-to-Many** with Doctor: A specialization can be assigned to multiple doctors

---

## Relationships Diagram

```
Region (Bölgə)
  ├── has many → City (Şəhər)
  │                ├── has many → Clinic (Klinika)
  │                │                └── has many → Doctor (Həkim)
  │                └── has many → Doctor
  └── has many → Doctor

Specialization (İxtisas)
  └── has many → Doctor
```

---

## Key Features

### 1. Unique Code System
- All doctors must have a unique 6-character code
- Auto-generated if not provided during creation
- Used for quick identification and references

### 2. Financial Tracking
- Tracks previous debts, calculated amounts, and deleted amounts
- Automatically calculates final debt on save
- Provides debt status property for easy checking

### 3. Hierarchical Location
- Region → City → Clinic → Doctor
- Allows for detailed geographical organization
- Useful for regional reporting and analysis

### 4. Professional Categorization
- Category system (A, B, C) for doctor classification
- Degree system (VIP, I, II, III) for ranking
- Specialization system for medical expertise

### 5. Multi-tenant Support
- All models respect tenant database isolation
- Migrations applied to both default and tenant databases
- Each company sees only their own data

---

## Admin Interface

All models are registered in Django admin with:
- List display of key fields
- Search functionality
- Filtering options
- Autocomplete for foreign keys
- Custom actions (for Doctor model)

### Doctor Admin Actions:
1. **Activate Doctors**: Bulk activate selected doctors
2. **Deactivate Doctors**: Bulk deactivate selected doctors
3. **Calculate Debts**: Recalculate debts for selected doctors

---

## Usage Examples

### Creating a Doctor:

```python
from doctors.models import Doctor
from regions.models import Region, City, Clinic, Specialization

# Method 1: With code
doctor = Doctor.objects.create(
    code='ABC123',
    ad='Dr. Əli Məmmədov',
    telefon='+994501234567',
    gender='male',
    category='A',
    degree='VIP'
)

# Method 2: Auto-generate code
doctor = Doctor.objects.create(
    ad='Dr. Leyla Həsənova',
    telefon='+994501234568',
    gender='female',
    category='B',
    degree='I'
)
# Code will be auto-generated (e.g., '7F2G9H')
```

### Querying Doctors:

```python
# Get all doctors in a specific region
doctors = Doctor.objects.filter(region__name='Bakı')

# Get doctors with debt
doctors_with_debt = Doctor.objects.filter(yekun_borc__gt=0)

# Get active doctors in a specific specialization
active_cardio_doctors = Doctor.objects.filter(
    is_active=True,
    ixtisas__name='Kardiologiya'
)

# Get doctors in a specific clinic
clinic_doctors = Doctor.objects.filter(clinic__code='CLN001')
```

---

## Migration Notes

- Initial migrations created for all models
- Doctor model updated with new fields
- All migrations applied to both default and tenant databases
- Existing doctors receive default code '000000' (should be updated)

---

## Next Steps

1. Update existing doctor records with unique codes
2. Create frontend forms for all models
3. Add API endpoints if needed
4. Implement reporting features based on regions/categories
5. Add data import/export functionality

---

## File Locations

- Doctor Model: `doctors/models.py`
- Region Models: `regions/models.py`
- Doctor Admin: `doctors/admin.py`
- Regions Admin: `regions/admin.py`
- Doctor Views: `doctors/views.py`
- Regions Views: `regions/views.py`
- URLs: `config/urls.py`, `doctors/urls.py`, `regions/urls.py`

