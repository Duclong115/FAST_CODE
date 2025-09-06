# 🗄️ Hướng Dẫn Phân Quyền Database

## 📋 Tổng Quan

Hệ thống phân quyền database cho phép quản trị viên kiểm soát chính xác việc truy cập logs của từng database cụ thể, đảm bảo chỉ những nhân viên được ủy quyền mới có thể xem và thao tác với dữ liệu nhạy cảm.

## 🔐 Tính Năng Bảo Mật

### ✅ Phân Quyền Theo Database
- **Kiểm soát chính xác**: Chỉ user được cấp quyền mới có thể truy cập database cụ thể
- **3 cấp độ quyền**: Read, Write, Admin
- **Quản lý thời hạn**: Có thể đặt thời gian hết hạn cho quyền
- **Audit trail**: Theo dõi ai cấp quyền, khi nào, cho ai

### ✅ Bảo Mật Nâng Cao
- **Superuser bypass**: Admin có thể truy cập tất cả database
- **Permission validation**: Kiểm tra quyền trước mỗi truy cập
- **Expired permission check**: Tự động kiểm tra quyền hết hạn
- **Unique constraint**: Mỗi user chỉ có 1 quyền cho 1 database

## 🎯 Cấp Độ Phân Quyền

### 📖 Read (Chỉ Đọc)
- **Quyền hạn**: Xem logs của database
- **Chức năng**:
  - Xem danh sách logs
  - Tạo báo cáo
  - Xuất dữ liệu
- **Hạn chế**: Không thể chỉnh sửa hoặc xóa

### ✏️ Write (Đọc và Ghi)
- **Quyền hạn**: Tất cả quyền Read + chỉnh sửa
- **Chức năng**:
  - Tất cả quyền Read
  - Import logs mới
  - Chỉnh sửa logs hiện có
- **Hạn chế**: Không thể xóa hoặc quản lý database

### 👑 Admin (Quản Trị)
- **Quyền hạn**: Toàn quyền với database
- **Chức năng**:
  - Tất cả quyền Write
  - Xóa logs
  - Quản lý cấu hình database
  - Cấp quyền cho user khác (nếu được ủy quyền)

## 🚀 Hướng Dẫn Sử Dụng

### 1. Quản Trị Viên - Cấp Quyền Database

#### 📋 Truy Cập Quản Lý Phân Quyền
```bash
# URL quản lý phân quyền database
http://127.0.0.1:8000/admin/database-permissions/

# Yêu cầu: Đăng nhập với tài khoản Superuser
Username: admin
Password: admin123
```

#### ➕ Tạo Phân Quyền Mới
1. **Truy cập**: Admin Panel → Phân Quyền Database → Tạo Mới
2. **Điền thông tin**:
   - **Người dùng**: Chọn user cần cấp quyền
   - **Database**: Tên database (VD: T24VN, WAY4, EBANK)
   - **Loại quyền**: Read/Write/Admin
   - **Hết hạn**: Thời gian hết hạn (tùy chọn)
   - **Ghi chú**: Mô tả lý do cấp quyền

3. **Lưu**: Click "Cấp Quyền Database"

#### ✏️ Chỉnh Sửa Phân Quyền
1. **Tìm phân quyền**: Sử dụng tìm kiếm hoặc filter
2. **Chỉnh sửa**: Click "Chỉnh sửa" trên phân quyền cần sửa
3. **Thay đổi**: Cập nhật loại quyền, thời hạn, trạng thái
4. **Lưu**: Click "Cập Nhật Phân Quyền"

#### 🔄 Quản Lý Hàng Loạt
- **Kích hoạt**: Bật nhiều phân quyền cùng lúc
- **Vô hiệu hóa**: Tắt nhiều phân quyền cùng lúc
- **Xóa**: Xóa nhiều phân quyền cùng lúc

### 2. Người Dùng - Xem Phân Quyền Của Mình

#### 👤 Truy Cập Phân Quyền Cá Nhân
```bash
# URL xem phân quyền của user
http://127.0.0.1:8000/my-database-permissions/

# Hoặc từ menu: User dropdown → Phân quyền Database
```

#### 📊 Thông Tin Hiển Thị
- **Thống kê tổng quan**: Tổng quyền, quyền hoạt động, hết hạn
- **Database có thể truy cập**: Danh sách database với nút truy cập
- **Chi tiết phân quyền**: Bảng chi tiết tất cả quyền
- **Hướng dẫn**: Giải thích các loại quyền

### 3. Sử Dụng Phân Quyền Trong Ứng Dụng

#### 🔍 Xem Logs Theo Database
1. **Truy cập trang chủ**: http://127.0.0.1:8000/
2. **Chọn database**: Từ dropdown filter
3. **Kiểm tra quyền**: Hệ thống tự động kiểm tra quyền truy cập
4. **Hiển thị logs**: Chỉ hiển thị logs của database có quyền

