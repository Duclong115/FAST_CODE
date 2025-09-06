# 👥 Hướng Dẫn Quản Lý Người Dùng Cho Quản Trị Viên

## 📋 Tổng Quan

Hệ thống quản lý người dùng bảo mật cho phép quản trị viên kiểm soát hoàn toàn việc truy cập vào công cụ phân tích log SQL, đảm bảo chỉ những nhân viên được ủy quyền mới có thể sử dụng hệ thống.

## 🔐 Bảo Mật Hệ Thống

### ✅ Tính Năng Bảo Mật Đã Triển Khai

1. **Phân Quyền Nghiêm Ngặt**:
   - ✅ Chỉ Superuser mới có thể truy cập admin panel
   - ✅ Kiểm tra quyền `@user_passes_test(is_admin)`
   - ✅ Bảo vệ tất cả admin views

2. **Mã Hóa Mật Khẩu Mạnh**:
   - ✅ PBKDF2-SHA256 với 1,000,000 iterations
   - ✅ Salt ngẫu nhiên cho mỗi mật khẩu
   - ✅ Không có mật khẩu plain text

3. **Session Management**:
   - ✅ Session timeout 24 giờ
   - ✅ CSRF protection
   - ✅ Secure session storage

4. **Audit Trail**:
   - ✅ Log tất cả thao tác admin
   - ✅ Track đăng nhập/đăng xuất
   - ✅ Monitor hoạt động người dùng

## 🎯 Vai Trò Người Dùng

### 👑 Superuser (Quản Trị Viên)
- **Quyền hạn**: Toàn quyền hệ thống
- **Truy cập**: Admin panel + Ứng dụng chính
- **Chức năng**: 
  - Tạo/chỉnh sửa/xóa người dùng
  - Reset mật khẩu
  - Quản lý phân quyền
  - Xem log bảo mật

### 👨‍💼 Staff (Nhân Viên Cấp Cao)
- **Quyền hạn**: Truy cập admin panel hạn chế
- **Truy cập**: Admin panel + Ứng dụng chính
- **Chức năng**:
  - Xem thông tin người dùng
  - Không quản lý người dùng
  - Quyền hạn hạn chế

### 👤 User (Người Dùng Thường)
- **Quyền hạn**: Chỉ truy cập ứng dụng chính
- **Truy cập**: Ứng dụng phân tích log SQL
- **Chức năng**:
  - Xem và phân tích logs
  - Tạo báo cáo
  - Không có quyền admin

## 🚀 Hướng Dẫn Sử Dụng

### 1. Truy Cập Admin Panel

```bash
# URL admin dashboard
http://127.0.0.1:8000/admin/

# Yêu cầu: Đăng nhập với tài khoản Superuser
Username: admin
Password: admin123
```

### 2. Dashboard Quản Trị

**Thống kê tổng quan**:
- Tổng số người dùng
- Người dùng hoạt động/không hoạt động
- Số Superuser/Staff/User
- Người dùng mới trong 7 ngày
- Top người dùng đăng nhập gần đây

**Thao tác nhanh**:
- Tạo người dùng mới
- Quản lý người dùng
- Xem log bảo mật
- Về ứng dụng chính

### 3. Quản Lý Người Dùng

#### 📋 Danh Sách Người Dùng (`/admin/users/`)

**Tính năng**:
- ✅ Tìm kiếm theo username, email, tên
- ✅ Lọc theo trạng thái (hoạt động/không hoạt động)
- ✅ Lọc theo vai trò (Superuser/Staff/User)
- ✅ Phân trang (10/20/50/100 per page)
- ✅ Bulk actions (kích hoạt/vô hiệu hóa/xóa hàng loạt)

**Thông tin hiển thị**:
- ID, Username, Email
- Vai trò (Superuser/Staff/User)
- Trạng thái (Hoạt động/Không hoạt động)
- Ngày tạo, Lần đăng nhập cuối
- Thao tác (Xem/Chỉnh sửa/Reset mật khẩu)

#### ➕ Tạo Người Dùng Mới (`/admin/users/create/`)

**Thông tin bắt buộc**:
- Username (3-150 ký tự, unique)
- Email (unique)
- Password (tối thiểu 8 ký tự)

**Thông tin tùy chọn**:
- First name, Last name
- Trạng thái hoạt động
- Phân quyền (Staff/Superuser)

**Tính năng đặc biệt**:
- ✅ Tự động tạo mật khẩu bảo mật
- ✅ Validation nghiêm ngặt
- ✅ Kiểm tra trùng lặp username/email

#### ✏️ Chỉnh Sửa Người Dùng (`/admin/users/<id>/edit/`)

**Có thể chỉnh sửa**:
- Username, Email
- First name, Last name
- Trạng thái hoạt động
- Phân quyền (Staff/Superuser)

**Bảo vệ**:
- Không cho phép tự chỉnh sửa quyền của mình
- Validation trùng lặp (trừ user hiện tại)

