# Prescription/Recipe Management Module

## ✅ Overview

A complete prescription/recipe registration system has been created, allowing healthcare providers to register prescriptions with doctor selection, multiple drug selection, and real-time tracking.

### 🔄 Latest Enhancements (Region-Based Workflow)
- Region must now be selected first; doctors are auto-filtered per region.
- Doctor dropdown loads asynchronously once a region is chosen.
- Each drug has its own quantity input (e.g., **Qəbələ – Abdullayev Hüseyn – Aspirin – 5**).
- Recent prescriptions panel now lists region/doctor/drug/quantity combinations exactly as requested.

## 📋 Features

### **1. Prescription Registration Form**
- Region selection (required) with dynamic doctor filtering
- Doctor selection list auto-populated per region
- Date selection with default to today
- Optional patient name
- Multiple drug quantity inputs (no more checkboxes)
- Drug search functionality
- Real-time counter of selected drugs
- Optional notes field

### **2. Recent Prescriptions Panel**
- Shows last 5 prescriptions
- Displays: Date, Doctor, Patient, Drug Count, Total Amount
- Real-time updates after new prescription

### **3. Data Models**

#### **Prescription Model**:
- Doctor (FK to Doctor)
- Date
- Patient Name (optional)
- Notes (optional)
- Status (Active/Inactive)
- Timestamps (Created/Updated)

#### **PrescriptionItem Model**:
- Prescription (FK to Prescription)
- Drug (FK to Drug)
- Quantity
- Unit Price (snapshot at prescription time)
- Dosage instructions (optional)
- Duration (optional)

## 🎨 Page Design

### Layout Structure

```
┌──────────────────────────────────────────────────────────┐
│ LEFT SIDE                    │ RIGHT SIDE                │
│ (Form)                       │ (Recent Prescriptions)    │
├──────────────────────────────┼──────────────────────────┤
│ 📋 Qeydiyyat Əlavə Et      │ Ən Son Qeydiyyatlar (Son 5)│
│ ──────────────────────────  │ ──────────────────────────│
│ İlkin                        │ ┌────┬──────┬──────┬────┐│
│ Qabala                       │ │ №  │Tarix │Həkim │Dərm││
│                              │ ├────┼──────┼──────┼────┤│
│ Həkim adı: [Dropdown]        │ │ 1  │24 Nov│Dr.A  │ 3  ││
│ Tarix: [Date Picker]         │ │ 2  │23 Nov│Dr.B  │ 5  ││
│ Xəstə Adı: [Input]           │ │ 3  │22 Nov│Dr.C  │ 2  ││
│                              │ └────┴──────┴──────┴────┘│
│ Dərmanlar                    │                          │
│ ┌──────────────────────────┐ │                          │
│ │ 🔍 Dərman axtar...       │ │                          │
│ ├──────────────────────────┤ │                          │
│ │ □ Paracetamol    5.50₼  │ │                          │
│ │ ☑ İbuprofen      8.00₼  │ │                          │
│ │ □ Amoksisilin   12.00₼  │ │                          │
│ │ ☑ Vitamin C     18.00₼  │ │                          │
│ │ ...                      │ │                          │
│ └──────────────────────────┘ │                          │
│                              │                          │
│ Qeyd: [Textarea]             │                          │
│                              │                          │
│ [Yadda Saxla] [Sil]    [2]   │                          │
└──────────────────────────────┴──────────────────────────┘
```

### Color Scheme

**Form Design**:
- Header: Dark gradient (`#1e293b` to `#334155`)
- Form background: Surface color
- Section labels: Uppercase, gray, small text
- Selected drugs: Highlighted with primary color

**Buttons**:
- Save: Blue gradient (`#3b82f6` to `#2563eb`)
- Delete: Red gradient (`#ef4444` to `#dc2626`)
- Counter: Primary color with border

**Recent Panel**:
- Drug count badge: Green gradient
- Amount: Primary color, bold
- Hover: Subtle background change

## 🔧 Features Breakdown

### 1. **Doctor Selection** 👨‍⚕️
- Dropdown showing all active doctors
- Format: "Doctor Name - Code"
- Required field
- Validation on submit

### 2. **Date Selection** 📅
- Date input field
- Defaults to current date
- Required field
- Can select past or future dates

### 3. **Patient Name** 👤
- Optional text field
- For recording patient information
- Can be left blank

### 4. **Drug Selection** 💊

**Features**:
- ✅ **Search**: Real-time filtering of drugs
- ✅ **Checkboxes**: Select multiple drugs
- ✅ **Price Display**: Shows final price for each drug
- ✅ **Visual Feedback**: Selected drugs highlighted
- ✅ **Counter**: Shows count of selected drugs (bottom right)
- ✅ **Scrollable List**: All drugs accessible

**Search Functionality**:
```javascript
Type "para" → Shows: Paracetamol
Type "vitamin" → Shows: Vitamin C
```

### 5. **Notes** 📝
- Optional textarea
- For additional prescription notes
- Multi-line support

### 6. **Form Actions** ⚡

