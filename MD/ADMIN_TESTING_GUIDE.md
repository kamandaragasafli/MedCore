# 🔐 Admin & Testing Guide - Session Management

## ✅ **PROBLEM SOLVED!**

**UPDATE:** This issue has been **completely resolved** with the **Dual Session System**!

You can now log in to:
- Django Admin (`/admin/`) → Uses `admin_sessionid` cookie
- Regular Site (`/`) → Uses `sessionid` cookie

**Both sessions work independently in the SAME browser!** 🎉

**See:** `QUICK_TEST_GUIDE.md` for 5-minute test, or `DUAL_SESSION_IMPLEMENTATION_GUIDE.md` for full technical details.

---

## ❗ **Original Problem (NOW FIXED)**

<details>
<summary>Click to see original issue description</summary>

Django used to use **one session per browser**. When you:
1. Log in as **superuser** in admin panel
2. Then log in as **test company user** on the main site
3. → The superuser session was replaced

This was **normal Django behavior**, but has now been fixed with custom middleware.

</details>

---

## ✅ **Current Solution (Dual Session System)**

The system now uses **separate session cookies** for admin and regular users:

```
Browser Cookies:
├─ admin_sessionid → Django Admin (/admin/)
└─ sessionid       → Company Dashboard (/)
```

**Benefits:**
- ✅ No more session conflicts
- ✅ Work on admin and dashboard simultaneously
- ✅ Single browser, dual sessions
- ✅ Secure and isolated

**Quick Test:**
1. Visit `/admin/` and login
2. Visit `/login/` and login as user
3. Check cookies (F12) - you'll see BOTH!
4. Switch between tabs - both work! 🎉

---

## ✅ **Alternative Solutions** (If Needed)

### **Solution 1: Use Different Browsers** ⭐ RECOMMENDED

The easiest and most reliable method:

| Browser | Purpose | Login |
|---------|---------|-------|
| **Chrome** | Admin Panel | Superuser |
| **Firefox** | Company Testing | Test Account |
| **Edge** | Additional Testing | Another Account |
| **Incognito Mode** | Quick Tests | Temporary Account |

#### **How to Use:**
```bash
# Chrome - Admin Panel
http://127.0.0.1:8000/admin/
Username: admin
Password: your_superuser_password

# Firefox - Company Dashboard  
http://127.0.0.1:8000/login/
Username: test_company
Password: test_password
```

✅ **Advantages:**
- No code changes needed
- Clear separation
- Can run simultaneously
- No session conflicts

---

### **Solution 2: Link Superuser to a Company**

Make your superuser also a company owner so you can access both admin and dashboard.

#### **Step 1: Run the Command**

```bash
python manage.py link_superuser_to_company
```

#### **Step 2: Follow the Prompts**

```
Found 1 superuser(s):
1. admin - Not linked to any company

Select superuser number: 1

Available companies:
1. SolveyMMC (admin@solveymmc.com)
2. Test Hospital (test@hospital.com)

Select company number: 1

[SUCCESS] Linked admin to SolveyMMC as Owner
```

#### **Step 3: Test**

Now your superuser can:
- ✅ Access `/admin/` (Django admin)
- ✅ Access `/` (Company dashboard)
- ✅ Manage company data
- ✅ See admin interface

#### **How It Works:**

The command creates a `UserProfile` that links your superuser to a company:

```python
UserProfile:
  user: admin (superuser)
  company: SolveyMMC
  role: owner
```

✅ **Advantages:**
- Single login for everything
- No browser switching
- Full admin + company access

❌ **Disadvantages:**
- Superuser is tied to one company
- Can't test multi-company scenarios easily

---

### **Solution 3: Automatic Superuser Handling** ⭐ NOW ENABLED

**I've updated the middleware** to automatically handle superusers!

#### **How It Works:**

When a superuser (without a company profile) accesses the dashboard:
1. Middleware detects they're a superuser
2. Automatically assigns them to the **first company** (temporarily)
3. They can access the dashboard
4. Admin panel URLs (`/admin/`) are excluded from company routing

#### **Code Update:**

```python
# subscription/middleware.py
if request.path.startswith('/admin/'):
    clear_tenant_db()
    return None  # Skip tenant logic for admin

# For superusers without profile, use first company
if request.user.is_superuser:
    first_company = Company.objects.first()
    request.company = first_company
    request.user_role = 'admin'
```