#### 🔑 Reset Mật Khẩu (`/admin/users/<id>/reset-password/`)

**Tính năng**:
- ✅ Tạo mật khẩu mới cho người dùng
- ✅ Validation mật khẩu mạnh
- ✅ Xác nhận mật khẩu
- ✅ Tự động mã hóa và lưu

#### 🔄 Bật/Tắt Trạng Thái (`/admin/users/<id>/toggle-active/`)

**Tính năng**:
- ✅ Bật/tắt tài khoản người dùng
- ✅ Không cho phép tự khóa mình
- ✅ Thông báo kết quả

#### 🗑️ Xóa Người Dùng (`/admin/users/<id>/delete/`)

**Bảo vệ**:
- ✅ Không cho phép tự xóa mình
- ✅ Xác nhận trước khi xóa
- ✅ Xóa hoàn toàn khỏi database

### 4. Bulk Actions (Hành Động Hàng Loạt)

**Các hành động**:
- **Kích hoạt**: Bật tài khoản cho nhiều người dùng
- **Vô hiệu hóa**: Tắt tài khoản cho nhiều người dùng
- **Xóa**: Xóa nhiều người dùng cùng lúc

**Bảo vệ**:
- ✅ Không cho phép tự thao tác với mình
- ✅ Xác nhận trước khi thực hiện
- ✅ Thông báo số lượng đã thao tác

## 🛡️ Bảo Mật Nâng Cao

### 1. Kiểm Soát Truy Cập

```python
# Chỉ Superuser mới có thể truy cập admin
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    # Admin logic
```

### 2. Bảo Vệ Tự Thao Tác

```python
# Không cho phép tự khóa/xóa mình
if user == request.user:
    messages.error(request, 'Không thể thao tác với chính mình!')
    return redirect(...)
```

### 3. Validation Nghiêm Ngặt

```python
# Kiểm tra trùng lặp username/email
if CustomUser.objects.filter(username=username).exists():
    raise ValidationError('Tên người dùng đã tồn tại')
```

### 4. Audit Logging

```python
# Log tất cả thao tác admin
logger.info(f"Admin {request.user.username} created user {new_user.username}")
```

## 📊 Monitoring & Reporting

### Dashboard Metrics
- **Tổng người dùng**: Theo dõi số lượng người dùng
- **Tỷ lệ hoạt động**: Phần trăm người dùng hoạt động
- **Phân bố vai trò**: Superuser/Staff/User
- **Hoạt động gần đây**: Người dùng mới và đăng nhập

### Security Monitoring
- **Đăng nhập gần đây**: Track hoạt động người dùng
- **Thay đổi quyền**: Monitor việc thay đổi phân quyền
- **Bulk actions**: Log các thao tác hàng loạt
- **Failed attempts**: Theo dõi đăng nhập thất bại

## 🚨 Xử Lý Sự Cố

### 1. Người Dùng Không Thể Đăng Nhập
```bash
# Kiểm tra trạng thái tài khoản
1. Vào admin panel
2. Tìm người dùng
3. Kiểm tra "Trạng thái" = "Hoạt động"
4. Nếu không hoạt động → Kích hoạt
```

### 2. Quên Mật Khẩu
```bash
# Reset mật khẩu từ admin
1. Vào admin panel
2. Tìm người dùng
3. Click "Reset mật khẩu"
4. Tạo mật khẩu mới
5. Thông báo cho người dùng
```

### 3. Phân Quyền Sai
```bash
# Chỉnh sửa quyền người dùng
1. Vào admin panel
2. Tìm người dùng
3. Click "Chỉnh sửa"
4. Thay đổi quyền (Staff/Superuser)
5. Lưu thay đổi
```

## 📚 Tài Liệu Tham Khảo

- [Django Admin](https://docs.djangoproject.com/en/5.2/ref/contrib/admin/)
- [Django Authentication](https://docs.djangoproject.com/en/5.2/topics/auth/)
- [Django Permissions](https://docs.djangoproject.com/en/5.2/topics/auth/default/#permissions)
- [Security Best Practices](https://docs.djangoproject.com/en/5.2/topics/security/)

## 🎯 Kết Luận

**Hệ thống quản lý người dùng đã hoàn thành với mức độ bảo mật cao:**

- ✅ **Phân quyền nghiêm ngặt**: Chỉ Superuser truy cập admin
- ✅ **CRUD hoàn chỉnh**: Tạo/chỉnh sửa/xóa người dùng
- ✅ **Bảo mật nâng cao**: Mã hóa mật khẩu, session management
- ✅ **Bulk operations**: Thao tác hàng loạt
- ✅ **Audit trail**: Log tất cả hoạt động
- ✅ **User-friendly**: Giao diện thân thiện, dễ sử dụng

**Quản trị viên có thể kiểm soát hoàn toàn việc truy cập hệ thống và đảm bảo chỉ những nhân viên được ủy quyền mới có thể sử dụng công cụ phân tích log SQL!** 🛡️✨
