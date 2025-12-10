from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    # Authentication
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboard & Pages
    path('', views.dashboard, name='dashboard'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('api/notifications/count/', views.get_notification_count, name='notification_count'),
    path('profile/', views.profile, name='profile'),
    path('settings/', views.settings, name='settings'),
    path('help/', views.help_support, name='help'),
]

