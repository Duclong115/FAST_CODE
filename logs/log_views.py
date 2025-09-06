#!/usr/bin/env python3
"""
Views để xem và quản lý logs
"""

import os
import logging
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.conf import settings
from .admin_views import is_admin
from .logging_utils import ActivityLogger

# Logger
logger = logging.getLogger('logs')


@login_required
@user_passes_test(is_admin)
def admin_log_viewer(request):
    """Trang xem logs cho admin"""
    log_type = request.GET.get('type', 'web_activity')
    page_number = request.GET.get('page', 1)
    search = request.GET.get('search', '')
    
    # Đường dẫn đến các file log
    log_files = {
        'web_activity': 'logs/web_activity.log',
        'security': 'logs/security.log',
        'django_general': 'logs/django_general.log',
        'django_errors': 'logs/django_errors.log',
    }
    
    log_file_path = log_files.get(log_type, 'logs/web_activity.log')
    full_path = os.path.join(settings.BASE_DIR, log_file_path)
    
    # Đọc log file
    log_entries = []
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Lọc theo search nếu có
            if search:
                lines = [line for line in lines if search.lower() in line.lower()]
            
            # Đảo ngược để hiển thị mới nhất trước
            lines.reverse()
            
            # Phân trang
            paginator = Paginator(lines, 50)
            page_obj = paginator.get_page(page_number)
            
            log_entries = page_obj.object_list
            
        except Exception as e:
            messages.error(request, f'Lỗi đọc file log: {str(e)}')
            logger.error(f'Error reading log file {full_path}: {str(e)}')
    
    # Thống kê
    stats = {
        'total_log_types': len(log_files),
        'current_log_type': log_type,
        'log_file_exists': os.path.exists(full_path),
        'log_file_size': os.path.getsize(full_path) if os.path.exists(full_path) else 0,
    }
    
    context = {
        'title': 'Log Viewer',
        'log_entries': log_entries,
        'page_obj': page_obj,
        'log_type': log_type,
        'log_types': list(log_files.keys()),
        'search': search,
        'stats': stats,
    }
    
    return render(request, 'logs/admin/log_viewer.html', context)


@login_required
@user_passes_test(is_admin)
def admin_log_download(request):
    """Tải xuống file log"""
    log_type = request.GET.get('type', 'web_activity')
    
    log_files = {
        'web_activity': 'logs/web_activity.log',
        'security': 'logs/security.log',
        'django_general': 'logs/django_general.log',
        'django_errors': 'logs/django_errors.log',
    }
    
    log_file_path = log_files.get(log_type, 'logs/web_activity.log')
    full_path = os.path.join(settings.BASE_DIR, log_file_path)
    
    if not os.path.exists(full_path):
        messages.error(request, f'File log {log_type} không tồn tại!')
        return redirect('logs:admin_log_viewer')
    
    try:
        with open(full_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type='text/plain')
            response['Content-Disposition'] = f'attachment; filename="{log_type}_{timezone.now().strftime("%Y%m%d_%H%M%S")}.log"'
            
            # Ghi log hoạt động tải xuống
            ActivityLogger.log_admin_action(request, f"LOG_DOWNLOAD_{log_type}")
            
            return response
            
    except Exception as e:
        messages.error(request, f'Lỗi tải xuống file log: {str(e)}')
        logger.error(f'Error downloading log file {full_path}: {str(e)}')
        return redirect('logs:admin_log_viewer')