**Yadda Saxla** (Save):
- Blue button with save icon
- Validates form before submit
- Checks for at least one drug selected
- Shows success/error message

**Sil** (Delete/Reset):
- Red button with trash icon
- Clears entire form
- Confirmation dialog
- Resets drug selection counter

**Counter**:
- Shows number of selected drugs
- Updates in real-time
- Primary color styling

### 7. **Recent Prescriptions** 📊

**Table Columns**:
- **№**: Row number (1-5)
- **Tarix**: Prescription date (formatted: "24 Nov 2025")
- **Həkim**: Doctor name (truncated)
- **Xəstə**: Patient name (or "-" if empty)
- **Dərman**: Drug count badge (green)
- **Məbləğ**: Total amount in AZN

**Features**:
- Sticky header (stays visible when scrolling)
- Hover effects on rows
- Empty state message
- Auto-updates after new prescription

## 💻 Technical Implementation

### Files Created

**1. prescriptions/models.py**
- `Prescription` model
- `PrescriptionItem` model
- Calculated properties: `total_amount`, `drug_count`

**2. prescriptions/views.py**
- `add_prescription` - Add new prescription (GET/POST)
- `prescription_list` - List all prescriptions

**3. prescriptions/urls.py**
- `/prescriptions/` - List page
- `/prescriptions/add/` - Add page

**4. prescriptions/admin.py**
- Admin configuration
- Inline drug items
- List display with filters

**5. prescriptions/templates/prescriptions/add.html**
- Complete add prescription page
- 800+ lines (HTML + CSS + JS)
- Responsive design
- Interactive features

### Database Schema

**Prescription Table**:
```sql
CREATE TABLE prescriptions_prescription (
    id INTEGER PRIMARY KEY,
    doctor_id INTEGER NOT NULL,
    date DATE NOT NULL,
    patient_name VARCHAR(200),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES doctors_doctor(id)
);
```

**PrescriptionItem Table**:
```sql
CREATE TABLE prescriptions_prescriptionitem (
    id INTEGER PRIMARY KEY,
    prescription_id INTEGER NOT NULL,
    drug_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,
    unit_price DECIMAL(10,2) NOT NULL,
    dosage VARCHAR(200),
    duration VARCHAR(100),
    FOREIGN KEY (prescription_id) REFERENCES prescriptions_prescription(id),
    FOREIGN KEY (drug_id) REFERENCES drugs_drug(id)
);
```

### Multi-Tenancy Support
- ✅ Tenant-specific prescriptions
- ✅ Each company has their own prescriptions
- ✅ Data isolation per tenant
- ✅ Works with existing doctor and drug data

## 🎯 Usage Instructions

### Access Add Prescription Page

**URL**:
```
http://127.0.0.1:8000/prescriptions/add/
```

### Create New Prescription

**Step 1**: Select Doctor
- Click doctor dropdown
- Choose from active doctors

**Step 2**: Select/Confirm Date
- Date defaults to today
- Change if needed

**Step 3**: Enter Patient Name (Optional)
- Type patient's name
- Can be left blank

**Step 4**: Search & Select Drugs
- Use search box to filter drugs
- Check boxes for desired drugs
- Watch counter update

**Step 5**: Add Notes (Optional)
- Enter any additional notes

**Step 6**: Save
- Click "Yadda Saxla" button
- See success message
- Check recent prescriptions panel

### Reset Form

**Option 1**: Click "Sil" button
- Confirmation dialog appears
- Clears all fields
- Unselects all drugs

**Option 2**: Refresh page
- Loses unsaved data

## 📊 Example Usage

### Example 1: Simple Prescription

```
Həkim: Dr. Əhməd - A001
Tarix: 24.11.2025
Xəstə: Murad Əliyev
Dərmanlar: 
  ☑ Paracetamol (5.50₼)
  ☑ Vitamin C (18.00₼)
Qeyd: Gündə 2 dəfə

Result: Prescription with 2 drugs, total: 23.50₼
```

### Example 2: Multiple Drugs

```
Həkim: Dr. Leyla - L002
Tarix: 24.11.2025
Dərmanlar: 
  ☑ İbuprofen (8.00₼)
  ☑ Amoksisilin (12.00₼)
  ☑ Vitamin C (18.00₼)
  ☑ Aspirin (6.00₼)
  ☑ Nurofen (22.00₼)

Result: Prescription with 5 drugs, total: 66.00₼
```

## 🎨 JavaScript Features

### 1. **Drug Search**
```javascript
// Real-time filtering
Type in search box → Instantly filters drug list
Case-insensitive
Shows/hides matching drugs
```

### 2. **Selected Counter**
```javascript
// Updates automatically
Check drug → Counter increases
Uncheck drug → Counter decreases
Shows current selection count
```

### 3. **Form Validation**
```javascript
// On submit
- Check doctor selected
- Check date entered
- Check at least 1 drug selected
- Show alert if validation fails
```

### 4. **Reset Confirmation**
```javascript
// Click Sil button
- Show confirmation dialog
- If confirmed: Reset form
- If cancelled: Keep data
```

