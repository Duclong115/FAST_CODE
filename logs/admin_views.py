#!/usr/bin/env python3
"""
Views quản lý người dùng cho quản trị viên
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
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.conf import settings
import secrets
import string
from .models import CustomUser
from .forms import AdminUserForm, AdminUserEditForm, AdminPasswordResetForm


def is_admin(user):
    """Kiểm tra user có phải admin không"""
    return user.is_authenticated and user.is_superuser


@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    """Dashboard quản trị viên"""
    # Thống kê tổng quan
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    inactive_users = total_users - active_users
    superusers = CustomUser.objects.filter(is_superuser=True).count()
    staff_users = CustomUser.objects.filter(is_staff=True).count()
    
    # Users mới trong 7 ngày
    week_ago = timezone.now() - timezone.timedelta(days=7)
    recent_users = CustomUser.objects.filter(created_at__gte=week_ago).count()
    
    # Users đăng nhập gần đây
    recent_login_users = CustomUser.objects.filter(
        last_login_at__gte=week_ago
    ).count()
    
    # Top 5 users đăng nhập nhiều nhất
    top_users = CustomUser.objects.filter(
        last_login_at__isnull=False
    ).order_by('-last_login_at')[:5]
    
    context = {
        'title': 'Dashboard Quản Trị',
        'total_users': total_users,
        'active_users': active_users,
        'inactive_users': inactive_users,
        'superusers': superusers,
        'staff_users': staff_users,
        'recent_users': recent_users,
        'recent_login_users': recent_login_users,
        'top_users': top_users,
    }
    
    return render(request, 'logs/admin/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_list(request):
    """Danh sách người dùng"""
    # Lấy tham số filter và search
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    role_filter = request.GET.get('role', '')
    page_number = request.GET.get('page', 1)
    per_page = request.GET.get('per_page', 20)
    
    # Query cơ bản
    users = CustomUser.objects.all()
    
    # Filter theo search
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Filter theo status
    if status_filter == 'active':
        users = users.filter(is_active=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    # Filter theo role
    if role_filter == 'superuser':
        users = users.filter(is_superuser=True)
    elif role_filter == 'staff':
        users = users.filter(is_staff=True, is_superuser=False)
    elif role_filter == 'user':
        users = users.filter(is_staff=False, is_superuser=False)
    
    # Sắp xếp
    users = users.order_by('-created_at')
    
    # Phân trang
    paginator = Paginator(users, per_page)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'title': 'Quản Lý Người Dùng',
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'role_filter': role_filter,
        'per_page': per_page,
        'total_users': users.count(),
    }
    
    return render(request, 'logs/admin/user_list.html', context)


@login_required
@user_passes_test(is_admin)
@csrf_protect
def admin_user_create(request):
    """Tạo người dùng mới"""
    if request.method == 'POST':
        form = AdminUserForm(request.POST)
        if form.is_valid():
            try:
                # Tạo user mới
                user = CustomUser.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                
                # Cập nhật thông tin bổ sung
                user.first_name = form.cleaned_data.get('first_name', '')
                user.last_name = form.cleaned_data.get('last_name', '')
                user.is_active = form.cleaned_data.get('is_active', True)
                user.is_staff = form.cleaned_data.get('is_staff', False)
                user.is_superuser = form.cleaned_data.get('is_superuser', False)
                user.save()
                
                messages.success(request, f'Đã tạo người dùng "{user.username}" thành công!')
                return redirect('logs:admin_user_list')
                
            except Exception as e:
                messages.error(request, f'Lỗi tạo người dùng: {str(e)}')
    else:
        form = AdminUserForm()
    
    context = {
        'title': 'Tạo Người Dùng Mới',
        'form': form,
    }
    
    return render(request, 'logs/admin/user_create.html', context)


@login_required
@user_passes_test(is_admin)
def admin_user_detail(request, user_id):
    """Chi tiết người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Thống kê đăng nhập
    login_stats = {
        'total_logins': 0,  # Có thể thêm model LoginLog để track
        'last_login': user.last_login_at,
        'created_at': user.created_at,
    }
    
    # Lấy phân quyền database của user
    user_permissions = user.get_database_permissions()
    
    context = {
        'title': f'Chi Tiết Người Dùng: {user.username}',
        'user': user,
        'login_stats': login_stats,
        'user_permissions': user_permissions,
    }
    
    return render(request, 'logs/admin/user_detail.html', context)


@login_required
@user_passes_test(is_admin)
@csrf_protect
def admin_user_edit(request, user_id):
    """Chỉnh sửa người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Đã cập nhật thông tin người dùng "{user.username}" thành công!')
                return redirect('logs:admin_user_detail', user_id=user.id)
                
            except Exception as e:
                messages.error(request, f'Lỗi cập nhật: {str(e)}')
    else:
        form = AdminUserEditForm(instance=user)
    
    context = {
        'title': f'Chỉnh Sửa Người Dùng: {user.username}',
        'form': form,
        'user': user,
    }
    
    return render(request, 'logs/admin/user_edit.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_user_toggle_active(request, user_id):
    """Bật/tắt trạng thái hoạt động của user"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Không cho phép tự khóa mình
    if user == request.user:
        messages.error(request, 'Không thể thay đổi trạng thái của chính mình!')
        return redirect('logs:admin_user_detail', user_id=user.id)
    
    try:
        user.is_active = not user.is_active
        user.save()
        
        status = 'kích hoạt' if user.is_active else 'vô hiệu hóa'
        messages.success(request, f'Đã {status} người dùng "{user.username}" thành công!')
        
    except Exception as e:
        messages.error(request, f'Lỗi thay đổi trạng thái: {str(e)}')
    
    return redirect('logs:admin_user_detail', user_id=user.id)