#### ⚠️ Xử Lý Không Có Quyền
- **Thông báo lỗi**: "Bạn không có quyền truy cập database X"
- **Chuyển hướng**: Về trang chủ hoặc trang phù hợp
- **Gợi ý**: Liên hệ quản trị viên để được cấp quyền

## 🛡️ Bảo Mật và Kiểm Soát

### 1. Kiểm Tra Quyền Tự Động
```python
# Trong views, hệ thống tự động kiểm tra
if database_filter and not request.user.has_database_permission(database_filter):
    messages.error(request, f'Bạn không có quyền truy cập database "{database_filter}"!')
    database_filter = ''
```

### 2. Filter Database Theo Quyền
```python
# Chỉ hiển thị database user có quyền truy cập
if request.user.is_superuser:
    databases = SqlLog.objects.values_list('database_name', flat=True).distinct()
else:
    databases = request.user.get_accessible_databases()
```

### 3. Decorator Kiểm Tra Quyền
```python
# Có thể sử dụng decorator để bảo vệ views
@require_database_permission('read')
def view_logs(request, database_name):
    # Logic xem logs
```

## 📊 Monitoring và Báo Cáo

### Dashboard Admin
- **Tổng phân quyền**: Số lượng phân quyền đã cấp
- **Phân quyền hoạt động**: Số phân quyền đang có hiệu lực
- **Phân quyền hết hạn**: Số phân quyền đã hết hạn
- **Phân bố theo database**: Số user có quyền với mỗi database

### Thống Kê Chi Tiết
- **Theo user**: Số phân quyền của mỗi user
- **Theo database**: Số user có quyền với mỗi database
- **Theo loại quyền**: Phân bố Read/Write/Admin
- **Theo thời gian**: Phân quyền được cấp gần đây

## 🚨 Xử Lý Sự Cố

### 1. User Không Thể Truy Cập Database
```bash
# Kiểm tra và khắc phục
1. Vào admin panel → Phân quyền Database
2. Tìm user và database
3. Kiểm tra trạng thái quyền
4. Nếu không có → Tạo quyền mới
5. Nếu có nhưng không hoạt động → Kích hoạt
6. Nếu hết hạn → Gia hạn hoặc tạo mới
```

### 2. Phân Quyền Không Hoạt Động
```bash
# Kiểm tra nguyên nhân
1. Kiểm tra is_active = True
2. Kiểm tra expires_at (nếu có)
3. Kiểm tra database_name chính xác
4. Kiểm tra user.is_active = True
```

### 3. Superuser Không Thể Truy Cập
```bash
# Kiểm tra quyền superuser
1. Đảm bảo user.is_superuser = True
2. Đảm bảo user.is_active = True
3. Đăng nhập lại để refresh session
```

## 📚 API và Methods

### User Methods
```python
# Kiểm tra quyền database
user.has_database_permission(database_name, permission_type='read')

# Lấy danh sách database có thể truy cập
user.get_accessible_databases()

# Lấy tất cả phân quyền của user
user.get_database_permissions()
```

### Permission Model Methods
```python
# Kiểm tra quyền hết hạn
permission.is_expired()

# Kiểm tra quyền hợp lệ
permission.is_valid()
```

## 🎯 Best Practices

### 1. Cấp Quyền
- **Nguyên tắc tối thiểu**: Chỉ cấp quyền cần thiết
- **Thời hạn hợp lý**: Đặt thời hạn cho quyền tạm thời
- **Ghi chú rõ ràng**: Mô tả lý do cấp quyền
- **Review định kỳ**: Kiểm tra và thu hồi quyền không cần thiết

### 2. Quản Lý Database
- **Đặt tên chuẩn**: Sử dụng tên database nhất quán
- **Phân loại**: Nhóm database theo mức độ nhạy cảm
- **Backup**: Sao lưu danh sách phân quyền
- **Monitoring**: Theo dõi hoạt động truy cập

### 3. Bảo Mật
- **Audit log**: Ghi lại mọi thay đổi phân quyền
- **Regular review**: Kiểm tra phân quyền định kỳ
- **Incident response**: Quy trình xử lý vi phạm
- **Training**: Đào tạo user về phân quyền

## 🎉 Kết Luận

**Hệ thống phân quyền database đã hoàn thành với mức độ bảo mật cao:**

- ✅ **Kiểm soát chính xác**: Chỉ user được ủy quyền mới truy cập database cụ thể
- ✅ **3 cấp độ quyền**: Read, Write, Admin với chức năng rõ ràng
- ✅ **Quản lý thời hạn**: Có thể đặt thời gian hết hạn cho quyền
- ✅ **Audit trail**: Theo dõi đầy đủ việc cấp và sử dụng quyền
- ✅ **User-friendly**: Giao diện thân thiện cho cả admin và user
- ✅ **Bảo mật nâng cao**: Kiểm tra quyền tự động, không thể bypass

**Quản trị viên có thể kiểm soát hoàn toàn việc truy cập logs của từng database, đảm bảo chỉ những nhân viên được ủy quyền mới có thể xem dữ liệu nhạy cảm!** 🛡️✨
