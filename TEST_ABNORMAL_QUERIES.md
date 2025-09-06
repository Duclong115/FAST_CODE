# Test Tính Năng Quét Truy Vấn Bất Thường

## 🎯 Mục đích
Test tính năng "Quét Truy Vấn Bất Thường" với quy tắc: **exec_time_ms > 500 VÀ exec_count > 100**

## 📊 Quy tắc phát hiện
- **Thời gian thực thi > 500ms** VÀ **Số lần thực thi > 100**
- Các truy vấn này có thể gây tải cao cho hệ thống và cần được kiểm tra

## 🧪 Kết quả Test

### Thống kê tổng quan:
- **Tổng số logs**: 301
- **Truy vấn bất thường**: 4 (1.33%)
- **Truy vấn bình thường**: 297 (98.67%)

### Danh sách truy vấn bất thường:

1. **WAY4** - `SELECT * FROM customers WHERE cust_id = 203`
   - Thời gian: **5005 ms** ⚠️
   - Số lần thực thi: **150**
   - Thời gian TB: 33.37 ms

2. **T24VN** - `SELECT * FROM action_log WHERE action_id = 32`
   - Thời gian: **2000 ms** ⚠️
   - Số lần thực thi: **105**
   - Thời gian TB: 19.05 ms

3. **T24VN** - `SELECT * FROM accounts WHERE balance > 1000000`
   - Thời gian: **1100 ms** ⚠️
   - Số lần thực thi: **125**
   - Thời gian TB: 8.80 ms

4. **MICRO** - `SELECT * FROM trans_log_103 Create_date > sysdate -1`
   - Thời gian: **504 ms** ⚠️
   - Số lần thực thi: **103**
   - Thời gian TB: 4.89 ms

## 🌐 Test Cases

### 1. Truy cập trang Abnormal Queries
**URL**: http://127.0.0.1:8000/abnormal-queries/
**Kết quả mong đợi**: 
- Hiển thị 4 truy vấn bất thường
- Thống kê tổng quan với tỷ lệ 1.33%
- Phân loại mức độ nghiêm trọng

### 2. Lọc theo Database
**URL**: http://127.0.0.1:8000/abnormal-queries/?database=T24VN
**Kết quả mong đợi**: Hiển thị 2 truy vấn bất thường của T24VN

**URL**: http://127.0.0.1:8000/abnormal-queries/?database=WAY4
**Kết quả mong đợi**: Hiển thị 1 truy vấn bất thường của WAY4

### 3. Test Database không có truy vấn bất thường
**URL**: http://127.0.0.1:8000/abnormal-queries/?database=EBANK
**Kết quả mong đợi**: 
```
✅ Không có truy vấn bất thường nào cho database "EBANK"
Database này hoạt động tốt và không có truy vấn nào vi phạm quy tắc.
```

### 4. Test Database không tồn tại
**URL**: http://127.0.0.1:8000/abnormal-queries/?database=DATABASE_KHONG_TON_TAI
**Kết quả mong đợi**: 
```
✅ Không có truy vấn bất thường nào cho database "DATABASE_KHONG_TON_TAI"
Database này hoạt động tốt và không có truy vấn nào vi phạm quy tắc.
```

## 🎨 Tính năng Giao diện

### 1. Thống kê tổng quan
- **Truy vấn bất thường**: 4 (màu đỏ)
- **Tổng số logs**: 301 (màu xanh)
- **Tỷ lệ bất thường**: 1.33% (màu vàng)
- **Truy vấn bình thường**: 297 (màu xanh lá)

### 2. Thống kê theo Database
- **T24VN**: 2 truy vấn bất thường
- **WAY4**: 1 truy vấn bất thường  
- **MICRO**: 1 truy vấn bất thường

### 3. Phân loại mức độ nghiêm trọng
- **Rất cao**: exec_time_ms > 2000 VÀ exec_count > 500
- **Cao**: exec_time_ms > 1000 VÀ exec_count > 200
- **Trung bình**: Các trường hợp khác

### 4. Bảng dữ liệu
- Hiển thị đầy đủ thông tin: ID, Database, SQL Query, Thời gian, Số lần thực thi
- Màu sắc phân loại theo mức độ nghiêm trọng
- Phân trang và lọc theo database

## 🔧 Scripts Test

### Test tính năng abnormal queries:
```bash
python test_abnormal_queries.py
```

### Test kết nối PostgreSQL:
```bash
python test_postgres.py
```

## 📝 Ghi chú

- Quy tắc có thể được điều chỉnh trong view `abnormal_queries`
- Hiện tại phát hiện được 4 truy vấn bất thường từ tổng số 301 logs
- Tỷ lệ bất thường 1.33% là hợp lý cho hệ thống production
- Truy vấn của WAY4 với 5005ms là nghiêm trọng nhất cần được ưu tiên xử lý
