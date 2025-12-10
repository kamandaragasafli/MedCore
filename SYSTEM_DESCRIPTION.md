# MedAdmin - Professional Medical Management SaaS Platform

## System Overview

MedAdmin is a comprehensive, multi-tenant Software-as-a-Service (SaaS) platform designed specifically for medical clinics, hospitals, and healthcare organizations in Azerbaijan. The system provides a complete solution for managing doctors, prescriptions, medications, sales, financial reports, and patient data with advanced analytics and AI-powered assistance.

## Core Features

### 1. Multi-Tenant Architecture
- **Isolated Databases**: Each company/organization has its own separate database
- **Data Security**: Complete data isolation between different companies
- **Scalable Infrastructure**: Supports unlimited companies with independent data storage

### 2. Doctor Management
- **Doctor Profiles**: Complete doctor information including name, code, specialization, region, clinic, degree, category
- **Financial Tracking**: Track previous debt (evvelki_borc), calculated amounts (hesablanmish_miqdar), deleted amounts (silinen_miqdar), and final debt (yekun_borc)
- **Payment Management**: Record and track doctor payments
- **Export Functionality**: Export doctor lists to Excel with full formatting

### 3. Prescription Management
- **Prescription Recording**: Create and manage prescriptions with multiple drugs
- **Drug Quantities**: Track quantities for each drug per prescription
- **Date Tracking**: Record prescription dates for monthly reporting
- **Region-Based Organization**: Organize prescriptions by regions

### 4. Drug/Medication Management
- **Drug Database**: Comprehensive drug catalog with names, prices, and active/inactive status
- **Price Management**: Track drug prices and calculate totals
- **Inventory Tracking**: Monitor drug quantities across prescriptions

### 5. Sales Management
- **Sales Recording**: Record sales transactions
- **Revenue Tracking**: Calculate total sales revenue
- **Item-Level Details**: Track individual items in each sale

### 6. Monthly Reports & Analytics
- **Comprehensive Reports**: Monthly reports showing:
  - Doctor summaries with all financial data
  - Drug quantities per doctor
  - Calculated values and payments
  - Final debt calculations
  - Deleted amounts tracking
- **Excel Export**: Export reports to Excel with identical formatting to HTML view
- **Filtering Options**: Filter by region, date range, doctor name
- **Real-time Calculations**: Dynamic calculations based on current data

### 7. Archived Reports System
- **Month Closure**: Close and archive monthly reports
- **Data Snapshot**: Create immutable snapshots of monthly data
- **Historical View**: View archived reports exactly as they were when closed
- **Debt Transfer**: Automatically transfer final debt to previous debt for next month
- **Data Reset**: Reset monthly totals after closure

### 8. Subscription Plans
- **Basic Plan**: Essential features for small clinics
  - Basic dashboard
  - Doctor and prescription management
  - Basic reports
- **Professional Plan**: Advanced features for growing practices
  - Professional dashboard with charts
  - Sales management
  - Revenue tracking
  - Top doctors analytics
  - AI Chatbot access
- **Enterprise Plan**: Full-featured solution for large organizations
  - Enterprise dashboard with all analytics
  - Region distribution analytics
  - Monthly trend analysis
  - Advanced reporting
  - AI Chatbot access
  - Print functionality

### 9. AI Chatbot Integration (Professional & Enterprise Only)
- **n8n Integration**: Seamless integration with n8n workflows
- **AI-Powered Assistance**: Get help with system usage, reports, and data
- **Real-time Chat**: Modern chat interface with typing indicators
- **Suggested Questions**: Quick-start prompts for common queries
- **Webhook-Based**: Flexible integration with any AI service via n8n

### 10. Notification System
- **Company Notifications**: Master admin can send notifications to specific companies
- **Notification Templates**: Pre-made templates for common messages:
  - System maintenance warnings
  - Subscription expiry warnings (3 days, 1 day)
  - New features announcements
  - Security updates
  - Service restoration
  - Plan limit reached
- **Notification Types**: Info, warning, success, error, subscription
- **Action Links**: Include actionable links in notifications
- **Read/Unread Status**: Track notification status

