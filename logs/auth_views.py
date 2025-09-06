#!/usr/bin/env python3
"""
Views cho hệ thống xác thực người dùng
"""

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.db import IntegrityError
from .models import CustomUser
from .forms import UserRegistrationForm, UserLoginForm
from .logging_utils import ActivityLogger


@csrf_protect
@never_cache
def register_view(request):
    """View đăng ký người dùng mới"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                # Tạo người dùng mới
                user = CustomUser.objects.create_user(
                    username=form.cleaned_data['username'],
                    email=form.cleaned_data['email'],
                    password=form.cleaned_data['password']
                )
                
                # Cập nhật thông tin bổ sung
                user.first_name = form.cleaned_data.get('first_name', '')
                user.last_name = form.cleaned_data.get('last_name', '')
                user.save()
                
                messages.success(request, 'Đăng ký thành công! Bạn có thể đăng nhập ngay bây giờ.')
                
                # Ghi log đăng ký thành công
                ActivityLogger.log_user_registration(request, user, success=True)
                
                return redirect('logs:login')
                
            except IntegrityError:
                messages.error(request, 'Tên người dùng đã tồn tại')
                # Ghi log đăng ký thất bại
                ActivityLogger.log_user_registration(request, None, success=False, failure_reason="Username already exists")
            except Exception as e:
                messages.error(request, f'Lỗi đăng ký: {str(e)}')
                # Ghi log đăng ký thất bại
                ActivityLogger.log_user_registration(request, None, success=False, failure_reason=str(e))
    else:
        form = UserRegistrationForm()
    
    context = {
        'form': form,
        'title': 'Đăng ký tài khoản'
    }
    return render(request, 'logs/auth/register.html', context)


@csrf_protect
@never_cache
def login_view(request):
    """View đăng nhập người dùng với tính năng khóa tài khoản"""
    if request.user.is_authenticated:
        return redirect('logs:index')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Kiểm tra user có tồn tại không
            try:
                user = CustomUser.objects.get(username=username)
                
                # Kiểm tra tài khoản có bị khóa không
                if user.is_account_locked():
                    remaining_time = user.get_lockout_remaining_time()
                    minutes = remaining_time // 60
                    seconds = remaining_time % 60
                    
                    if minutes > 0:
                        messages.error(request, f'Tài khoản đã bị khóa do nhập sai mật khẩu quá nhiều lần. Vui lòng thử lại sau {minutes} phút {seconds} giây.')
                    else:
                        messages.error(request, f'Tài khoản đã bị khóa do nhập sai mật khẩu quá nhiều lần. Vui lòng thử lại sau {seconds} giây.')
                    
                    # Ghi log đăng nhập thất bại - tài khoản bị khóa
                    ActivityLogger.log_user_login(request, user, success=False, failure_reason="Account locked")
                    return render(request, 'logs/auth/login.html', {
                        'form': form,
                        'title': 'Đăng nhập',
                        'next': request.GET.get('next', ''),
                        'account_locked': True,
                        'remaining_time': remaining_time
                    })
                
                # Kiểm tra tài khoản có active không
                if not user.is_active:
                    messages.error(request, 'Tài khoản của bạn đã bị vô hiệu hóa')
                    # Ghi log đăng nhập thất bại
                    ActivityLogger.log_user_login(request, user, success=False, failure_reason="Account disabled")
                    return render(request, 'logs/auth/login.html', {
                        'form': form,
                        'title': 'Đăng nhập',
                        'next': request.GET.get('next', '')
                    })
                
                # Xác thực mật khẩu
                if user.check_password(password):
                    # Reset số lần đăng nhập thất bại
                    user.reset_failed_login()
                    
                    # Cập nhật thời gian đăng nhập cuối
                    user.last_login_at = timezone.now()
                    user.save(update_fields=['last_login_at'])
                    
                    # Kiểm tra MFA
                    if user.mfa_enabled:
                        # Lưu thông tin đăng nhập vào session để xác thực MFA
                        request.session['pending_user_id'] = user.id
                        request.session['pending_username'] = user.username
                        request.session['pending_next'] = request.GET.get('next', 'logs:index')
                        
                        # Ghi log đăng nhập thành công (chưa hoàn tất MFA)
                        ActivityLogger.log_user_login(request, user, success=True, mfa_pending=True)
                        
                        messages.info(request, 'Vui lòng xác thực MFA để hoàn tất đăng nhập.')
                        return redirect('logs:mfa_verification')
                    else:
                        # Đăng nhập thành công (không có MFA)
                        login(request, user)
                        
                        messages.success(request, f'Chào mừng {user.username}!')
                        
                        # Ghi log đăng nhập thành công
                        ActivityLogger.log_user_login(request, user, success=True)
                        
                        # Chuyển hướng đến trang được yêu cầu hoặc trang chủ
                        next_url = request.GET.get('next', 'logs:index')
                        return redirect(next_url)
                else:
                    # Mật khẩu sai - tăng số lần thất bại
                    user.increment_failed_login()
                    
                    # Kiểm tra xem có bị khóa không sau khi tăng
                    if user.is_account_locked():
                        remaining_time = user.get_lockout_remaining_time()
                        minutes = remaining_time // 60
                        seconds = remaining_time % 60
                        
                        if minutes > 0:
                            messages.error(request, f'Tài khoản đã bị khóa do nhập sai mật khẩu quá nhiều lần. Vui lòng thử lại sau {minutes} phút {seconds} giây.')
                        else:
                            messages.error(request, f'Tài khoản đã bị khóa do nhập sai mật khẩu quá nhiều lần. Vui lòng thử lại sau {seconds} giây.')
                        
                        # Ghi log đăng nhập thất bại - tài khoản bị khóa
                        ActivityLogger.log_user_login(request, user, success=False, failure_reason="Account locked after failed attempts")
                        return render(request, 'logs/auth/login.html', {
                            'form': form,
                            'title': 'Đăng nhập',
                            'next': request.GET.get('next', ''),
                            'account_locked': True,
                            'remaining_time': remaining_time
                        })
                    else:
                        # Chưa bị khóa, chỉ hiển thị thông báo lỗi
                        attempts_left = 3 - user.failed_login_attempts
                        if attempts_left > 0:
                            messages.error(request, f'Tên người dùng hoặc mật khẩu không đúng. Còn {attempts_left} lần thử.')
                        else:
                            messages.error(request, 'Tên người dùng hoặc mật khẩu không đúng.')
                        
                        # Ghi log đăng nhập thất bại
                        ActivityLogger.log_user_login(request, user, success=False, failure_reason="Invalid password")
                        
            except CustomUser.DoesNotExist:
                messages.error(request, 'Tên người dùng hoặc mật khẩu không đúng')
                # Ghi log đăng nhập thất bại
                ActivityLogger.log_user_login(request, None, success=False, failure_reason="User not found")
    else:
        form = UserLoginForm()
    
    context = {
        'form': form,
        'title': 'Đăng nhập',
        'next': request.GET.get('next', '')
    }
    return render(request, 'logs/auth/login.html', context)


@login_required
def logout_view(request):
    """View đăng xuất người dùng"""
    username = request.user.username
    user = request.user
    
    # Ghi log đăng xuất trước khi logout
    ActivityLogger.log_user_logout(request, user)
    
    logout(request)
    messages.success(request, f'Tạm biệt {username}! Bạn đã đăng xuất thành công.')
    return redirect('logs:login')


@login_required
def profile_view(request):
    """View hiển thị thông tin cá nhân"""
    user = request.user
    context = {
        'user': user,
        'title': 'Thông tin cá nhân'
    }
    return render(request, 'logs/auth/profile.html', context)


@login_required
def change_password_view(request):
    """View đổi mật khẩu"""
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Kiểm tra mật khẩu cũ
        if not request.user.check_password(old_password):
            messages.error(request, 'Mật khẩu cũ không đúng')
            return render(request, 'logs/auth/change_password.html')
        
        # Kiểm tra mật khẩu mới
        if new_password != confirm_password:
            messages.error(request, 'Mật khẩu mới và xác nhận mật khẩu không khớp')
            return render(request, 'logs/auth/change_password.html')
        
        if len(new_password) < 8:
            messages.error(request, 'Mật khẩu mới phải có ít nhất 8 ký tự')
            return render(request, 'logs/auth/change_password.html')
        
        # Cập nhật mật khẩu
        request.user.set_password(new_password)
        request.user.save()
        
        messages.success(request, 'Đổi mật khẩu thành công!')
        return redirect('logs:profile')
    
    context = {
        'title': 'Đổi mật khẩu'
    }
    return render(request, 'logs/auth/change_password.html', context)


def auth_required_view(request):
    """View hiển thị thông báo yêu cầu đăng nhập"""
    context = {
        'title': 'Yêu cầu đăng nhập',
        'message': 'Bạn cần đăng nhập để truy cập trang này.'
    }
    return render(request, 'logs/auth/auth_required.html', context)
