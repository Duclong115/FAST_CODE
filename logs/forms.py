#!/usr/bin/env python3
"""
Forms cho hệ thống xác thực
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import CustomUser, DatabasePermission


class UserRegistrationForm(forms.Form):
    """Form đăng ký người dùng mới"""
    
    username = forms.CharField(
        max_length=150,
        label='Tên người dùng',
        help_text='Tên người dùng phải có từ 3-150 ký tự',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên người dùng',
            'required': True
        })
    )
    
    email = forms.EmailField(
        label='Email',
        help_text='Địa chỉ email hợp lệ',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập địa chỉ email',
            'required': True
        })
    )
    
    password = forms.CharField(
        min_length=8,
        label='Mật khẩu',
        help_text='Mật khẩu phải có ít nhất 8 ký tự',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu',
            'required': True
        })
    )
    
    confirm_password = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu',
            'required': True
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label='Tên',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên (tùy chọn)'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label='Họ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập họ (tùy chọn)'
        })
    )
    
    def clean_username(self):
        """Kiểm tra tên người dùng"""
        username = self.cleaned_data.get('username')
        
        if len(username) < 3:
            raise ValidationError('Tên người dùng phải có ít nhất 3 ký tự')
        
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Tên người dùng đã tồn tại')
        
        return username
    
    def clean_email(self):
        """Kiểm tra email"""
        email = self.cleaned_data.get('email')
        
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Email đã được sử dụng')
        
        return email
    
    def clean(self):
        """Kiểm tra tổng thể form"""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password:
            if password != confirm_password:
                raise ValidationError('Mật khẩu và xác nhận mật khẩu không khớp')
        
        return cleaned_data


class UserLoginForm(forms.Form):
    """Form đăng nhập người dùng"""
    
    username = forms.CharField(
        max_length=150,
        label='Tên người dùng',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên người dùng',
            'required': True,
            'autofocus': True
        })
    )
    
    password = forms.CharField(
        label='Mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu',
            'required': True
        })
    )
    
    remember_me = forms.BooleanField(
        required=False,
        label='Ghi nhớ đăng nhập',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_username(self):
        """Kiểm tra tên người dùng"""
        username = self.cleaned_data.get('username')
        
        if not username:
            raise ValidationError('Vui lòng nhập tên người dùng')
        
        return username
    
    def clean_password(self):
        """Kiểm tra mật khẩu"""
        password = self.cleaned_data.get('password')
        
        if not password:
            raise ValidationError('Vui lòng nhập mật khẩu')
        
        return password


class AdminUserForm(forms.Form):
    """Form tạo người dùng cho admin"""
    
    username = forms.CharField(
        max_length=150,
        label='Tên người dùng',
        help_text='Tên người dùng phải có từ 3-150 ký tự',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên người dùng',
            'required': True
        })
    )
    
    email = forms.EmailField(
        label='Email',
        help_text='Địa chỉ email hợp lệ',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập địa chỉ email',
            'required': True
        })
    )
    
    password = forms.CharField(
        min_length=8,
        label='Mật khẩu',
        help_text='Mật khẩu phải có ít nhất 8 ký tự',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu',
            'required': True
        })
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label='Tên',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập tên (tùy chọn)'
        })
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label='Họ',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập họ (tùy chọn)'
        })
    )
    
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label='Tài khoản hoạt động',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    is_staff = forms.BooleanField(
        required=False,
        initial=False,
        label='Quyền Staff',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    is_superuser = forms.BooleanField(
        required=False,
        initial=False,
        label='Quyền Superuser',
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        })
    )
    
    def clean_username(self):
        """Kiểm tra tên người dùng"""
        username = self.cleaned_data.get('username')
        
        if len(username) < 3:
            raise ValidationError('Tên người dùng phải có ít nhất 3 ký tự')
        
        if CustomUser.objects.filter(username=username).exists():
            raise ValidationError('Tên người dùng đã tồn tại')
        
        return username
    
    def clean_email(self):
        """Kiểm tra email"""
        email = self.cleaned_data.get('email')
        
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError('Email đã được sử dụng')
        
        return email


class AdminUserEditForm(forms.ModelForm):
    """Form chỉnh sửa người dùng cho admin"""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'username': 'Tên người dùng',
            'email': 'Email',
            'first_name': 'Tên',
            'last_name': 'Họ',
            'is_active': 'Tài khoản hoạt động',
            'is_staff': 'Quyền Staff',
            'is_superuser': 'Quyền Superuser',
        }
    
    def clean_username(self):
        """Kiểm tra tên người dùng"""
        username = self.cleaned_data.get('username')
        
        if len(username) < 3:
            raise ValidationError('Tên người dùng phải có ít nhất 3 ký tự')
        
        # Kiểm tra trùng lặp (trừ user hiện tại)
        existing = CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk)
        if existing.exists():
            raise ValidationError('Tên người dùng đã tồn tại')
        
        return username
    
    def clean_email(self):
        """Kiểm tra email"""
        email = self.cleaned_data.get('email')
        
        # Kiểm tra trùng lặp (trừ user hiện tại)
        existing = CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk)
        if existing.exists():
            raise ValidationError('Email đã được sử dụng')
        
        return email


class AdminPasswordResetForm(forms.Form):
    """Form reset mật khẩu cho admin"""
    
    new_password = forms.CharField(
        min_length=8,
        label='Mật khẩu mới',
        help_text='Mật khẩu phải có ít nhất 8 ký tự',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập mật khẩu mới',
            'required': True
        })
    )
    
    confirm_password = forms.CharField(
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nhập lại mật khẩu mới',
            'required': True
        })
    )
    
    def clean(self):
        """Kiểm tra tổng thể form"""
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError('Mật khẩu mới và xác nhận mật khẩu không khớp')
        
        return cleaned_data


class DatabasePermissionForm(forms.Form):
    """Form tạo phân quyền database"""
    
    user = forms.ModelChoiceField(
        queryset=CustomUser.objects.filter(is_active=True).order_by('username'),
        label='Người dùng',
        help_text='Chọn người dùng để cấp quyền',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    database_name = forms.CharField(
        max_length=50,
        label='Tên Database',
        help_text='Tên database được cấp quyền truy cập',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'VD: T24VN, WAY4, EBANK',
            'required': True
        })
    )
    
    # Thêm field để chọn từ danh sách database có sẵn
    database_choice = forms.ChoiceField(
        required=False,
        label='Chọn từ Database có sẵn',
        help_text='Hoặc chọn từ danh sách database đã có trong hệ thống',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'database-choice'
        })
    )
    
    permission_type = forms.ChoiceField(
        choices=[
            ('read', 'Chỉ đọc'),
            ('write', 'Đọc và ghi'),
            ('admin', 'Quản trị'),
        ],
        label='Loại quyền',
        help_text='Loại quyền truy cập database',
        widget=forms.Select(attrs={
            'class': 'form-select',
            'required': True
        })
    )
    
    expires_at = forms.DateTimeField(
        required=False,
        label='Hết hạn vào',
        help_text='Thời gian quyền hết hạn (để trống = không hết hạn)',
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    notes = forms.CharField(
        required=False,
        label='Ghi chú',
        help_text='Ghi chú về quyền này',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'VD: Quyền truy cập cho dự án ABC...'
        })
    )
    
    def clean_database_name(self):
        """Kiểm tra tên database"""
        database_name = self.cleaned_data.get('database_name')
        database_choice = self.cleaned_data.get('database_choice')
        
        # Ưu tiên database_choice nếu có
        if database_choice:
            return database_choice.upper()
        
        if not database_name:
            raise ValidationError('Vui lòng nhập tên database hoặc chọn từ danh sách')
        
        if len(database_name) < 2:
            raise ValidationError('Tên database phải có ít nhất 2 ký tự')
        
        return database_name.upper()  # Chuyển thành chữ hoa
    
    def clean(self):
        """Kiểm tra tổng thể form"""
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        database_name = cleaned_data.get('database_name')
        
        if user and database_name:
            # Kiểm tra xem user đã có quyền với database này chưa
            from .models import DatabasePermission
            existing = DatabasePermission.objects.filter(
                user=user,
                database_name=database_name
            ).exists()
            
            if existing:
                raise ValidationError(f'Người dùng {user.username} đã có quyền truy cập database {database_name}!')
        
        return cleaned_data
    
    def save(self, commit=True):
        """Lưu phân quyền database"""
        from .models import DatabasePermission
        
        permission = DatabasePermission(
            user=self.cleaned_data['user'],
            database_name=self.cleaned_data['database_name'],
            permission_type=self.cleaned_data['permission_type'],
            expires_at=self.cleaned_data.get('expires_at'),
            notes=self.cleaned_data.get('notes', '')
        )
        
        if commit:
            permission.save()
        
        return permission


class DatabasePermissionEditForm(forms.ModelForm):
    """Form chỉnh sửa phân quyền database"""
    
    class Meta:
        model = DatabasePermission
        fields = ['permission_type', 'expires_at', 'is_active', 'notes']
        widgets = {
            'permission_type': forms.Select(attrs={'class': 'form-select'}),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
        labels = {
            'permission_type': 'Loại quyền',
            'expires_at': 'Hết hạn vào',
            'is_active': 'Quyền hoạt động',
            'notes': 'Ghi chú',
        }
