# Hệ Thống Logging Toàn Diện - SQL Log Analyzer

## 📋 Tổng Quan

Hệ thống logging được thiết kế tương tự như **log4j** để ghi lại tất cả các hoạt động của web application, bao gồm:

- ✅ **Tất cả HTTP requests/responses**
- ✅ **Hoạt động đăng nhập/đăng xuất**
- ✅ **Thao tác admin và phân quyền**
- ✅ **Sự kiện bảo mật**
- ✅ **Lỗi hệ thống**
- ✅ **Truy cập dữ liệu**

## 🗂️ Cấu Trúc Log Files

### 1. **Web Activity Log** (`logs/web_activity.log`)
```
[INFO] 2025-09-06 12:36:08,906 | REQUEST | GET /manage/ | User: admin (ID: 1) | IP: 127.0.0.1
[INFO] 2025-09-06 12:36:08,906 | RESPONSE | GET /manage/ | Status: 200 | Duration: 0.045s | User: admin (ID: 1)
[INFO] 2025-09-06 12:36:08,906 | USER_LOGIN_SUCCESS | User: admin (ID: 1) | IP: 127.0.0.1
[INFO] 2025-09-06 12:36:08,906 | DB_PERMISSION_CREATE | Admin: admin (ID: 1) | Permission ID: 5 | Database: T24VN
```

### 2. **Security Log** (`logs/security.log`)
```
[WARNING] 2025-09-06 12:36:08,891 | USER_LOGIN_FAILED | Username: hacker | Reason: Invalid credentials | IP: 192.168.1.100
[ERROR] 2025-09-06 12:36:08,891 | EXCEPTION | POST /admin/users/ | Exception: PermissionDenied | User: Anonymous | IP: 127.0.0.1
[WARNING] 2025-09-06 12:36:08,891 | SUSPICIOUS_REQUEST | GET /admin/script.php | IP: 192.168.1.100
```

### 3. **Django General Log** (`logs/django_general.log`)
```
[INFO] 2025-09-06 12:36:08,205 | logs | log_system_event:184 | SYSTEM_EVENT | DATABASE_BACKUP_COMPLETED
[INFO] 2025-09-06 12:36:08,205 | logs | admin_action:156 | ADMIN_ACTION | USER_CREATED | Details: Created user testuser
```

### 4. **Django Errors Log** (`logs/django_errors.log`)
```
[ERROR] 2025-09-06 12:36:08,205 | logs | view_function:45 | HTTP_ERROR | POST /api/logs/ | Status: 500 | User: admin
```

## 🔧 Cấu Hình Logging

### Settings Configuration (`log_analyzer/settings.py`)

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '[{levelname}] {asctime} | {name} | {funcName}:{lineno} | {message}',
            'style': '{',
        },
        'web_activity': {
            'format': '[{levelname}] {asctime} | {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file_web_activity': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/web_activity.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 10,
            'formatter': 'web_activity',
        },
        # ... other handlers
    },
    'loggers': {
        'web_activity': {
            'handlers': ['file_web_activity'],
            'level': 'INFO',
            'propagate': False,
        },
        # ... other loggers
    },
}
```

## 🛠️ Middleware Logging

### WebActivityLoggingMiddleware
- **Ghi log tất cả HTTP requests/responses**
- **Theo dõi thời gian xử lý**
- **Ghi log POST data (loại bỏ thông tin nhạy cảm)**
- **Ghi log lỗi HTTP**

### SecurityLoggingMiddleware
- **Phát hiện suspicious requests**
- **Ghi log các pattern đáng ngờ**
- **Theo dõi rate limiting**

## 📝 Activity Logger

### Sử Dụng ActivityLogger

```python
from logs.logging_utils import ActivityLogger

# Log đăng nhập
ActivityLogger.log_user_login(request, user, success=True)

# Log hoạt động admin
ActivityLogger.log_admin_action(request, "USER_CREATED", "Created user testuser")