### 11. Contract Agreement System
- **Terms Acceptance**: Users must agree to terms before accessing the system
- **Contract Tracking**: Track contract agreements per user
- **Version Control**: Support for contract versions

### 12. Master Admin Panel
- **Company Management**: Create, view, and manage all companies
- **User Management**: Manage users across all companies
- **Platform Analytics**: View platform-wide statistics
- **Notification Sending**: Send notifications to companies
- **Tenant Switching**: Switch between company databases for testing

## Technical Architecture

### Technology Stack
- **Backend**: Django 5.2.3 (Python)
- **Database**: SQLite (with multi-tenant support)
- **Frontend**: HTML, CSS, JavaScript
- **Charts**: Chart.js
- **Excel Export**: openpyxl
- **AI Integration**: n8n webhooks
- **Styling**: Custom CSS with modern design

### Key Technical Features
- **Multi-Tenant Middleware**: Automatic database routing based on company
- **Custom Decorators**: Access control for subscriptions, contracts, and features
- **Context Processors**: Global template context (notifications, subscription info)
- **Management Commands**: Administrative tasks (clean default data, create templates)
- **Safe Data Handling**: Robust error handling for invalid Decimal data

## Business Model

### Pricing Structure
- **Basic Plan**: 100₼/month
- **Professional Plan**: 150₼/month (Most Popular)
- **Enterprise Plan**: 200₼/month

### Features by Plan
| Feature | Basic | Professional | Enterprise |
|---------|-------|--------------|------------|
| Doctor Management | ✅ | ✅ | ✅ |
| Prescription Management | ✅ | ✅ | ✅ |
| Basic Reports | ✅ | ✅ | ✅ |
| Sales Management | ❌ | ✅ | ✅ |
| Advanced Analytics | ❌ | ✅ | ✅ |
| AI Chatbot | ❌ | ✅ | ✅ |
| Region Analytics | ❌ | ❌ | ✅ |
| Monthly Trends | ❌ | ❌ | ✅ |
| Print Reports | ❌ | ❌ | ✅ |

## Security & Compliance

- **User Authentication**: Django authentication system
- **Role-Based Access**: Different roles for users
- **Data Isolation**: Complete separation between companies
- **Contract Agreements**: Legal compliance tracking
- **Session Management**: Secure session handling

## Target Market

- **Primary**: Medical clinics and hospitals in Azerbaijan
- **Secondary**: Healthcare organizations needing prescription and doctor management
- **Tertiary**: Medical supply companies tracking sales and inventory

## Unique Selling Points

1. **Azerbaijani Language Support**: Fully localized for Azerbaijani market
2. **Medical-Specific Features**: Designed specifically for healthcare workflows
3. **Multi-Tenant SaaS**: Scalable solution for multiple organizations
4. **AI Integration**: Modern AI chatbot for user assistance
5. **Comprehensive Reporting**: Detailed financial and operational reports
6. **Excel Export**: Professional Excel reports matching HTML views
7. **Archive System**: Historical data preservation with month closure
8. **Plan-Based Features**: Flexible pricing with feature tiers

## System Workflow

1. **Registration**: Company registers and selects a plan
2. **Contract Agreement**: Users agree to terms and conditions
3. **Setup**: Add doctors, drugs, and initial data
4. **Daily Operations**: Record prescriptions, sales, and payments
5. **Monthly Reporting**: Generate and review monthly reports
6. **Month Closure**: Archive monthly data and reset for next month
7. **Analytics**: View dashboards and analytics based on plan level

## Integration Capabilities

- **n8n Webhooks**: AI chatbot integration
- **Excel Export**: Data export functionality
- **API Ready**: Django REST Framework included
- **Webhook Support**: External system integration via webhooks

## Future Enhancements (Potential)

- Mobile app support
- Advanced AI features
- Payment gateway integration
- Email notifications
- SMS notifications
- Advanced analytics and BI
- Multi-language support expansion

---

**System Status**: Production Ready
**Version**: 1.0
**Last Updated**: November 2025

