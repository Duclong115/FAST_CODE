# Test Tính Năng Xử Lý Lỗi Định Dạng Trong File Log

## 🎯 Mục đích
Test tính năng xử lý lỗi khi có dòng trong file log không theo định dạng chuẩn và hiển thị chi tiết lỗi trên trang log files.

## 📊 File Test: `test_log_with_errors.log`

### Thống kê tổng quan:
- **Tổng số dòng**: 28
- **Đã xử lý thành công**: 20 dòng (71.43%)
- **Số dòng lỗi**: 8 dòng (28.57%)
- **Thời gian xử lý**: 0.038 giây

### Các dòng đúng định dạng (20 dòng):
```
DB:T24VN,sql:SELECT * FROM accounts WHERE balance > 1000000,exec_time_ms:1100,exec_count:125
DB:WAY4,sql:SELECT * FROM customers WHERE cust_id = 203,exec_time_ms:5005,exec_count:150
DB:EBANK,sql:SELECT * FROM transactions WHERE amount > 50000,exec_time_ms:800,exec_count:200
...
```

### Các dòng sai định dạng (8 dòng):

1. **Dòng 6**: `INVALID_LINE_WITHOUT_PREFIX`
   - **Lỗi**: Không có prefix "DB:"

2. **Dòng 8**: `MISSING_COMMA_BETWEEN_FIELDS DB:T24VN sql:SELECT * FROM users exec_time_ms:200 exec_count:30`
   - **Lỗi**: Thiếu dấu phẩy giữa các trường

3. **Dòng 11**: `WRONG_FORMAT:database=T24VN,query=SELECT * FROM logs,time=150,count:25`
   - **Lỗi**: Định dạng hoàn toàn khác

4. **Dòng 14**: `EMPTY_LINE_WITH_SPACES    `
   - **Lỗi**: Dòng trống chỉ có khoảng trắng

5. **Dòng 17**: `MISSING_EXEC_COUNT DB:T24VN,sql:SELECT * FROM audit_log,exec_time_ms:250`
   - **Lỗi**: Thiếu trường exec_count

6. **Dòng 20**: `INVALID_CHARACTERS_IN_TIME DB:T24VN,sql:SELECT * FROM test,exec_time_ms:abc,exec_count:10`
   - **Lỗi**: exec_time_ms chứa ký tự không phải số

7. **Dòng 23**: `MISSING_SQL_PREFIX DB:T24VN,SELECT * FROM products,exec_time_ms:180,exec_count:40`
   - **Lỗi**: Thiếu prefix "sql:" trước câu SQL

8. **Dòng 26**: `WRONG_ORDER DB:T24VN,exec_time_ms:160,sql:SELECT * FROM orders,exec_count:35`
   - **Lỗi**: Thứ tự các trường không đúng

## 🌐 Test Cases

### 1. Import file log có lỗi
**Command**: `python manage.py import_logs test_log_with_errors.log --clear-existing`
**Kết quả mong đợi**: 
- Hiển thị cảnh báo cho 10 lỗi đầu tiên
- Tiếp tục xử lý các dòng khác
- Lưu chi tiết lỗi vào database

### 2. Truy cập trang Log Files
**URL**: http://127.0.0.1:8000/log-files/
**Kết quả mong đợi**: 
- Hiển thị file `test_log_with_errors.log`
- Cột "Chi tiết lỗi" có nút "Xem lỗi" màu vàng
- Tỷ lệ thành công: 71.43%

### 3. Xem chi tiết lỗi
**Action**: Click nút "Xem lỗi" trong bảng
**Kết quả mong đợi**: 
- Modal hiển thị với header màu vàng
- Tổng số dòng lỗi: 8
- Danh sách chi tiết các dòng lỗi
- Ghi chú về định dạng chuẩn

### 4. Kiểm tra dữ liệu đã lưu
**Database**: 20 logs được lưu thành công
**Thống kê theo Database**:
- **EBANK**: 5 logs
- **WAY4**: 5 logs  
- **T24VN**: 4 logs
- **MICRO**: 4 logs
- **BIZ**: 1 log
- **SALE**: 1 log

## 🎨 Tính năng Giao diện

### 1. Trang Log Files
- **Cột mới**: "Chi tiết lỗi"
- **Nút "Xem lỗi"**: Màu vàng với icon cảnh báo
- **Trạng thái "Không có lỗi"**: Màu xanh với icon check

### 2. Modal Chi tiết lỗi
- **Header**: Màu vàng với icon cảnh báo
- **Thông tin tổng quan**: Số dòng lỗi và tỷ lệ thành công
- **Danh sách lỗi**: Scrollable với font monospace
- **Ghi chú**: Định dạng chuẩn được yêu cầu

### 3. Xử lý lỗi trong Management Command
- **Hiển thị cảnh báo**: 10 lỗi đầu tiên trong console
- **Tiếp tục xử lý**: Không dừng khi gặp lỗi
- **Lưu chi tiết**: Tất cả lỗi được lưu vào database

## 🔧 Scripts Test

### Test tính năng xử lý lỗi:
```bash
python test_error_handling.py
```

### Import file log có lỗi:
```bash
python manage.py import_logs test_log_with_errors.log --clear-existing
```

### Test kết nối PostgreSQL:
```bash
python test_postgres.py
```

## 📝 Ghi chú

### Định dạng chuẩn:
```
DB:database_name,sql:SQL_query,exec_time_ms:time,exec_count:count
```

### Các loại lỗi được phát hiện:
1. **Thiếu prefix**: Không có "DB:" ở đầu
2. **Thiếu dấu phẩy**: Giữa các trường
3. **Định dạng sai**: Hoàn toàn khác format chuẩn
4. **Dòng trống**: Chỉ có khoảng trắng
5. **Thiếu trường**: Thiếu exec_count hoặc sql:
6. **Kiểu dữ liệu sai**: exec_time_ms không phải số
7. **Thứ tự sai**: Các trường không đúng thứ tự

### Tính năng:
- ✅ **Tiếp tục xử lý**: Không dừng khi gặp lỗi
- ✅ **Ghi chi tiết lỗi**: Lưu tất cả lỗi vào database
- ✅ **Hiển thị trên web**: Modal với thông tin chi tiết
- ✅ **Thống kê tổng quan**: Tỷ lệ thành công/thất bại
- ✅ **Giao diện thân thiện**: Bootstrap 5 với màu sắc phân loại