@login_required
@user_passes_test(is_admin)
def admin_log_clear(request):
    """Xóa nội dung file log"""
    if request.method == 'POST':
        log_type = request.POST.get('log_type')
        
        log_files = {
            'web_activity': 'logs/web_activity.log',
            'security': 'logs/security.log',
            'django_general': 'logs/django_general.log',
            'django_errors': 'logs/django_errors.log',
        }
        
        log_file_path = log_files.get(log_type)
        if not log_file_path:
            messages.error(request, 'Loại log không hợp lệ!')
            return redirect('logs:admin_log_viewer')
        
        full_path = os.path.join(settings.BASE_DIR, log_file_path)
        
        try:
            # Backup file hiện tại trước khi xóa
            backup_path = f"{full_path}.backup_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
            if os.path.exists(full_path):
                os.rename(full_path, backup_path)
            
            # Tạo file mới
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(f"# Log file cleared at {timezone.now()}\n")
            
            messages.success(request, f'Đã xóa thành công file log {log_type}!')
            
            # Ghi log hoạt động xóa log
            ActivityLogger.log_admin_action(request, f"LOG_CLEAR_{log_type}")
            
        except Exception as e:
            messages.error(request, f'Lỗi xóa file log: {str(e)}')
            logger.error(f'Error clearing log file {full_path}: {str(e)}')
    
    return redirect('logs:admin_log_viewer')


@login_required
@user_passes_test(is_admin)
def admin_log_stats(request):
    """Thống kê logs"""
    log_files = {
        'web_activity': 'logs/web_activity.log',
        'security': 'logs/security.log',
        'django_general': 'logs/django_general.log',
        'django_errors': 'logs/django_errors.log',
    }
    
    stats = {}
    total_size = 0
    
    for log_type, log_file_path in log_files.items():
        full_path = os.path.join(settings.BASE_DIR, log_file_path)
        
        if os.path.exists(full_path):
            file_size = os.path.getsize(full_path)
            total_size += file_size
            
            # Đếm số dòng
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
            except:
                line_count = 0
            
            stats[log_type] = {
                'size': file_size,
                'size_mb': round(file_size / (1024 * 1024), 2),
                'line_count': line_count,
                'exists': True,
            }
        else:
            stats[log_type] = {
                'size': 0,
                'size_mb': 0,
                'line_count': 0,
                'exists': False,
            }
    
    context = {
        'title': 'Log Statistics',
        'stats': stats,
        'total_size': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
    }
    
    return render(request, 'logs/admin/log_stats.html', context)


@login_required
@user_passes_test(is_admin)
def admin_log_search(request):
    """Tìm kiếm trong logs"""
    if request.method == 'POST':
        search_term = request.POST.get('search_term', '')
        log_types = request.POST.getlist('log_types')
        
        if not search_term:
            messages.error(request, 'Vui lòng nhập từ khóa tìm kiếm!')
            return redirect('logs:admin_log_viewer')
        
        if not log_types:
            log_types = ['web_activity', 'security', 'django_general', 'django_errors']
        
        log_files = {
            'web_activity': 'logs/web_activity.log',
            'security': 'logs/security.log',
            'django_general': 'logs/django_general.log',
            'django_errors': 'logs/django_errors.log',
        }
        
        results = []
        
        for log_type in log_types:
            log_file_path = log_files.get(log_type)
            if not log_file_path:
                continue
                
            full_path = os.path.join(settings.BASE_DIR, log_file_path)
            
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if search_term.lower() in line.lower():
                                results.append({
                                    'log_type': log_type,
                                    'line_number': line_num,
                                    'content': line.strip(),
                                })
                except Exception as e:
                    logger.error(f'Error searching in log file {full_path}: {str(e)}')
        
        # Sắp xếp theo thời gian (giả định log mới hơn ở cuối file)
        results.sort(key=lambda x: x['line_number'], reverse=True)
        
        # Phân trang
        paginator = Paginator(results, 50)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        
        # Ghi log hoạt động tìm kiếm
        ActivityLogger.log_admin_action(
            request, 
            f"LOG_SEARCH", 
            f"Term: {search_term}, Types: {log_types}, Results: {len(results)}"
        )
        
        context = {
            'title': 'Log Search Results',
            'search_term': search_term,
            'log_types': log_types,
            'results': page_obj.object_list,
            'page_obj': page_obj,
            'total_results': len(results),
        }
        
        return render(request, 'logs/admin/log_search_results.html', context)
    
    return redirect('logs:admin_log_viewer')
