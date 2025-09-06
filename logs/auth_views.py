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
                return redirect('logs:login')
                
            except IntegrityError:
                messages.error(request, 'Tên người dùng đã tồn tại')
            except Exception as e:
                messages.error(request, f'Lỗi đăng ký: {str(e)}')
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
    """View đăng nhập người dùng"""
    if request.user.is_authenticated:
        return redirect('logs:index')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            # Xác thực người dùng
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                if user.is_active:
                    # Đăng nhập thành công
                    login(request, user)
                    
                    # Cập nhật thời gian đăng nhập cuối
                    user.last_login_at = timezone.now()
                    user.save(update_fields=['last_login_at'])
                    
                    messages.success(request, f'Chào mừng {user.username}!')
                    
                    # Chuyển hướng đến trang được yêu cầu hoặc trang chủ
                    next_url = request.GET.get('next', 'logs:index')
                    return redirect(next_url)
                else:
                    messages.error(request, 'Tài khoản của bạn đã bị vô hiệu hóa')
            else:
                messages.error(request, 'Tên người dùng hoặc mật khẩu không đúng')
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
