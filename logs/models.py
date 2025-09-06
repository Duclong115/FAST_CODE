from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.hashers import make_password, check_password
import pyotp
import secrets
import string


class CustomUser(AbstractUser):
    """Model người dùng tùy chỉnh"""
    
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Địa chỉ email của người dùng"
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Thời gian tạo",
        help_text="Thời gian tài khoản được tạo"
    )
    
    last_login_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Lần đăng nhập cuối",
        help_text="Thời gian đăng nhập cuối cùng"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Tài khoản hoạt động",
        help_text="Tài khoản có đang hoạt động không"
    )
    
    # Account lockout fields
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name="Số lần đăng nhập thất bại",
        help_text="Số lần đăng nhập thất bại liên tiếp"
    )
    
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Khóa đến",
        help_text="Thời gian tài khoản bị khóa đến (None = không bị khóa)"
    )
    
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Lần đăng nhập thất bại cuối",
        help_text="Thời gian đăng nhập thất bại cuối cùng"
    )
    
    # Fix reverse accessor conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="customuser_set",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="customuser_set",
        related_query_name="customuser",
    )
    
    # MFA fields
    mfa_enabled = models.BooleanField(
        default=False,
        verbose_name="MFA Enabled",
        help_text="Bật xác thực hai yếu tố"
    )
    
    mfa_secret_key = models.CharField(
        max_length=32,
        blank=True,
        null=True,
        verbose_name="MFA Secret Key",
        help_text="Secret key cho TOTP"
    )
    
    mfa_backup_codes = models.JSONField(
        default=list,
        blank=True,
        verbose_name="MFA Backup Codes",
        help_text="Danh sách backup codes"
    )
    
    class Meta:
        verbose_name = "Người dùng"
        verbose_name_plural = "Người dùng"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.username} ({self.email})"
    
    # Removed custom set_password and check_password methods
    # Django's AbstractUser already provides these methods
    
    def has_database_permission(self, database_name, permission_type='read'):
        """Kiểm tra user có quyền truy cập database không"""
        if self.is_superuser:
            return True
        
        try:
            permission = DatabasePermission.objects.get(
                user=self,
                database_name=database_name,
                is_active=True
            )
            
            # Kiểm tra quyền hết hạn
            if permission.is_expired():
                return False
            
            # Kiểm tra loại quyền
            permission_levels = {'read': 1, 'write': 2, 'admin': 3}
            required_level = permission_levels.get(permission_type, 1)
            user_level = permission_levels.get(permission.permission_type, 0)
            
            return user_level >= required_level
            
        except DatabasePermission.DoesNotExist:
            return False
    
    def get_accessible_databases(self):
        """Lấy danh sách database user có thể truy cập"""
        if self.is_superuser:
            # Superuser có thể truy cập tất cả database
            from django.db.models import Q
            return SqlLog.objects.values_list('database_name', flat=True).distinct()
        
        # Lấy danh sách database từ permissions
        permissions = DatabasePermission.objects.filter(
            user=self,
            is_active=True
        ).exclude(expires_at__lt=timezone.now())
        
        return [perm.database_name for perm in permissions if not perm.is_expired()]
    
    def get_database_permissions(self):
        """Lấy tất cả quyền database của user"""
        return DatabasePermission.objects.filter(user=self).order_by('-granted_at')
    
    def is_account_locked(self):
        """Kiểm tra tài khoản có bị khóa không"""
        if self.locked_until:
            return timezone.now() < self.locked_until
        return False
    
    def get_lockout_remaining_time(self):
        """Lấy thời gian còn lại của khóa tài khoản (tính bằng giây)"""
        if self.locked_until:
            remaining = self.locked_until - timezone.now()
            return max(0, int(remaining.total_seconds()))
        return 0
    
    def increment_failed_login(self):
        """Tăng số lần đăng nhập thất bại"""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # Nếu đã thất bại 3 lần, khóa tài khoản 10 phút
        if self.failed_login_attempts >= 3:
            from datetime import timedelta
            self.locked_until = timezone.now() + timedelta(minutes=10)
        
        self.save(update_fields=['failed_login_attempts', 'last_failed_login', 'locked_until'])
    
    def reset_failed_login(self):
        """Reset số lần đăng nhập thất bại (khi đăng nhập thành công)"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_failed_login = None
        self.save(update_fields=['failed_login_attempts', 'locked_until', 'last_failed_login'])
    
    def unlock_account(self):
        """Mở khóa tài khoản (chỉ admin mới có thể làm)"""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.last_failed_login = None
        self.save(update_fields=['failed_login_attempts', 'locked_until', 'last_failed_login'])
    
    # MFA methods
    def generate_mfa_secret(self):
        """Tạo secret key cho MFA"""
        if not self.mfa_secret_key:
            self.mfa_secret_key = pyotp.random_base32()
            self.save(update_fields=['mfa_secret_key'])
        return self.mfa_secret_key
    
    def get_mfa_qr_code_url(self):
        """Lấy URL QR code cho MFA"""
        if not self.mfa_secret_key:
            self.generate_mfa_secret()
        
        totp_uri = pyotp.totp.TOTP(self.mfa_secret_key).provisioning_uri(
            name=self.email,
            issuer_name="SQL Log Analyzer"
        )
        return totp_uri
    
    def generate_backup_codes(self):
        """Tạo 10 backup codes"""
        codes = []
        for _ in range(10):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            codes.append(code)
        
        self.mfa_backup_codes = codes
        self.save(update_fields=['mfa_backup_codes'])
        return codes
    
    def verify_totp_code(self, code):
        """Xác thực TOTP code"""
        if not self.mfa_secret_key:
            return False
        
        totp = pyotp.TOTP(self.mfa_secret_key)
        return totp.verify(code, valid_window=1)
    
    def verify_backup_code(self, code):
        """Xác thực backup code"""
        if not self.mfa_backup_codes:
            return False
        
        if code in self.mfa_backup_codes:
            # Xóa backup code đã sử dụng
            self.mfa_backup_codes.remove(code)
            self.save(update_fields=['mfa_backup_codes'])
            return True
        return False
    
    def enable_mfa(self):
        """Bật MFA"""
        if not self.mfa_secret_key:
            self.generate_mfa_secret()
        if not self.mfa_backup_codes:
            self.generate_backup_codes()
        
        self.mfa_enabled = True
        self.save(update_fields=['mfa_enabled'])
    
    def disable_mfa(self):
        """Tắt MFA"""
        self.mfa_enabled = False
        self.mfa_secret_key = None
        self.mfa_backup_codes = []
        self.save(update_fields=['mfa_enabled', 'mfa_secret_key', 'mfa_backup_codes'])


class DatabasePermission(models.Model):
    """Model phân quyền truy cập database"""
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Người dùng",
        help_text="Người dùng được cấp quyền"
    )
    
    database_name = models.CharField(
        max_length=50,
        verbose_name="Tên Database",
        help_text="Tên database được cấp quyền truy cập"
    )
    
    permission_type = models.CharField(
        max_length=20,
        choices=[
            ('read', 'Chỉ đọc'),
            ('write', 'Đọc và ghi'),
            ('admin', 'Quản trị'),
        ],
        default='read',
        verbose_name="Loại quyền",
        help_text="Loại quyền truy cập database"
    )
    
    granted_by = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_permissions',
        verbose_name="Cấp quyền bởi",
        help_text="Người dùng đã cấp quyền này"
    )
    
    granted_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Thời gian cấp quyền",
        help_text="Thời gian quyền được cấp"
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Hết hạn vào",
        help_text="Thời gian quyền hết hạn (để trống = không hết hạn)"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Quyền hoạt động",
        help_text="Quyền có đang hoạt động không"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ghi chú",
        help_text="Ghi chú về quyền này"
    )
    
    class Meta:
        verbose_name = "Quyền Database"
        verbose_name_plural = "Quyền Database"
        unique_together = ['user', 'database_name']
        ordering = ['-granted_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['database_name']),
            models.Index(fields=['permission_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.database_name} ({self.permission_type})"
    
    def is_expired(self):
        """Kiểm tra quyền có hết hạn không"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def is_valid(self):
        """Kiểm tra quyền có hợp lệ không"""
        return self.is_active and not self.is_expired()