✅ **Advantages:**
- Automatic - no setup needed
- Admin panel always works
- Dashboard works for superusers
- Can switch companies easily

---

### **Solution 4: Create Separate Test Accounts**

Create dedicated test accounts for each company:

```bash
python manage.py shell
```

```python
from django.contrib.auth.models import User
from subscription.models import Company, UserProfile

# Get companies
company1 = Company.objects.get(name='SolveyMMC')
company2 = Company.objects.get(name='Test Hospital')

# Create test user for Company 1
user1 = User.objects.create_user(
    username='test_solvey',
    email='test@solvey.com',
    password='testpass123',
    first_name='Test',
    last_name='User'
)

UserProfile.objects.create(
    user=user1,
    company=company1,
    role='owner'
)

# Create test user for Company 2
user2 = User.objects.create_user(
    username='test_hospital',
    email='test@hospital.com',
    password='testpass123',
    first_name='Hospital',
    last_name='Admin'
)

UserProfile.objects.create(
    user=user2,
    company=company2,
    role='owner'
)
```

✅ **Advantages:**
- Clean separation
- Real multi-tenant testing
- No superuser conflicts

---

## 🔄 **Recommended Testing Workflow**

### **Option A: Browser Separation** (Best for Most Cases)

```
Chrome → Admin Panel (superuser)
  ├─ Manage users
  ├─ Check subscriptions
  ├─ View all companies
  └─ System administration

Firefox → Company A Dashboard
  ├─ Add doctors
  ├─ Manage patients
  ├─ View reports
  └─ Company-specific data

Edge → Company B Dashboard
  └─ Test multi-tenancy isolation
```

### **Option B: Linked Superuser** (Quick Testing)

```
Single Browser → Logged in as superuser
  ├─ /admin/ → Django admin interface
  ├─ / → Company dashboard
  ├─ /settings/ → Company settings
  └─ All features accessible
```

---

## 🎯 **Quick Commands Reference**

### **Link Superuser to Company:**
```bash
python manage.py link_superuser_to_company
```

### **Create Test User:**
```bash
python manage.py shell
# Then use code from Solution 4
```

### **Check Current User Profile:**
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
from subscription.models import UserProfile

user = User.objects.get(username='admin')
try:
    profile = UserProfile.objects.get(user=user)
    print(f"Company: {profile.company.name}")
    print(f"Role: {profile.role}")
except UserProfile.DoesNotExist:
    print("No company profile")
```

### **List All User Profiles:**
```bash
python manage.py shell
```
```python
from subscription.models import UserProfile

for profile in UserProfile.objects.all():
    print(f"{profile.user.username} → {profile.company.name} ({profile.role})")
```

---

## 📊 **Understanding Django Sessions**

### **Why This Happens:**

Django stores session data in:
- Database (default)
- Cache
- Files
- Cookies

Session ID is stored in browser cookie: `sessionid`

**One browser = One sessionid = One active user**

### **Session Flow:**

```
Browser Request
  ↓
Django checks sessionid cookie
  ↓
Looks up session in database
  ↓
Gets user_id from session
  ↓
Returns User object
  ↓
Middleware sets request.user
```

When you log in as a different user:
```
New login → New session → Old session deleted → Old user logged out
```

---

## 🔒 **Security Note**

This behavior is **intentional** and **secure**:
- Prevents session hijacking
- Ensures one user per browser
- Protects against cross-user data leaks

**Don't try to maintain multiple sessions in one browser** - it can cause:
- Session confusion
- Data leaks
- Security vulnerabilities

---

## ✅ **Summary**

### **For Daily Testing:**
Use **different browsers** for different roles.

### **For Quick Admin + Dashboard Access:**
Run `python manage.py link_superuser_to_company` once.

### **For Multi-Company Testing:**
Create separate test accounts for each company.

### **Current Setup:**
✅ Middleware now automatically handles superusers
✅ Admin panel URLs excluded from tenant routing
✅ Superusers can access dashboard without profile

---

## 🎉 **You're All Set!**

Your system now handles:
- ✅ Multiple companies with isolated data
- ✅ Superuser access to both admin and dashboard
- ✅ Clear session management
- ✅ Secure multi-tenancy

**Just remember:** One browser = One logged-in user at a time!

Use multiple browsers for simultaneous testing. 🚀