### 5. **Auto-scroll to Messages**
```javascript
// After form submit
- If messages exist
- Scroll to top smoothly
- User sees success/error message
```

## 📱 Responsive Design

### Desktop (> 1200px)
- 2-column layout (form + recent)
- Full-height sections
- All features visible
- Spacious layout

### Tablet (768px - 1200px)
- Single column layout
- Form stacks above recent
- Reduced heights
- Maintained functionality

### Mobile (< 768px)
- Single column
- Smaller padding
- Stacked buttons
- Compact table
- Smaller fonts
- Touch-friendly

## ✨ User Experience Features

### Visual Feedback
- ✅ **Hover Effects**: On buttons, rows, drug items
- ✅ **Selected State**: Highlighted drugs
- ✅ **Counter Badge**: Real-time updates
- ✅ **Color Coding**: Drug count (green), amount (primary)

### Accessibility
- ✅ **Clear Labels**: All form fields labeled
- ✅ **Required Indicators**: * on required fields
- ✅ **Placeholders**: Helpful hints in inputs
- ✅ **Error Messages**: Clear validation messages

### Performance
- ✅ **Fast Search**: Instant filtering
- ✅ **Efficient Queries**: Prefetch related data
- ✅ **Minimal Loading**: Quick page render

## 🚀 Future Enhancements

### Planned Features

1. **Dosage Management**
   - Add dosage field per drug
   - Duration field per drug
   - Instructions per drug

2. **Quantity Control**
   - Select quantity for each drug
   - Calculate total based on quantity
   - Update prices dynamically

3. **Prescription Templates**
   - Save common prescription sets
   - Quick select from templates
   - Edit and save new templates

4. **Print Functionality**
   - Print prescription
   - Professional layout
   - QR code for verification

5. **Edit Prescriptions**
   - Edit existing prescriptions
   - Add/remove drugs
   - Update patient info

6. **Delete Prescriptions**
   - Soft delete (mark inactive)
   - Confirmation dialog
   - Restore functionality

7. **Prescription History**
   - View all prescriptions
   - Filter by doctor/date/patient
   - Search functionality
   - Export to Excel

8. **Statistics**
   - Most prescribed drugs
   - Doctor activity
   - Revenue by period
   - Charts and graphs

9. **Patient Management**
   - Link to patient records
   - Patient history
   - Recurring prescriptions

10. **Notifications**
    - Email prescription to patient
    - SMS notifications
    - Print reminders

## ✅ Testing Checklist

- [x] Create prescription with all fields
- [x] Create prescription with minimal fields
- [x] Select multiple drugs
- [x] Search drugs
- [x] Selected counter updates
- [x] Form validation works
- [x] Reset form works
- [x] Recent prescriptions display
- [x] Responsive on mobile
- [x] Multi-tenant isolation
- [ ] Edit prescription (future)
- [ ] Delete prescription (future)
- [ ] Print prescription (future)

## 📁 Files Summary

**Created**:
- `prescriptions/__init__.py`
- `prescriptions/apps.py`
- `prescriptions/models.py` (2 models)
- `prescriptions/views.py` (2 views)
- `prescriptions/urls.py`
- `prescriptions/admin.py`
- `prescriptions/templates/prescriptions/add.html` (800+ lines)
- `prescriptions/migrations/0001_initial.py`

**Modified**:
- `config/settings.py` - Added 'prescriptions' to INSTALLED_APPS
- `config/urls.py` - Added prescriptions URL pattern

**Documentation**:
- `PRESCRIPTION_MODULE.md` - Complete documentation

## 🎁 Benefits

### For Healthcare Providers
- ✅ **Fast Registration**: Quick prescription entry
- ✅ **Multi-drug Support**: Select multiple drugs easily
- ✅ **Search Feature**: Find drugs quickly
- ✅ **Recent View**: See last 5 prescriptions
- ✅ **Professional**: Clean, modern interface

### For Business
- ✅ **Revenue Tracking**: Total amount per prescription
- ✅ **Activity Monitor**: Recent prescriptions panel
- ✅ **Doctor Tracking**: Linked to doctors
- ✅ **Drug Tracking**: Linked to drugs
- ✅ **Audit Trail**: Timestamps on all records

### For Development
- ✅ **Reusable Pattern**: Similar to other modules
- ✅ **Maintainable**: Clean code structure
- ✅ **Extensible**: Easy to add features
- ✅ **Documented**: Well-commented

## 🎯 Summary

The prescription/recipe management system provides a comprehensive solution for registering prescriptions with:

**Key Features**:
- 📋 Easy doctor selection
- 💊 Multiple drug selection with search
- 🔢 Real-time counter
- 📊 Recent prescriptions panel
- ✅ Form validation
- 🎨 Beautiful, professional design
- 📱 Fully responsive
- 🔒 Multi-tenant secure

**Access Now**:
```
http://127.0.0.1:8000/prescriptions/add/
```

The system is ready for production use and seamlessly integrates with the existing doctor and drug management modules! 💊✨

