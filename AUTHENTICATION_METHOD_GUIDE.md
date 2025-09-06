# 🔐 Hướng Dẫn Phương Thức Xác Thực

## 📋 Tổng Quan

Hệ thống SQL Log Analyzer sử dụng **Session-based Authentication**, không sử dụng JWT token.

## 🎯 Phương Thức Xác Thực

### ✅ **SESSION-BASED AUTHENTICATION**

**Đặc điểm**:
- ✅ Sử dụng Django's built-in session system
- ✅ Session được lưu trong database
- ✅ Session timeout: 24 giờ
- ✅ CSRF protection enabled
- ❌ Không sử dụng JWT token

## 🔧 Cấu Hình Chi Tiết

### 1. Authentication Backend
```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend'
]
```

### 2. Session Settings
```python
# Session engine
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Session timeout
SESSION_COOKIE_AGE = 86400  # 24 hours

# Session behavior
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
```

### 3. Middleware
```python
MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # ... other middleware
]
```

## 🗄️ Session Storage

### Database Storage
- **Table**: `django_session`
- **Engine**: `django.contrib.sessions.backends.db`
- **Format**: Encrypted session data

### Session Structure
```sql
CREATE TABLE django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date TIMESTAMP WITH TIME ZONE NOT NULL
);
```

### Session Data Example
```
Session Key: 3oximpothl41lhzgqwff9eq85ufo5skz
Session Data: .eJxVjEEOgjAQRe_StWko09YZl-45A5nOVIsaSCisjHcXEha6_e-9_zY9r0vp15rnflBzMdGcfrfE8szjDvTB432yMo3LPCS7K_a...
Expire Date: 2025-09-07 04:32:03.912818+00:00
```

## 🔄 Luồng Xác Thực

### 1. Đăng Nhập
```
User submits login form → 
Django authenticates credentials → 
Creates session in database → 
Sets session cookie → 
Redirects to protected page
```

### 2. Truy Cập Trang Được Bảo Vệ
```
User requests protected page → 
Django checks session cookie → 
Validates session in database → 
Allows/denies access
```

### 3. Đăng Xuất
```
User clicks logout → 
Django destroys session → 
Removes session from database → 
Redirects to login page
```

## 🛡️ Bảo Mật Session

### ✅ Đã Triển Khai

1. **Session Encryption**: Session data được mã hóa
2. **CSRF Protection**: Bảo vệ chống tấn công CSRF
3. **Session Timeout**: 24 giờ tự động hết hạn
4. **Secure Cookies**: Sẵn sàng cho HTTPS
5. **Session Validation**: Kiểm tra session trong database

### 🔒 Session Security Features

```python
# CSRF protection
CSRF_COOKIE_SECURE = True  # For production
CSRF_COOKIE_HTTPONLY = True

# Session security
SESSION_COOKIE_SECURE = True  # For production
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

## 📊 So Sánh Session vs JWT

| Đặc Điểm | Session-based | JWT Token |
|----------|---------------|-----------|
| **Storage** | Server-side (Database) | Client-side (LocalStorage/Cookie) |
| **Security** | ✅ High (Server validation) | ⚠️ Medium (Client validation) |
| **Scalability** | ⚠️ Requires shared storage | ✅ Stateless |
| **Revocation** | ✅ Easy (Delete session) | ❌ Difficult (Blacklist) |
| **Size** | ✅ Small (Session ID only) | ❌ Large (Full payload) |
| **Performance** | ⚠️ Database lookup | ✅ No database lookup |
| **Django Support** | ✅ Built-in | ❌ Requires third-party |

## 🚀 Ưu Điểm Session-based

### ✅ Bảo Mật Cao
- Session data được lưu trên server
- Không thể bị giả mạo từ client
- Dễ dàng revoke session

### ✅ Django Native
- Tích hợp sẵn với Django
- Không cần thư viện bổ sung
- Hỗ trợ đầy đủ các tính năng

### ✅ CSRF Protection
- Django tự động bảo vệ CSRF
- Session-based CSRF tokens
- Không cần cấu hình thêm

## ⚠️ Nhược Điểm Session-based

### ❌ Scalability
- Cần shared storage cho multiple servers
- Database lookup cho mỗi request
- Có thể bottleneck với high traffic

### ❌ Stateless
- Không stateless như JWT
- Phụ thuộc vào server state
- Khó scale horizontally

## 🔧 Cấu Hình Production

### Database Session với Redis
```python
# settings.py
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Session Security
```python
# Production settings
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
SESSION_COOKIE_AGE = 3600  # 1 hour for production
```

## 🧪 Test Session

### Kiểm Tra Session
```python
# Test session creation
from django.test import Client
client = Client()
client.login(username='testuser', password='test123')

# Check session
session_key = client.session.session_key
print(f"Session key: {session_key}")

# Check database
from django.contrib.sessions.models import Session
session = Session.objects.get(session_key=session_key)
print(f"Session data: {session.session_data}")
```

### Monitor Sessions
```python
# Count active sessions
from django.contrib.sessions.models import Session
from django.utils import timezone

active_sessions = Session.objects.filter(
    expire_date__gt=timezone.now()
).count()
print(f"Active sessions: {active_sessions}")
```

## 📚 Tài Liệu Tham Khảo

- [Django Sessions](https://docs.djangoproject.com/en/5.2/topics/http/sessions/)
- [Django Authentication](https://docs.djangoproject.com/en/5.2/topics/auth/)
- [Session vs JWT](https://auth0.com/blog/a-look-at-the-latest-draft-for-jwt-bcp/)
- [Django Security](https://docs.djangoproject.com/en/5.2/topics/security/)

## 🎯 Kết Luận

**Hệ thống sử dụng SESSION-BASED AUTHENTICATION**

**Đặc điểm**:
- ✅ Session lưu trong database
- ✅ Timeout 24 giờ
- ✅ CSRF protection
- ✅ Bảo mật cao
- ❌ Không sử dụng JWT

**Phù hợp cho**: Ứng dụng web truyền thống, không cần scale horizontally lớn, ưu tiên bảo mật.

**Không phù hợp cho**: API services, microservices, ứng dụng cần scale lớn.
