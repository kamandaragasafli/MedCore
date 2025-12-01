# 🧪 Quick Test Guide - Dual Session System

## ✅ Simple 5-Minute Test

Follow these steps to verify your dual session system is working:

---

### **Step 1: Open Your Browser** 🌐

Open **Chrome** or **Firefox** and visit:
```
http://127.0.0.1:8000/admin/
```

---

### **Step 2: Login to Django Admin** 🔐

Use your superuser credentials:
```
Username: admin
Password: [your password]
```

✅ You should now see the Django admin interface.

---

### **Step 3: Check Admin Cookie** 🍪

1. Press **F12** to open Developer Tools
2. Click the **Application** tab (Chrome) or **Storage** tab (Firefox)
3. Expand **Cookies** → Click `http://127.0.0.1:8000`

You should see:
```
Name: admin_sessionid
Value: [long random string]
```

✅ **This is your admin session cookie!**

---

### **Step 4: Visit Regular Login** 🏠

**Without closing the admin tab**, in the **same browser**, open a new tab and visit:
```
http://127.0.0.1:8000/login/
```

---

### **Step 5: Login as Company User** 👤

Login with a regular company account:
```
Username: [company username]
Password: [company password]
```

✅ You should see the dashboard.

---

### **Step 6: Check BOTH Cookies** 🍪🍪

Press **F12** again and check cookies:

You should now see **TWO** cookies:
```
Name: admin_sessionid          ← Admin session
Value: [random string]

Name: sessionid                 ← User session  
Value: [different random string]
```

✅ **Both sessions are active!**

---

### **Step 7: Test Switching** 🔄

Now try switching between tabs:

**Tab 1:** Go to `http://127.0.0.1:8000/admin/`
- ✅ You should still be logged in as admin!

**Tab 2:** Go to `http://127.0.0.1:8000/`
- ✅ You should still be logged in as company user!

**Tab 1 again:** Visit `http://127.0.0.1:8000/admin/subscription/company/`
- ✅ Admin interface works!

**Tab 2 again:** Visit `http://127.0.0.1:8000/doctors/`
- ✅ Company dashboard works!

---

### **Step 8: Test Logout** 🚪

**In Tab 2 (Company User):** Click logout
- ✅ Company user logged out
- ✅ Cookie `sessionid` should be deleted

**In Tab 1 (Admin):** Refresh the page
- ✅ Admin still logged in!
- ✅ Cookie `admin_sessionid` still exists!

---

## 🎉 SUCCESS!

If all the above steps worked, your dual session system is **working perfectly**!

**What this means:**
- ✅ Admin and user sessions are completely separate
- ✅ Logging in/out as one doesn't affect the other
- ✅ You can work on both admin and user interface simultaneously
- ✅ No more session conflicts!

---

## 🐛 Troubleshooting

### **Problem: Only see one cookie**

**Solution:** Clear all cookies and try again:
1. F12 → Application → Cookies
2. Right-click on the domain → Clear
3. Start from Step 1

### **Problem: Admin shows company user**

**Solution:** Server needs to be restarted:
```powershell
# Stop the server (Ctrl+C in the terminal)
# Then start again:
python manage.py runserver
```

### **Problem: Getting logged out when switching**

**Solution:** Check if middleware is properly configured:

Open `config/settings.py` and verify:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'core.middleware.DualSessionMiddleware',  # ← This line
    'django.middleware.common.CommonMiddleware',
    # ...
]
```

---

## 📸 Expected Cookie Screenshot

When you open DevTools → Application → Cookies, you should see:

```
┌──────────────────┬────────────────────────┬───────┬───────────┐
│ Name             │ Value                  │ Path  │ Domain    │
├──────────────────┼────────────────────────┼───────┼───────────┤
│ admin_sessionid  │ xyz123abc...           │ /     │ localhost │
│ sessionid        │ def456uvw...           │ /     │ localhost │
│ csrftoken        │ ghi789rst...           │ /     │ localhost │
└──────────────────┴────────────────────────┴───────┴───────────┘
```

The important part: **TWO session cookies** with different names!

---

## 🎯 Quick Reference

| Action | URL | Cookie Used |
|--------|-----|-------------|
| Django Admin Login | `/admin/` | `admin_sessionid` |
| Company User Login | `/login/` | `sessionid` |
| View Doctors (User) | `/doctors/` | `sessionid` |
| Manage Doctors (Admin) | `/admin/doctors/doctor/` | `admin_sessionid` |
| Settings Page (User) | `/settings/` | `sessionid` |
| Subscription Admin | `/admin/subscription/` | `admin_sessionid` |

---

**For complete technical details, see:**
- `DUAL_SESSION_IMPLEMENTATION_GUIDE.md` (Full documentation)
- `core/middleware.py` (Implementation code)
- `config/settings.py` (Configuration)

---

**🎊 Enjoy your dual session system!**

