# Notification System Documentation

## Overview

The notification system allows master admins to send notifications to companies. Companies can view these notifications in their dashboard.

## Features

1. **Master Admin Panel**
   - Send notifications to single or multiple companies
   - Different notification types (info, warning, success, error, subscription)
   - Mark notifications as important
   - Add action links to notifications

2. **Company Dashboard**
   - View all notifications
   - Filter by read/unread/important
   - Mark notifications as read
   - Notification badge showing unread count
   - Notification menu item in sidebar

## Usage

### Sending Notifications from Master Admin

1. **From Company List Page:**
   - Click "Bildiriş Göndər" button in the header to send to multiple companies
   - Click "Bildiriş" button on a specific company card to send to that company only

2. **From Company Detail Page:**
   - Click "Bildiriş Göndər" button in the header

3. **Fill in the form:**
   - Select company/companies (checkboxes)
   - Enter title (required)
   - Enter message (required)
   - Select notification type (info, warning, success, error, subscription)
   - Mark as important (optional)
   - Add action URL (optional)
   - Add action text (optional)

4. **Click "Göndər" to send**

### Viewing Notifications (Company Side)

1. **Access Notifications:**
   - Click the bell icon in the top bar (shows unread count badge)
   - Or click "Bildirişlər" in the sidebar menu

2. **Filter Notifications:**
   - **Hamısı** - All notifications
   - **Oxunmamış** - Unread notifications (shows count)
   - **Oxunmuş** - Read notifications
   - **Vacib** - Important notifications

3. **Mark as Read:**
   - Click "Oxunmuş kimi işarələ" button on unread notifications
   - Or click the notification to view details

## Notification Types

- **info** (Məlumat) - General information (blue)
- **warning** (Xəbərdarlıq) - Warnings (orange)
- **success** (Uğur) - Success messages (green)
- **error** (Xəta) - Error messages (red)
- **subscription** (Abunəlik) - Subscription-related (purple)

## Example Use Cases

### Subscription Expiry Warning

**Title:** Abunəlik Bitməsi Haqqında Xəbərdarlıq

**Message:** 
```
Sizin abunəliyiniz 3 gün sonra bitəcək. 
Abunəliyinizi yeniləmək üçün zəhmət olmasa ödəniş edin.
```

**Type:** subscription

**Important:** Yes

**Action URL:** /subscription/plans/

**Action Text:** Abunəliyi Yenilə

### System Maintenance

**Title:** Sistem Təmir İşləri

**Message:**
```
Sistem təmir işləri 15 Yanvar 2025 tarixində saat 02:00-04:00 arası aparılacaq.
Bu müddət ərzində sistemə giriş mümkün olmayacaq.
```

**Type:** warning

**Important:** Yes

## Database Model

### Notification Model Fields

- `company` - ForeignKey to Company
- `title` - CharField (200 chars)
- `message` - TextField
- `notification_type` - CharField (choices: info, warning, success, error, subscription)
- `is_read` - BooleanField (default: False)
- `is_important` - BooleanField (default: False)
- `created_by` - ForeignKey to User (master admin who sent it)
- `created_at` - DateTimeField (auto)
- `read_at` - DateTimeField (nullable)
- `action_url` - URLField (optional)
- `action_text` - CharField (optional)

## API Endpoints

### Company Side

- `GET /notifications/` - View all notifications
- `GET /notifications/?filter=unread` - Filter notifications
- `GET /notifications/?mark_read=<id>` - Mark notification as read
- `GET /api/notifications/count/` - Get unread count (AJAX)

### Master Admin Side

- `GET /master-admin/notifications/send/` - Show send notification form
- `GET /master-admin/notifications/send/<company_id>/` - Show form with company pre-selected
- `POST /master-admin/notifications/send/` - Send notification(s)

## UI Components

### Notification Badge

- Shows unread count in top bar bell icon
- Shows unread count in sidebar menu item
- Red badge with white text

### Notification Card

- Unread notifications have blue left border
- Important notifications have red left border
- Shows notification type badge
- Shows timestamp
- Shows action button if action_url is provided

## Future Enhancements

Possible future improvements:

1. **Automatic Notifications:**
   - Subscription expiry warnings (3 days, 1 day before)
   - Payment reminders
   - System updates

2. **Email Notifications:**
   - Send email when important notification is created
   - Daily/weekly digest of notifications

3. **Notification Preferences:**
   - Company-level notification settings
   - User-level notification preferences

4. **Notification Templates:**
   - Pre-defined notification templates
   - Quick send buttons for common notifications