class SqlLog(models.Model):
    """Model để lưu trữ dữ liệu SQL log"""
    
    database_name = models.CharField(
        max_length=50, 
        verbose_name="Tên Database",
        help_text="Tên của database (VD: T24VN, WAY4, EBANK)"
    )
    
    sql_query = models.TextField(
        verbose_name="Câu SQL",
        help_text="Câu SQL được thực thi"
    )
    
    exec_time_ms = models.PositiveIntegerField(
        verbose_name="Thời gian thực thi (ms)",
        help_text="Thời gian thực thi câu SQL tính bằng milliseconds"
    )
    
    exec_count = models.PositiveIntegerField(
        verbose_name="Số lần thực thi",
        help_text="Số lần câu SQL được thực thi"
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Thời gian tạo",
        help_text="Thời gian bản ghi được tạo"
    )
    
    line_number = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name="Số dòng trong file",
        help_text="Số dòng trong file log gốc"
    )
    
    optimization_suggestion = models.TextField(
        blank=True,
        null=True,
        verbose_name="Gợi ý tối ưu hóa",
        help_text="Gợi ý tối ưu hóa dựa trên phân tích SQL"
    )
    
    class Meta:
        verbose_name = "SQL Log"
        verbose_name_plural = "SQL Logs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['database_name']),
            models.Index(fields=['exec_time_ms']),
            models.Index(fields=['exec_count']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.database_name} - {self.sql_query[:50]}..."
    
    @property
    def exec_time_seconds(self):
        """Trả về thời gian thực thi tính bằng giây"""
        return self.exec_time_ms / 1000.0
    
    @property
    def avg_time_per_execution(self):
        """Trả về thời gian trung bình cho mỗi lần thực thi"""
        if self.exec_count > 0:
            return self.exec_time_ms / self.exec_count
        return 0


