from django.urls import path
from . import views

app_name = 'logs'

urlpatterns = [
    path('', views.index, name='index'),
    path('statistics/', views.statistics, name='statistics'),
    path('log-files/', views.log_files, name='log_files'),
    path('abnormal-queries/', views.abnormal_queries, name='abnormal_queries'),
    path('generate-report/', views.generate_report, name='generate_report'),
    path('api/logs/', views.api_logs, name='api_logs'),
]
