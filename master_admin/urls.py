"""
Master Admin Panel URLs
"""

from django.urls import path
from . import views

app_name = 'master_admin'

urlpatterns = [
    path('', views.master_dashboard, name='dashboard'),
    path('companies/', views.company_list, name='company_list'),
    path('companies/<int:company_id>/', views.company_detail, name='company_detail'),
    path('companies/<int:company_id>/switch/', views.switch_to_company, name='switch_to_company'),
    path('exit-impersonation/', views.exit_impersonation, name='exit_impersonation'),
    path('analytics/', views.platform_analytics, name='analytics'),
    path('users/', views.user_management, name='user_management'),
    path('notifications/send/', views.send_notification, name='send_notification'),
    path('notifications/send/<int:company_id>/', views.send_notification, name='send_notification'),
]