@login_required
@user_passes_test(is_admin)
@csrf_protect
def admin_user_reset_password(request, user_id):
    """Reset mật khẩu người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        force_change = request.POST.get('force_change')
        
        if not new_password or not confirm_password:
            messages.error(request, 'Vui lòng điền đầy đủ thông tin!')
        elif new_password != confirm_password:
            messages.error(request, 'Mật khẩu xác nhận không khớp!')
        elif len(new_password) < 8:
            messages.error(request, 'Mật khẩu phải có ít nhất 8 ký tự!')
        else:
            try:
                user.set_password(new_password)
                user.save()
                
                messages.success(request, f'Đã reset mật khẩu cho "{user.username}" thành công!')
                return redirect('logs:admin_user_detail', user_id=user.id)
                
            except Exception as e:
                messages.error(request, f'Lỗi reset mật khẩu: {str(e)}')
    
    context = {
        'title': f'Reset Mật Khẩu: {user.username}',
        'user': user,
    }
    
    return render(request, 'logs/admin/user_reset_password.html', context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_user_delete(request, user_id):
    """Xóa người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    # Không cho phép tự xóa mình
    if user == request.user:
        messages.error(request, 'Không thể xóa chính mình!')
        return redirect('logs:admin_user_detail', user_id=user.id)
    
    try:
        username = user.username
        user.delete()
        messages.success(request, f'Đã xóa người dùng "{username}" thành công!')
        return redirect('logs:admin_user_list')
        
    except Exception as e:
        messages.error(request, f'Lỗi xóa người dùng: {str(e)}')
        return redirect('logs:admin_user_detail', user_id=user.id)


@login_required
@user_passes_test(is_admin)
def admin_user_bulk_action(request):
    """Thực hiện hành động hàng loạt"""
    if request.method == 'POST':
        action = request.POST.get('action')
        user_ids = request.POST.getlist('user_ids')
        
        if not user_ids:
            messages.error(request, 'Vui lòng chọn ít nhất một người dùng!')
            return redirect('logs:admin_user_list')
        
        users = CustomUser.objects.filter(id__in=user_ids)
        
        try:
            if action == 'activate':
                users.update(is_active=True)
                messages.success(request, f'Đã kích hoạt {len(user_ids)} người dùng!')
            elif action == 'deactivate':
                # Không cho phép tự khóa mình
                users = users.exclude(id=request.user.id)
                users.update(is_active=False)
                messages.success(request, f'Đã vô hiệu hóa {users.count()} người dùng!')
            elif action == 'delete':
                # Không cho phép tự xóa mình
                users = users.exclude(id=request.user.id)
                count = users.count()
                users.delete()
                messages.success(request, f'Đã xóa {count} người dùng!')
            
        except Exception as e:
            messages.error(request, f'Lỗi thực hiện hành động: {str(e)}')
    
    return redirect('logs:admin_user_list')


@login_required
@user_passes_test(is_admin)
def admin_security_logs(request):
    """Log bảo mật"""
    # Có thể thêm model SecurityLog để track các hoạt động
    # Tạm thời tạo dữ liệu mẫu
    security_logs = [
        {
            'timestamp': timezone.now(),
            'user': request.user,
            'event_type': 'login',
            'ip_address': request.META.get('REMOTE_ADDR', 'Unknown'),
            'details': 'Admin login'
        }
    ]
    
    context = {
        'title': 'Log Bảo Mật',
        'security_logs': security_logs,
    }
    
    return render(request, 'logs/admin/security_logs.html', context)


def generate_secure_password(length=12):
    """Tạo mật khẩu bảo mật"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password


@login_required
@user_passes_test(is_admin)
def admin_generate_password(request):
    """API tạo mật khẩu bảo mật"""
    if request.method == 'POST':
        length = int(request.POST.get('length', 12))
        password = generate_secure_password(length)
        
        return JsonResponse({
            'success': True,
            'password': password,
            'strength': 'Strong' if length >= 12 else 'Medium'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
@user_passes_test(is_admin)
@require_http_methods(["POST"])
def admin_user_unlock(request, user_id):
    """Mở khóa tài khoản người dùng"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    try:
        # Mở khóa tài khoản
        user.unlock_account()
        
        # Ghi log admin action
        from .logging_utils import ActivityLogger
        ActivityLogger.log_admin_action(
            request, 'UNLOCK_ACCOUNT', user.id,
            f'Unlocked account for user: {user.username}'
        )
        
        messages.success(request, f'Đã mở khóa tài khoản "{user.username}" thành công!')
        
    except Exception as e:
        messages.error(request, f'Lỗi mở khóa tài khoản: {str(e)}')
    
    return redirect('logs:admin_user_detail', user_id=user.id)
