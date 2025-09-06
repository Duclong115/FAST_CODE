from django.contrib import admin
from .models import SqlLog, LogFile


@admin.register(SqlLog)
class SqlLogAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'database_name', 'exec_time_ms', 'exec_count', 
        'avg_time_per_execution', 'line_number', 'created_at'
    ]
    list_filter = ['database_name', 'created_at']
    search_fields = ['sql_query', 'database_name']
    readonly_fields = ['avg_time_per_execution', 'exec_time_seconds']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Thông tin cơ bản', {
            'fields': ('database_name', 'sql_query', 'line_number')
        }),
        ('Thống kê thực thi', {
            'fields': ('exec_time_ms', 'exec_count', 'avg_time_per_execution', 'exec_time_seconds')
        }),
        ('Thời gian', {
            'fields': ('created_at',)
        }),
    )


@admin.register(LogFile)
class LogFileAdmin(admin.ModelAdmin):
    list_display = [
        'file_name', 'file_size', 'imported_count', 'skipped_count', 
        'error_count', 'processed_by', 'processed_at'
    ]
    list_filter = ['processed_at', 'processed_by']
    search_fields = ['file_name', 'processed_by__username']
    readonly_fields = ['processed_at']
    ordering = ['-processed_at']
    
    fieldsets = (
        ('Thông tin file', {
            'fields': ('file_name', 'file_path', 'file_size')
        }),
        ('Kết quả import', {
            'fields': ('imported_count', 'skipped_count', 'error_count', 'total_lines', 'processed_lines')
        }),
        ('Thông tin xử lý', {
            'fields': ('processed_by', 'processed_at')
        }),
    )