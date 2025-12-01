# 🚀 Quick Start Guide - MedAdmin Dashboard

## 📋 **Step-by-Step Setup:**

### **1. Create Superuser (Admin Account)**
Open terminal and run:
```bash
python manage.py createsuperuser
```

**Enter these details:**
- Username: `admin`
- Email address: `admin@medadmin.com`
- Password: `admin123` (or your choice)
- Password (again): `admin123`

### **2. Run the Development Server**
```bash
python manage.py runserver
```

### **3. Access the Login Page**
Open your browser and go to:
```
http://localhost:8000/login/
```

### **4. Login**
- Username: `admin`
- Password: `admin123` (or what you set)
- Click "Sign In"

### **5. Explore the Dashboard**
You'll be redirected to the beautiful dashboard!

---

## 🎯 **Available URLs:**

| Page | URL | Description |
|------|-----|-------------|
| Login | `/login/` | Login page |
| Dashboard | `/` | Main dashboard (protected) |
| Doctors | `/doctors/` | Doctor list (protected) |
| Add Doctor | `/doctors/add/` | Add new doctor (protected) |
| Profile | `/profile/` | User profile (protected) |
| Logout | `/logout/` | Logout |

---

## 👥 **Create Test Users (Optional)**

Run Python shell:
```bash
python manage.py shell
```

Then paste this:
```python
from django.contrib.auth.models import User

# Doctor 1
User.objects.create_user(
    username='doctor1',
    email='doctor1@medadmin.com',
    password='test1234',
    first_name='John',
    last_name='Doe'
)

# Doctor 2
User.objects.create_user(
    username='doctor2',
    email='doctor2@medadmin.com',
    password='test1234',
    first_name='Sarah',
    last_name='Smith'
)

print("Test users created!")
exit()
```

---

## 🎨 **Features You Can Use:**

### **Dashboard:**
- ✅ Real-time statistics with animated charts
- ✅ Interactive Chart.js visualizations
- ✅ Sparkline graphs
- ✅ Count animations
- ✅ Theme switcher (5 themes)
- ✅ Dark mode support

### **Sidebar Menu:**
- ✅ Doctors management
- ✅ Payments tracking
- ✅ Sales reports
- ✅ Data management
- ✅ Drugs inventory
- ✅ Registrations
- ✅ Regional insights

### **User Features:**
- ✅ AI Chatbot assistant
- ✅ User profile dropdown
- ✅ Notifications (badge counts)
- ✅ Count buttons with live updates
- ✅ Search functionality
- ✅ Settings & help

### **Responsive Design:**
- ✅ Desktop optimized
- ✅ Tablet friendly
- ✅ Mobile responsive
- ✅ Touch-optimized buttons

---

## 🎭 **Try These:**

### **Change Theme:**
1. Click the palette icon (bottom right)
2. Choose from 5 themes:
   - Light Mode (default)
   - Dark Mode
   - Ocean Blue
   - Purple Dream
   - Nature Green
3. Click "Yadda Saxla" to save

### **Open Chatbot:**
1. Click the message icon (top right)
2. Type a message
3. Get AI responses
4. Use quick action buttons

### **View Doctors:**
1. Click "Həkimlər" in sidebar
2. See doctor list
3. Click "Yeni Həkim" to add

### **User Menu:**
1. Click your avatar (top right)
2. See dropdown with:
   - My Profile
   - Settings
   - Notifications
   - Help & Support
   - Logout

---

## 🔧 **Troubleshooting:**

### **Can't login?**
Make sure you created a superuser:
```bash
python manage.py createsuperuser
```

### **Static files not loading?**
```bash
python manage.py collectstatic --noinput
```

### **Database errors?**
```bash
python manage.py migrate
```

### **Charts not showing?**
Check if Chart.js is loaded in browser console (F12)

### **Page redirects to login constantly?**
Make sure you're logged in with valid credentials

---

## 📊 **Dashboard Features:**

### **Statistics Cards:**
- Total Appointments: 7,365 (+25%)
- Total Patients: 5,656 (+15%)
- Total Vacancy: 636 (-5%)
- Total Doctors: 575 (+3%)

### **Interactive Charts:**
- Patient Visited (line chart with Monthly/Weekly/Today)
- Patient Bar Chart (Last 7/30 days)
- Real-time sparklines
- Animated transitions

### **Data Tables:**
- Appointments table
- Top patient visits by region
- World map visualization

---

## 🌟 **Pro Tips:**

1. **Use keyboard shortcuts:**
   - `Ctrl + K` to focus search
   - `Esc` to close modals

2. **Mobile sidebar:**
   - Click hamburger menu to open
   - Click outside to close

3. **Count buttons:**
   - Update every 10 seconds
   - Show real-time changes

4. **Theme persistence:**
   - Saved in localStorage
   - Persists across sessions

5. **Responsive tables:**
   - Scroll horizontally on mobile
   - Hide non-essential columns

---

## 📞 **Need Help?**

- Check `LOGIN_SETUP_GUIDE.md` for login details
- Check `FIXED_ISSUES.md` for common problems
- Check `URL_PATTERNS_REFERENCE.md` for URL structure

---

## ✅ **Quick Checklist:**

Before using the system:
- [ ] Created superuser
- [ ] Server is running
- [ ] Accessed `/login/` page
- [ ] Successfully logged in
- [ ] Dashboard loads correctly
- [ ] Sidebar menu works
- [ ] Charts are displaying
- [ ] Theme switcher works
- [ ] Chatbot opens
- [ ] User dropdown works

---

**Everything is ready! Start using your MedAdmin Dashboard! 🎉**

Login at: `http://localhost:8000/login/`

