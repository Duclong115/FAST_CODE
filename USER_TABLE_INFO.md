# 👥 Thông Tin Bảng Chứa User/Password

## 📋 Tổng Quan

Bảng chứa thông tin user và password trong hệ thống SQL Log Analyzer.

## 🗄️ Thông Tin Bảng

### ✅ Tên Bảng
```
logs_customuser
```

### ✅ Database
- **Engine**: PostgreSQL
- **Database**: `sql_log_analyzer`
- **Host**: `localhost`
- **Port**: `5432`
- **User**: `postgres`

### ✅ Model Django
```python
class CustomUser(AbstractUser):
    # Kế thừa từ Django's AbstractUser
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    last_login_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
```

## 🔍 Cấu Trúc Bảng

### Các Trường Chính

| Trường | Kiểu Dữ Liệu | Mô Tả |
|--------|--------------|-------|
| `id` | `bigint` | Primary key, tự động tăng |
| `username` | `varchar` | Tên người dùng (unique) |
| `password` | `varchar` | **Mật khẩu đã mã hóa** |
| `email` | `varchar` | Email (unique) |
| `first_name` | `varchar` | Tên |
| `last_name` | `varchar` | Họ |
| `is_active` | `boolean` | Tài khoản có hoạt động |
| `is_superuser` | `boolean` | Có phải superuser |
| `is_staff` | `boolean` | Có phải staff |
| `date_joined` | `timestamp` | Ngày tham gia |
| `last_login` | `timestamp` | Lần đăng nhập cuối (Django) |
| `created_at` | `timestamp` | Ngày tạo tài khoản |
| `last_login_at` | `timestamp` | Lần đăng nhập cuối (custom) |

### 🔐 Trường Password

**Trường**: `password` (varchar)
**Mã hóa**: PBKDF2-SHA256 với 1,000,000 iterations
**Format**: `pbkdf2_sha256$iterations$salt$hash`

**Ví dụ**:
```
pbkdf2_sha256$1000000$8ABrcIZIuRpwiSwh09kcrG$yKBusm24eyyoeCuz0ZQJ5yJPxRfGTQ2hEgysu2nubw0=
```

## 👥 Dữ Liệu Hiện Tại

### Danh Sách Users

| ID | Username | Email | Role | Status |
|----|----------|-------|------|--------|
| 5 | `admin` | admin@example.com | Superuser | Active |
| 6 | `testuser` | test@example.com | User | Active |
| 7 | `thuongvn` | ngocthuongfcvn@gmail.com | User | Active |
| 8 | `secureuser` | secure@example.com | User | Active |

### Thông Tin Chi Tiết

#### 👤 Admin User
- **Username**: `admin`
- **Email**: `admin@example.com`
- **Password**: `admin123` (đã mã hóa)
- **Role**: Superuser + Staff
- **Created**: 2025-09-06 04:17:24
- **Last Login**: 2025-09-06 04:25:30

#### 👤 Test User
- **Username**: `testuser`
- **Email**: `test@example.com`
- **Password**: `test123` (đã mã hóa)
- **Role**: Regular User
- **Created**: 2025-09-06 04:17:24
- **Last Login**: Never

#### 👤 Real User
- **Username**: `thuongvn`
- **Email**: `ngocthuongfcvn@gmail.com`
- **Password**: `[mật khẩu của bạn]` (đã mã hóa)
- **Role**: Regular User
- **Created**: 2025-09-06 04:19:17
- **Last Login**: 2025-09-06 04:19:26

#### 👤 Secure User
- **Username**: `secureuser`
- **Email**: `secure@example.com`
- **Password**: `SecurePass123!@#` (đã mã hóa)
- **Role**: Regular User
- **Created**: 2025-09-06 04:20:30
- **Last Login**: Never

## 🔒 Bảo Mật

### ✅ Mã Hóa Mật Khẩu
- **Algorithm**: PBKDF2-SHA256
- **Iterations**: 1,000,000 (rất cao)
- **Salt**: Ngẫu nhiên cho mỗi mật khẩu
- **Hash Length**: 89 ký tự

### ✅ Validation
- **Minimum Length**: 8 ký tự
- **Complexity**: Không chỉ số, không giống thông tin cá nhân
- **Uniqueness**: Username và email unique

### ✅ Session Management
- **Timeout**: 24 giờ
- **Save Every Request**: Có
- **CSRF Protection**: Có

## 🛠️ Truy Vấn Database

### Xem Tất Cả Users
```sql
SELECT id, username, email, is_active, is_superuser, created_at 
FROM logs_customuser 
ORDER BY created_at DESC;
```

### Xem Thông Tin User Cụ Thể
```sql
SELECT * FROM logs_customuser WHERE username = 'admin';
```

### Đếm Số Users
```sql
SELECT COUNT(*) as total_users FROM logs_customuser;
```

### Users Hoạt Động
```sql
SELECT COUNT(*) as active_users 
FROM logs_customuser 
WHERE is_active = true;
```

## 🔧 Quản Lý Users

### Tạo User Mới (Django)
```python
from logs.models import CustomUser

# Tạo user thường
user = CustomUser.objects.create_user(
    username='newuser',
    email='new@example.com',
    password='newpassword123'
)

# Tạo superuser
admin = CustomUser.objects.create_superuser(
    username='newadmin',
    email='admin@example.com',
    password='adminpassword123'
)
```

### Cập Nhật User
```python
# Cập nhật thông tin
user = CustomUser.objects.get(username='testuser')
user.email = 'newemail@example.com'
user.first_name = 'New'
user.last_name = 'Name'
user.save()

# Đổi mật khẩu
user.set_password('newpassword123')
user.save()
```

### Xóa User
```python
# Xóa user
user = CustomUser.objects.get(username='testuser')
user.delete()
```

## 📊 Thống Kê

### Tổng Quan
- **Tổng số users**: 4
- **Users hoạt động**: 4
- **Superusers**: 1
- **Regular users**: 3

### Phân Bố Theo Thời Gian
- **2025-09-06**: 4 users được tạo
- **Peak time**: 04:17-04:20 (tạo nhiều users)

## 🚨 Lưu Ý Bảo Mật

### ✅ Đã Thực Hiện
1. **Mật khẩu được mã hóa**: Không có plain text
2. **Salt ngẫu nhiên**: Mỗi mật khẩu có salt riêng
3. **Iterations cao**: 1M iterations cho PBKDF2
4. **Validation nghiêm ngặt**: 5 lớp kiểm tra
5. **Session timeout**: 24h

### ⚠️ Khuyến Nghị
1. **Backup định kỳ**: Backup bảng `logs_customuser`
2. **Monitor đăng nhập**: Log các lần đăng nhập
3. **Rate limiting**: Giới hạn số lần đăng nhập
4. **2FA**: Thêm xác thực 2 yếu tố nếu cần
5. **Audit log**: Ghi log các thay đổi quan trọng

## 🎯 Kết Luận

**Bảng chứa user/password**: `logs_customuser`

**Đặc điểm**:
- ✅ Mật khẩu được mã hóa an toàn
- ✅ Cấu trúc bảng chuẩn Django
- ✅ Validation đầy đủ
- ✅ Session management tốt
- ✅ 4 users hiện tại đều hoạt động

**Bảo mật**: Mức độ cao với PBKDF2-SHA256 và 1M iterations! 🛡️
