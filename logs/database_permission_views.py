#!/usr/bin/env python3
"""
Views quản lý phân quyền database
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from .models import CustomUser, DatabasePermission, SqlLog
from .forms import DatabasePermissionForm, DatabasePermissionEditForm
from .admin_views import is_admin
from .logging_utils import ActivityLogger


@login_required
@user_passes_test(is_admin)
def admin_database_permissions(request):
    """Quản lý phân quyền database"""
    # Lấy tham số filter và search
    search = request.GET.get('search', '')
    database_filter = request.GET.get('database', '')
    user_filter = request.GET.get('user', '')
    status_filter = request.GET.get('status', '')
    page_number = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    
    # Query cơ bản
    permissions = DatabasePermission.objects.select_related('user', 'granted_by').all()
    
    # Filter theo search
    if search:
        permissions = permissions.filter(
            Q(user__username__icontains=search) |
            Q(database_name__icontains=search) |
            Q(notes__icontains=search)
        )
    
    # Filter theo database
    if database_filter:
        permissions = permissions.filter(database_name=database_filter)
    
    # Filter theo user
    if user_filter:
        permissions = permissions.filter(user__username=user_filter)
    
    # Filter theo status
    if status_filter == 'active':
        permissions = permissions.filter(is_active=True)
    elif status_filter == 'inactive':
        permissions = permissions.filter(is_active=False)
    elif status_filter == 'expired':
        permissions = permissions.filter(expires_at__lt=timezone.now())
    
    # Sắp xếp
    permissions = permissions.order_by('-granted_at')
    
    # Phân trang
    paginator = Paginator(permissions, per_page)
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách database và users cho filter
    databases = SqlLog.objects.values_list('database_name', flat=True).distinct().order_by('database_name')
    users = CustomUser.objects.filter(is_active=True).order_by('username')
    
    context = {
        'title': 'Quản Lý Phân Quyền Database',
        'page_obj': page_obj,
        'search': search,
        'database_filter': database_filter,
        'user_filter': user_filter,
        'status_filter': status_filter,
        'per_page': per_page,
        'databases': databases,
        'users': users,
        'total_permissions': permissions.count(),
    }
    
    return render(request, 'logs/admin/database_permissions.html', context)


@login_required
@user_passes_test(is_admin)
@csrf_protect
def admin_database_permission_create(request):
    """Tạo phân quyền database mới"""
    if request.method == 'POST':
        form = DatabasePermissionForm(request.POST)
        if form.is_valid():
            try:
                permission = form.save(commit=False)
                permission.granted_by = request.user
                permission.save()
                
                messages.success(request, f'Đã cấp quyền "{permission.permission_type}" cho {permission.user.username} truy cập database {permission.database_name}!')
                
                # Ghi log hoạt động cấp quyền
                ActivityLogger.log_database_permission_action(
                    request, 'CREATE', permission.id, 
                    permission.user.id, permission.database_name
                )
                
                return redirect('logs:admin_database_permissions')
                
            except Exception as e:
                messages.error(request, f'Lỗi tạo phân quyền: {str(e)}')
    else:
        form = DatabasePermissionForm()
    
    # Lấy danh sách database có sẵn để hiển thị trong dropdown
    available_databases = SqlLog.objects.values_list('database_name', flat=True).distinct().order_by('database_name')
    
    # Cập nhật choices cho database_choice field
    form.fields['database_choice'].choices = [('', '-- Chọn database --')] + [(db, db) for db in available_databases]
    
    context = {
        'title': 'Cấp Quyền Database Mới',
        'form': form,
        'available_databases': available_databases,
    }
    
    return render(request, 'logs/admin/database_permission_create.html', context)


@login_required
@user_passes_test(is_admin)
def admin_database_permission_detail(request, permission_id):
    """Chi tiết phân quyền database"""
    permission = get_object_or_404(DatabasePermission, id=permission_id)
    
    # Thống kê sử dụng
    usage_stats = {
        'total_logs': SqlLog.objects.filter(database_name=permission.database_name).count(),
        'recent_logs': SqlLog.objects.filter(
            database_name=permission.database_name,
            created_at__gte=timezone.now() - timezone.timedelta(days=7)
        ).count(),
    }
    
    context = {
        'title': f'Chi Tiết Phân Quyền: {permission.user.username} - {permission.database_name}',
        'permission': permission,
        'usage_stats': usage_stats,
    }
    
    return render(request, 'logs/admin/database_permission_detail.html', context)


@login_required
@user_passes_test(is_admin)
@csrf_protect
def admin_database_permission_edit(request, permission_id):
    """Chỉnh sửa phân quyền database"""
    permission = get_object_or_404(DatabasePermission, id=permission_id)
    
    if request.method == 'POST':
        form = DatabasePermissionEditForm(request.POST, instance=permission)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Đã cập nhật phân quyền cho {permission.user.username} truy cập database {permission.database_name}!')
                
                # Ghi log hoạt động cập nhật quyền
                ActivityLogger.log_database_permission_action(
                    request, 'UPDATE', permission.id, 
                    permission.user.id, permission.database_name
                )
                
                return redirect('logs:admin_database_permission_detail', permission_id=permission.id)
                
            except Exception as e:
                messages.error(request, f'Lỗi cập nhật: {str(e)}')
    else:
        form = DatabasePermissionEditForm(instance=permission)
    
    context = {
        'title': f'Chỉnh Sửa Phân Quyền: {permission.user.username} - {permission.database_name}',
        'form': form,
        'permission': permission,
    }
    
    return render(request, 'logs/admin/database_permission_edit.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_database_permission_toggle_active(request, permission_id):
    """Bật/tắt phân quyền database"""
    permission = get_object_or_404(DatabasePermission, id=permission_id)
    
    try:
        permission.is_active = not permission.is_active
        permission.save()
        
        status = 'kích hoạt' if permission.is_active else 'vô hiệu hóa'
        messages.success(request, f'Đã {status} phân quyền cho {permission.user.username} truy cập database {permission.database_name}!')
        
    except Exception as e:
        messages.error(request, f'Lỗi thay đổi trạng thái: {str(e)}')
    
    return redirect('logs:admin_database_permission_detail', permission_id=permission.id)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_database_permission_delete(request, permission_id):
    """Xóa phân quyền database"""
    permission = get_object_or_404(DatabasePermission, id=permission_id)
    
    try:
        user_name = permission.user.username
        database_name = permission.database_name
        permission.delete()
        
        messages.success(request, f'Đã xóa phân quyền cho {user_name} truy cập database {database_name}!')
        
        # Ghi log hoạt động xóa quyền
        ActivityLogger.log_database_permission_action(
            request, 'DELETE', permission_id, 
            None, database_name
        )
        
        return redirect('logs:admin_database_permissions')
        
    except Exception as e:
        messages.error(request, f'Lỗi xóa phân quyền: {str(e)}')
        return redirect('logs:admin_database_permission_detail', permission_id=permission.id)


@login_required
@user_passes_test(is_admin)
def admin_database_permission_bulk_action(request):
    """Thực hiện hành động hàng loạt cho phân quyền"""
    if request.method == 'POST':
        action = request.POST.get('action')
        permission_ids = request.POST.getlist('permission_ids')
        
        if not permission_ids:
            messages.error(request, 'Vui lòng chọn ít nhất một phân quyền!')
            return redirect('logs:admin_database_permissions')
        
        permissions = DatabasePermission.objects.filter(id__in=permission_ids)
        
        try:
            if action == 'activate':
                updated_count = permissions.update(is_active=True)
                messages.success(request, f'✅ Đã kích hoạt thành công {updated_count} phân quyền!')
            elif action == 'deactivate':
                updated_count = permissions.update(is_active=False)
                messages.success(request, f'✅ Đã vô hiệu hóa thành công {updated_count} phân quyền!')
            elif action == 'delete':
                count = permissions.count()
                # Lấy thông tin trước khi xóa để hiển thị
                deleted_info = []
                for perm in permissions:
                    deleted_info.append(f"{perm.user.username} - {perm.database_name}")
                
                permissions.delete()
                messages.success(request, f'✅ Đã xóa thành công {count} phân quyền!')
                if deleted_info:
                    messages.info(request, f'📋 Các phân quyền đã xóa: {", ".join(deleted_info[:5])}{"..." if len(deleted_info) > 5 else ""}')
            else:
                messages.error(request, f'❌ Hành động "{action}" không hợp lệ!')
            
        except Exception as e:
            messages.error(request, f'❌ Lỗi thực hiện hành động "{action}": {str(e)}')
    
    return redirect('logs:admin_database_permissions')


@login_required
@user_passes_test(is_admin)
@csrf_protect
def admin_bulk_database_permission_create(request):
    """Cấp quyền database hàng loạt"""
    if request.method == 'POST':
        user_ids = request.POST.getlist('users')
        databases = request.POST.getlist('databases')
        permission_type = request.POST.get('permission_type')
        expires_at = request.POST.get('expires_at')
        notes = request.POST.get('notes', '')
        
        if not user_ids or not databases or not permission_type:
            messages.error(request, 'Vui lòng chọn người dùng, database và loại quyền!')
            return redirect('logs:admin_bulk_database_permission_create')
        
        # Parse expires_at
        expires_datetime = None
        if expires_at:
            try:
                from datetime import datetime
                naive_datetime = datetime.fromisoformat(expires_at)
                expires_datetime = timezone.make_aware(naive_datetime)
            except ValueError:
                messages.error(request, 'Định dạng thời gian không hợp lệ!')
                return redirect('logs:admin_bulk_database_permission_create')
        
        # Tạo phân quyền hàng loạt
        created_count = 0
        skipped_count = 0
        
        try:
            for user_id in user_ids:
                user = CustomUser.objects.get(id=user_id)
                for database_name in databases:
                    # Kiểm tra xem đã có quyền chưa
                    existing = DatabasePermission.objects.filter(
                        user=user,
                        database_name=database_name.upper()
                    ).exists()
                    
                    if existing:
                        skipped_count += 1
                        continue
                    
                    # Tạo phân quyền mới
                    DatabasePermission.objects.create(
                        user=user,
                        database_name=database_name.upper(),
                        permission_type=permission_type,
                        granted_by=request.user,
                        expires_at=expires_datetime,
                        notes=notes
                    )
                    created_count += 1
            
            if created_count > 0:
                messages.success(request, f'Đã tạo thành công {created_count} phân quyền!')
            if skipped_count > 0:
                messages.warning(request, f'Đã bỏ qua {skipped_count} phân quyền (đã tồn tại)!')
            
            return redirect('logs:admin_database_permissions')
            
        except Exception as e:
            messages.error(request, f'Lỗi tạo phân quyền hàng loạt: {str(e)}')
    else:
        # GET request - hiển thị form
        users = CustomUser.objects.filter(is_active=True).order_by('username')
        available_databases = SqlLog.objects.values_list('database_name', flat=True).distinct().order_by('database_name')
        
        context = {
            'title': 'Cấp Quyền Database Hàng Loạt',
            'users': users,
            'available_databases': available_databases,
        }
        
        return render(request, 'logs/admin/bulk_database_permission_create.html', context)


@login_required
def user_database_permissions(request):
    """Xem phân quyền database của user hiện tại"""
    user = request.user
    permissions = user.get_database_permissions()
    
    # Thống kê
    stats = {
        'total_permissions': permissions.count(),
        'active_permissions': permissions.filter(is_active=True).count(),
        'expired_permissions': permissions.filter(expires_at__lt=timezone.now()).count(),
        'accessible_databases': len(user.get_accessible_databases()),
    }
    
    context = {
        'title': 'Phân Quyền Database Của Tôi',
        'permissions': permissions,
        'stats': stats,
        'accessible_databases': user.get_accessible_databases(),
    }
    
    return render(request, 'logs/user_database_permissions.html', context)


def check_database_permission(user, database_name, permission_type='read'):
    """Helper function để kiểm tra quyền database"""
    if not user.is_authenticated:
        return False
    
    return user.has_database_permission(database_name, permission_type)


def require_database_permission(permission_type='read'):
    """Decorator để yêu cầu quyền database"""
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Lấy database_name từ kwargs hoặc request.GET
            database_name = kwargs.get('database_name') or request.GET.get('database')
            
            if not database_name:
                messages.error(request, 'Không xác định được database!')
                return redirect('logs:index')
            
            if not check_database_permission(request.user, database_name, permission_type):
                messages.error(request, f'Bạn không có quyền truy cập database "{database_name}"!')
                return redirect('logs:index')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