class LogFile(models.Model):
    """Model để lưu thông tin về file log đã được xử lý"""
    
    file_name = models.CharField(
        max_length=255,
        verbose_name="Tên file",
        help_text="Tên file log"
    )
    
    file_path = models.CharField(
        max_length=500,
        verbose_name="Đường dẫn file",
        help_text="Đường dẫn đầy đủ đến file log",
        blank=True,
        null=True
    )
    
    file_size = models.BigIntegerField(
        verbose_name="Kích thước file (bytes)",
        help_text="Kích thước file tính bằng bytes"
    )
    
    total_lines = models.PositiveIntegerField(
        verbose_name="Tổng số dòng",
        help_text="Tổng số dòng trong file",
        default=0
    )
    
    processed_lines = models.PositiveIntegerField(
        verbose_name="Số dòng đã xử lý",
        help_text="Số dòng đã được xử lý thành công",
        default=0
    )
    
    imported_count = models.PositiveIntegerField(
        verbose_name="Số logs đã import",
        help_text="Số logs đã được import thành công",
        default=0
    )
    
    skipped_count = models.PositiveIntegerField(
        verbose_name="Số logs bị bỏ qua",
        help_text="Số logs bị bỏ qua do không có quyền",
        default=0
    )
    
    error_count = models.PositiveIntegerField(
        verbose_name="Số lỗi",
        help_text="Số dòng bị lỗi khi xử lý",
        default=0
    )
    
    processed_by = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name="Người xử lý",
        help_text="User đã xử lý file này",
        null=True,
        blank=True
    )
    
    failed_lines = models.PositiveIntegerField(
        default=0,
        verbose_name="Số dòng lỗi",
        help_text="Số dòng không thể xử lý"
    )
    
    processed_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Thời gian xử lý",
        help_text="Thời gian file được xử lý"
    )
    
    processing_time = models.DurationField(
        null=True,
        blank=True,
        verbose_name="Thời gian xử lý",
        help_text="Thời gian để xử lý file"
    )
    
    error_details = models.TextField(
        blank=True,
        null=True,
        verbose_name="Chi tiết lỗi",
        help_text="Chi tiết các dòng lỗi không thể xử lý"
    )
    
    class Meta:
        verbose_name = "Log File"
        verbose_name_plural = "Log Files"
        ordering = ['-processed_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.processed_lines}/{self.total_lines} dòng"
    
    @property
    def success_rate(self):
        """Tỷ lệ thành công"""
        if self.total_lines > 0:
            return (self.processed_lines / self.total_lines) * 100
        return 0