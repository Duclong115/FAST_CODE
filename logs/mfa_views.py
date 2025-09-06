#!/usr/bin/env python3
"""
Views cho Multi-Factor Authentication (MFA)
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import AnonymousUser
import qrcode
import io
import base64
from .models import CustomUser


@login_required
def mfa_setup(request):
    """Trang thiết lập MFA"""
    user = request.user
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'enable':
            # Bật MFA
            user.enable_mfa()
            messages.success(request, 'MFA đã được bật thành công!')
            
            # Ghi log
            from .logging_utils import ActivityLogger
            ActivityLogger.log_mfa_setup(request, user, 'ENABLED')
            
            return redirect('logs:mfa_setup')
        
        elif action == 'disable':
            # Tắt MFA
            user.disable_mfa()
            messages.success(request, 'MFA đã được tắt thành công!')
            
            # Ghi log
            from .logging_utils import ActivityLogger
            ActivityLogger.log_mfa_setup(request, user, 'DISABLED')
            
            return redirect('logs:mfa_setup')
        
        elif action == 'regenerate_backup_codes':
            # Tạo lại backup codes
            codes = user.generate_backup_codes()
            messages.success(request, 'Backup codes đã được tạo lại thành công!')
            
            # Ghi log
            from .logging_utils import ActivityLogger
            ActivityLogger.log_mfa_setup(request, user, 'REGENERATE_BACKUP_CODES')
            
            return redirect('logs:mfa_backup_codes')
    
    # Tạo QR code nếu chưa có secret key
    qr_code_data = None
    if not user.mfa_secret_key:
        user.generate_mfa_secret()
    
    qr_code_url = user.get_mfa_qr_code_url()
    
    # Tạo QR code image
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_code_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    qr_code_data = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'title': 'Thiết lập MFA',
        'qr_code_data': qr_code_data,
        'secret_key': user.mfa_secret_key,
        'mfa_enabled': user.mfa_enabled,
        'backup_codes_count': len(user.mfa_backup_codes) if user.mfa_backup_codes else 0
    }
    
    return render(request, 'logs/mfa_setup.html', context)


@login_required
def mfa_backup_codes(request):
    """Trang hiển thị backup codes"""
    user = request.user
    
    if not user.mfa_enabled:
        messages.warning(request, 'MFA chưa được bật. Vui lòng bật MFA trước.')
        return redirect('logs:mfa_setup')
    
    # Tạo backup codes nếu chưa có
    if not user.mfa_backup_codes:
        user.generate_backup_codes()
    
    context = {
        'title': 'Backup Codes',
        'backup_codes': user.mfa_backup_codes,
        'backup_codes_count': len(user.mfa_backup_codes)
    }
    
    return render(request, 'logs/mfa_backup_codes.html', context)


@login_required
def download_backup_codes(request):
    """Tải xuống backup codes dạng file txt"""
    user = request.user
    
    if not user.mfa_enabled:
        messages.error(request, 'MFA chưa được bật.')
        return redirect('logs:mfa_setup')
    
    if not user.mfa_backup_codes:
        messages.error(request, 'Không có backup codes.')
        return redirect('logs:mfa_backup_codes')
    
    # Tạo nội dung file
    content = f"""SQL Log Analyzer - Backup Codes
User: {user.username}
Email: {user.email}
Generated: {user.date_joined.strftime('%Y-%m-%d %H:%M:%S')}

BACKUP CODES (Sử dụng một lần):
"""
    
    for i, code in enumerate(user.mfa_backup_codes, 1):
        content += f"{i:2d}. {code}\n"
    
    content += f"""
Lưu ý:
- Mỗi backup code chỉ sử dụng được một lần
- Lưu trữ file này ở nơi an toàn
- Không chia sẻ backup codes với ai khác
- Nếu mất tất cả backup codes, liên hệ admin để reset MFA
"""
    
    # Tạo response
    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="backup_codes_{user.username}.txt"'
    
    return response


@csrf_protect
@require_http_methods(["POST"])
def verify_mfa_code(request):
    """API endpoint để xác thực MFA code"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Chưa đăng nhập'}, status=401)
    
    user = request.user
    code = request.POST.get('code', '').strip()
    
    if not code:
        return JsonResponse({'error': 'Vui lòng nhập code'}, status=400)
    
    # Thử xác thực TOTP code trước
    if user.verify_totp_code(code):
        return JsonResponse({'success': True, 'type': 'totp'})
    
    # Thử xác thực backup code
    if user.verify_backup_code(code):
        return JsonResponse({'success': True, 'type': 'backup'})
    
    return JsonResponse({'error': 'Code không hợp lệ'}, status=400)