# Log phân quyền database
ActivityLogger.log_database_permission_action(
    request, 'CREATE', permission_id, user_id, database_name
)

# Log sự kiện bảo mật
ActivityLogger.log_security_event(request, "SUSPICIOUS_LOGIN", "Multiple failed attempts")

# Log sự kiện hệ thống
ActivityLogger.log_system_event("DATABASE_BACKUP", "Backup completed successfully")
```

### Decorator cho Views

```python
from logs.logging_utils import log_view_activity

@log_view_activity("USER_MANAGEMENT")
def admin_user_list(request):
    # View code
    pass
```

## 🖥️ Log Viewer Interface

### Truy Cập Log Viewer
- **URL**: `/manage/logs/`
- **Yêu cầu**: Admin permissions
- **Tính năng**:
  - Xem logs theo loại
  - Tìm kiếm trong logs
  - Tải xuống log files
  - Xóa logs
  - Thống kê logs

### Tính Năng Log Viewer

#### 1. **Xem Logs**
- Chọn loại log (web_activity, security, django_general, django_errors)
- Phân trang (50 dòng/trang)
- Auto-refresh mỗi 30 giây

#### 2. **Tìm Kiếm**
- Tìm kiếm theo từ khóa
- Tìm kiếm trong nhiều loại log
- Hiển thị kết quả với số dòng

#### 3. **Tải Xuống**
- Tải xuống log files
- Tên file bao gồm timestamp
- Format: `{log_type}_{YYYYMMDD_HHMMSS}.log`

#### 4. **Xóa Logs**
- Xóa nội dung log files
- Tự động backup trước khi xóa
- Xác nhận trước khi xóa

#### 5. **Thống Kê**
- Kích thước từng loại log
- Số dòng trong mỗi file
- Tổng kích thước logs
- Trạng thái files

## 🔍 Các Loại Log Events

### 1. **Web Activity Events**
- `REQUEST` - HTTP request
- `RESPONSE` - HTTP response  
- `POST_DATA` - POST data (sanitized)
- `USER_LOGIN_SUCCESS` - Đăng nhập thành công
- `USER_LOGIN_FAILED` - Đăng nhập thất bại
- `USER_LOGOUT` - Đăng xuất
- `USER_REGISTRATION_SUCCESS` - Đăng ký thành công
- `USER_REGISTRATION_FAILED` - Đăng ký thất bại
- `PASSWORD_CHANGE_SUCCESS` - Đổi mật khẩu thành công
- `PASSWORD_CHANGE_FAILED` - Đổi mật khẩu thất bại

### 2. **Database Permission Events**
- `DB_PERMISSION_CREATE` - Tạo phân quyền
- `DB_PERMISSION_UPDATE` - Cập nhật phân quyền
- `DB_PERMISSION_DELETE` - Xóa phân quyền
- `DB_PERMISSION_ACTIVATE` - Kích hoạt phân quyền
- `DB_PERMISSION_DEACTIVATE` - Vô hiệu hóa phân quyền

### 3. **Admin Action Events**
- `ADMIN_ACTION` - Hoạt động admin
- `VIEW_ACCESS_*` - Truy cập view
- `VIEW_SUCCESS_*` - View thành công
- `VIEW_ERROR_*` - Lỗi view

### 4. **Security Events**
- `SECURITY_EVENT` - Sự kiện bảo mật
- `SUSPICIOUS_REQUEST` - Request đáng ngờ
- `HTTP_ERROR` - Lỗi HTTP
- `EXCEPTION` - Exception

### 5. **System Events**
- `SYSTEM_EVENT` - Sự kiện hệ thống
- `DATA_ACCESS` - Truy cập dữ liệu

## 📊 Log Rotation

### Cấu Hình Rotation
- **Kích thước tối đa**: 10MB per file
- **Số file backup**: 5-10 files tùy loại
- **Tự động rotation**: Khi đạt kích thước tối đa
- **Nén backup**: Không (có thể cấu hình)

### File Naming Convention
```
logs/web_activity.log          # File hiện tại
logs/web_activity.log.1        # Backup 1
logs/web_activity.log.2        # Backup 2
...
logs/web_activity.log.10       # Backup 10
```

## 🔒 Bảo Mật Logs

### Thông Tin Nhạy Cảm
- **Passwords**: Được thay thế bằng `[REDACTED]`
- **CSRF tokens**: Được thay thế bằng `[REDACTED]`
- **Secrets**: Được thay thế bằng `[REDACTED]`

### IP Address Tracking
- **Real IP**: Từ `HTTP_X_FORWARDED_FOR` header
- **Fallback**: `REMOTE_ADDR`
- **Privacy**: Có thể anonymize IP nếu cần

### Access Control
- **Log Viewer**: Chỉ admin mới truy cập được
- **Log Files**: Nằm ngoài web root
- **Permissions**: File permissions 600 (owner only)

## 🚀 Monitoring & Alerting

### Log Monitoring
- **File size monitoring**: Cảnh báo khi file quá lớn
- **Error rate monitoring**: Cảnh báo khi có nhiều lỗi
- **Security event monitoring**: Cảnh báo sự kiện bảo mật

### Integration với External Tools
- **ELK Stack**: Có thể export logs sang Elasticsearch
- **Splunk**: Có thể forward logs sang Splunk
- **Syslog**: Có thể forward sang syslog server

## 📈 Performance Impact

### Overhead
- **Minimal**: Logging có overhead rất thấp
- **Async**: Có thể implement async logging nếu cần
- **Buffering**: Logs được buffer để giảm I/O

### Optimization
- **Log level**: Chỉ log INFO và trên
- **File rotation**: Tránh file quá lớn
- **Cleanup**: Tự động xóa logs cũ

## 🛡️ Troubleshooting

### Common Issues

#### 1. **Log Files Không Được Tạo**
```bash
# Kiểm tra permissions
ls -la logs/
# Tạo thư mục nếu cần
mkdir -p logs/
chmod 755 logs/
```

#### 2. **Logs Không Hiển Thị**
- Kiểm tra Django settings
- Kiểm tra middleware configuration
- Kiểm tra logger configuration

#### 3. **Log Files Quá Lớn**
- Kiểm tra rotation settings
- Kiểm tra log level
- Xóa logs cũ thủ công

### Debug Commands
```python
# Test logging trong Django shell
python manage.py shell
>>> import logging
>>> logger = logging.getLogger('web_activity')
>>> logger.info('Test log message')
```

## 📚 Best Practices

### 1. **Log Levels**
- **DEBUG**: Thông tin debug chi tiết
- **INFO**: Thông tin hoạt động bình thường
- **WARNING**: Cảnh báo, không nghiêm trọng
- **ERROR**: Lỗi nghiêm trọng
- **CRITICAL**: Lỗi nghiêm trọng nhất

### 2. **Log Messages**
- **Structured**: Sử dụng format nhất quán
- **Contextual**: Bao gồm đủ thông tin context
- **Searchable**: Dễ tìm kiếm và filter

### 3. **Security**
- **Sanitize**: Loại bỏ thông tin nhạy cảm
- **Access Control**: Giới hạn truy cập logs
- **Retention**: Xóa logs cũ theo policy

### 4. **Performance**
- **Async**: Sử dụng async logging nếu cần
- **Buffering**: Buffer logs để giảm I/O
- **Rotation**: Rotate logs thường xuyên

## 🎯 Kết Luận

Hệ thống logging này cung cấp:

✅ **Truy vết hoàn chỉnh** tất cả hoạt động web  
✅ **Bảo mật cao** với sanitization  
✅ **Giao diện thân thiện** để xem logs  
✅ **Tự động rotation** để quản lý dung lượng  
✅ **Tích hợp sẵn** với Django application  
✅ **Mở rộng dễ dàng** cho các tính năng mới  

Hệ thống đã sẵn sàng sử dụng và có thể được mở rộng thêm theo nhu cầu cụ thể của dự án.
