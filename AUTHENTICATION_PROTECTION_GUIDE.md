# 🔒 Hướng Dẫn Bảo Vệ Trang Bằng Authentication

## 📋 Tổng Quan

Tất cả các trang chính của hệ thống đã được bảo vệ bằng `@login_required` decorator. Người dùng phải đăng nhập để truy cập các trang này.

## 🛡️ Các Trang Được Bảo Vệ

### ✅ Trang Chính (Yêu Cầu Đăng Nhập)

1. **Trang chủ** (`/`)
   - Hiển thị danh sách SQL logs
   - Có phân trang và filter theo database

2. **Thống kê** (`/statistics/`)
   - Thống kê tổng quan về logs
   - Biểu đồ và số liệu chi tiết

3. **File Logs** (`/log-files/`)
   - Danh sách các file log đã xử lý
   - Thông tin chi tiết về quá trình import

4. **Truy vấn bất thường** (`/abnormal-queries/`)
   - Danh sách các truy vấn có vấn đề
   - Gợi ý tối ưu hóa SQL

5. **Tạo báo cáo** (`/generate-report/`)
   - Form tạo báo cáo CSV/PDF
   - Xuất dữ liệu thống kê

6. **API Logs** (`/api/logs/`)
   - Endpoint JSON để lấy dữ liệu logs
   - Hỗ trợ phân trang và filter

### 🌐 Trang Công Khai (Không Cần Đăng Nhập)

1. **Đăng nhập** (`/auth/login/`)
   - Form đăng nhập
   - Xác thực username/password

2. **Đăng ký** (`/auth/register/`)
   - Form đăng ký tài khoản mới
   - Validation mật khẩu mạnh

3. **Yêu cầu đăng nhập** (`/auth/required/`)
   - Thông báo yêu cầu đăng nhập
   - Link đến trang đăng nhập/đăng ký

## 🔧 Cách Hoạt Động

### 1. Khi Chưa Đăng Nhập

```python
# Khi truy cập trang được bảo vệ
@login_required
def index(request):
    # Code view
```

**Hành vi**:
- Django tự động redirect đến `/auth/login/`
- URL gốc được lưu trong parameter `next`
- Sau khi đăng nhập thành công, redirect về URL gốc

### 2. Khi Đã Đăng Nhập

```python
# Kiểm tra trong template
{% if user.is_authenticated %}
    <p>Chào mừng {{ user.username }}!</p>
{% else %}
    <a href="{% url 'logs:login' %}">Đăng nhập</a>
{% endif %}
```

**Hành vi**:
- Có thể truy cập tất cả các trang
- Thông tin user hiển thị trong navbar
- Có thể đăng xuất

### 3. Khi Đăng Xuất

```python
@login_required
def logout_view(request):
    logout(request)
    return redirect('logs:login')
```

**Hành vi**:
- Session bị hủy
- Redirect về trang đăng nhập
- Không thể truy cập các trang được bảo vệ

## 🎯 Test Kết Quả

### ✅ Các Trang Được Bảo Vệ
- ✅ `/` → Redirect đến login
- ✅ `/statistics/` → Redirect đến login  
- ✅ `/log-files/` → Redirect đến login
- ✅ `/abnormal-queries/` → Redirect đến login
- ✅ `/generate-report/` → Redirect đến login
- ✅ `/api/logs/` → Redirect đến login

### ✅ Các Trang Công Khai
- ✅ `/auth/login/` → Accessible
- ✅ `/auth/register/` → Accessible
- ✅ `/auth/required/` → Accessible

### ✅ Luồng Đăng Nhập
- ✅ Login successful → Có thể truy cập tất cả trang
- ✅ Logout successful → Redirect về login
- ✅ Sau logout → Các trang được bảo vệ redirect đến login

## 🚀 Cách Sử Dụng

### 1. Truy Cập Khi Chưa Đăng Nhập

```bash
# Truy cập trang chủ
http://127.0.0.1:8000/

# Sẽ được redirect đến
http://127.0.0.1:8000/auth/login/?next=/
```

### 2. Đăng Nhập

```bash
# Truy cập trang đăng nhập
http://127.0.0.1:8000/auth/login/

# Tài khoản test
Username: testuser
Password: test123
```

### 3. Truy Cập Sau Khi Đăng Nhập

```bash
# Có thể truy cập tất cả trang
http://127.0.0.1:8000/
http://127.0.0.1:8000/statistics/
http://127.0.0.1:8000/log-files/
http://127.0.0.1:8000/abnormal-queries/
http://127.0.0.1:8000/generate-report/
```

### 4. Đăng Xuất

```bash
# Truy cập logout
http://127.0.0.1:8000/auth/logout/

# Hoặc click nút "Đăng xuất" trong navbar
```

## 🔧 Cấu Hình

### Settings.py

```python
# Login/Logout URLs
LOGIN_URL = '/auth/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/auth/login/'

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# Allowed hosts for testing
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'testserver']
```

### Views.py

```python
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    # View code
    pass

@login_required  
def statistics(request):
    # View code
    pass

# ... các views khác
```

## 🛡️ Bảo Mật

### ✅ Đã Triển Khai

1. **Authentication Required**: Tất cả trang chính yêu cầu đăng nhập
2. **Session Management**: Session timeout 24h
3. **CSRF Protection**: Bảo vệ chống tấn công CSRF
4. **Password Security**: Mật khẩu được mã hóa mạnh
5. **Redirect Security**: Redirect an toàn sau đăng nhập

### 🔒 Luồng Bảo Mật

```
User truy cập trang → Kiểm tra authentication → 
├─ Đã đăng nhập: Cho phép truy cập
└─ Chưa đăng nhập: Redirect đến login → 
   Đăng nhập thành công → Redirect về trang gốc
```

## 📚 Tài Liệu Tham Khảo

- [Django Authentication](https://docs.djangoproject.com/en/5.2/topics/auth/)
- [Django Login Required](https://docs.djangoproject.com/en/5.2/topics/auth/default/#the-login-required-decorator)
- [Django Sessions](https://docs.djangoproject.com/en/5.2/topics/http/sessions/)

## 🎯 Kết Luận

Hệ thống đã được bảo vệ hoàn toàn:

- ✅ **Tất cả trang chính yêu cầu đăng nhập**
- ✅ **Redirect tự động đến login khi chưa đăng nhập**
- ✅ **Session management an toàn**
- ✅ **CSRF protection đầy đủ**
- ✅ **Test thành công 100%**

**Bảo mật trang web đã hoàn thành!** 🔒✨