class MFAVerificationView(View):
    """View xác thực MFA cho đăng nhập"""
    
    def get(self, request):
        """Hiển thị form xác thực MFA"""
        # Kiểm tra có pending login không
        pending_user_id = request.session.get('pending_user_id')
        if not pending_user_id:
            return redirect('logs:login')
        
        try:
            user = CustomUser.objects.get(id=pending_user_id)
        except CustomUser.DoesNotExist:
            return redirect('logs:login')
        
        if not user.mfa_enabled:
            return redirect('logs:login')
        
        context = {
            'title': 'Xác thực MFA',
            'user': user,
            'pending_username': request.session.get('pending_username', '')
        }
        
        return render(request, 'logs/mfa_verification.html', context)
    
    def post(self, request):
        """Xử lý xác thực MFA"""
        # Kiểm tra có pending login không
        pending_user_id = request.session.get('pending_user_id')
        if not pending_user_id:
            return redirect('logs:login')
        
        try:
            user = CustomUser.objects.get(id=pending_user_id)
        except CustomUser.DoesNotExist:
            return redirect('logs:login')
        
        if not user.mfa_enabled:
            return redirect('logs:login')
        
        code = request.POST.get('code', '').strip()
        
        if not code:
            messages.error(request, 'Vui lòng nhập code xác thực.')
            return render(request, 'logs/mfa_verification.html', {
                'title': 'Xác thực MFA',
                'user': user,
                'pending_username': request.session.get('pending_username', '')
            })
        
        # Thử xác thực TOTP code
        if user.verify_totp_code(code):
            # Hoàn tất đăng nhập
            login(request, user)
            
            # Xóa thông tin pending
            del request.session['pending_user_id']
            del request.session['pending_username']
            next_url = request.session.pop('pending_next', 'logs:index')
            
            messages.success(request, 'Xác thực MFA thành công!')
            
            # Ghi log đăng nhập thành công (hoàn tất MFA)
            from .logging_utils import ActivityLogger
            ActivityLogger.log_user_login(request, user, success=True, mfa_completed=True)
            ActivityLogger.log_mfa_verification(request, user, success=True, method='TOTP')
            
            return redirect(next_url)
        
        # Thử xác thực backup code
        if user.verify_backup_code(code):
            # Hoàn tất đăng nhập
            login(request, user)
            
            # Xóa thông tin pending
            del request.session['pending_user_id']
            del request.session['pending_username']
            next_url = request.session.pop('pending_next', 'logs:index')
            
            messages.success(request, 'Xác thực MFA thành công bằng backup code!')
            
            # Ghi log đăng nhập thành công (hoàn tất MFA với backup code)
            from .logging_utils import ActivityLogger
            ActivityLogger.log_user_login(request, user, success=True, mfa_completed=True, mfa_method='backup_code')
            ActivityLogger.log_mfa_verification(request, user, success=True, method='BACKUP_CODE')
            ActivityLogger.log_backup_code_usage(request, user, success=True)
            
            return redirect(next_url)
        
        messages.error(request, 'Code xác thực không hợp lệ.')
        
        # Ghi log xác thực MFA thất bại
        from .logging_utils import ActivityLogger
        ActivityLogger.log_mfa_verification(request, user, success=False, failure_reason='Invalid code')
        
        return render(request, 'logs/mfa_verification.html', {
            'title': 'Xác thực MFA',
            'user': user,
            'pending_username': request.session.get('pending_username', '')
        })


# Decorator để kiểm tra MFA
def mfa_required(view_func):
    """Decorator yêu cầu xác thực MFA"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('logs:login')
        
        if request.user.mfa_enabled:
            # Kiểm tra xem đã xác thực MFA trong session chưa
            if not request.session.get('mfa_verified', False):
                return redirect('logs:mfa_verification')
        
        return view_func(request, *args, **kwargs)
    return wrapper
