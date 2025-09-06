from django.urls import path
from . import views
from . import auth_views
from . import admin_views
from . import database_permission_views

app_name = 'logs'

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('statistics/', views.statistics, name='statistics'),
    path('log-files/', views.log_files, name='log_files'),
    path('abnormal-queries/', views.abnormal_queries, name='abnormal_queries'),
    path('generate-report/', views.generate_report, name='generate_report'),
    path('api/logs/', views.api_logs, name='api_logs'),
    
    # Authentication URLs
    path('auth/login/', auth_views.login_view, name='login'),
    path('auth/register/', auth_views.register_view, name='register'),
    path('auth/logout/', auth_views.logout_view, name='logout'),
    path('auth/profile/', auth_views.profile_view, name='profile'),
    path('auth/change-password/', auth_views.change_password_view, name='change_password'),
    path('auth/required/', auth_views.auth_required_view, name='auth_required'),
    
    # Admin URLs (using 'manage' prefix to avoid conflict with Django admin)
    path('manage/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('manage/users/', admin_views.admin_user_list, name='admin_user_list'),
    path('manage/users/create/', admin_views.admin_user_create, name='admin_user_create'),
    path('manage/users/<int:user_id>/', admin_views.admin_user_detail, name='admin_user_detail'),
    path('manage/users/<int:user_id>/edit/', admin_views.admin_user_edit, name='admin_user_edit'),
    path('manage/users/<int:user_id>/toggle-active/', admin_views.admin_user_toggle_active, name='admin_user_toggle_active'),
    path('manage/users/<int:user_id>/reset-password/', admin_views.admin_user_reset_password, name='admin_user_reset_password'),
    path('manage/users/<int:user_id>/delete/', admin_views.admin_user_delete, name='admin_user_delete'),
    path('manage/users/bulk-action/', admin_views.admin_user_bulk_action, name='admin_user_bulk_action'),
    path('manage/security-logs/', admin_views.admin_security_logs, name='admin_security_logs'),
    path('manage/generate-password/', admin_views.admin_generate_password, name='admin_generate_password'),
    
    # Database Permission URLs
    path('manage/database-permissions/', database_permission_views.admin_database_permissions, name='admin_database_permissions'),
    path('manage/database-permissions/create/', database_permission_views.admin_database_permission_create, name='admin_database_permission_create'),
    path('manage/database-permissions/<int:permission_id>/', database_permission_views.admin_database_permission_detail, name='admin_database_permission_detail'),
    path('manage/database-permissions/<int:permission_id>/edit/', database_permission_views.admin_database_permission_edit, name='admin_database_permission_edit'),
    path('manage/database-permissions/<int:permission_id>/toggle-active/', database_permission_views.admin_database_permission_toggle_active, name='admin_database_permission_toggle_active'),
    path('manage/database-permissions/<int:permission_id>/delete/', database_permission_views.admin_database_permission_delete, name='admin_database_permission_delete'),
    path('manage/database-permissions/bulk-action/', database_permission_views.admin_database_permission_bulk_action, name='admin_database_permission_bulk_action'),
    path('manage/database-permissions/bulk-create/', database_permission_views.admin_bulk_database_permission_create, name='admin_bulk_database_permission_create'),
    
    # User Database Permissions
    path('my-database-permissions/', database_permission_views.user_database_permissions, name='user_database_permissions'),
]
