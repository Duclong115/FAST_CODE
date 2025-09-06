# Test Database Không Có Dữ Liệu

## 🎯 Mục đích
Test các trường hợp khi không có truy vấn nào cho database được chọn và hiển thị thông báo phù hợp.

## 📊 Dữ liệu Test

### Databases có trong hệ thống:
- **T24VN**: 104 logs (có dữ liệu)
- **EBANK**: 114 logs (có dữ liệu)  
- **WAY4**: 39 logs (có dữ liệu)
- **MICRO**: 21 logs (có dữ liệu)
- **BIZ**: 17 logs (có dữ liệu)
- **DB_KHONG_DU_LIEU**: 1 log (có dữ liệu nhưng exec_count = 0)
- **DATABASE_KHONG_TON_TAI**: 1 log (có dữ liệu nhưng exec_count = 0)

### Databases hoàn toàn không tồn tại:
- **DATABASE_HOAN_TOAN_KHONG_TON_TAI**: 0 logs
- **DATABASE_TRONG_RONG**: 0 logs

## 🧪 Các Test Case

### 1. Test Database có dữ liệu
**URL**: http://127.0.0.1:8000/?database=T24VN
**Kết quả mong đợi**: Hiển thị danh sách logs của T24VN

### 2. Test Database không tồn tại
**URL**: http://127.0.0.1:8000/?database=DATABASE_HOAN_TOAN_KHONG_TON_TAI
**Kết quả mong đợi**: 
```
⚠️ Không tìm thấy truy vấn nào cho database "DATABASE_HOAN_TOAN_KHONG_TON_TAI"
Vui lòng chọn database khác hoặc xem tất cả databases.
```

### 3. Test Database trống rỗng
**URL**: http://127.0.0.1:8000/?database=DATABASE_TRONG_RONG
**Kết quả mong đợi**: 
```
⚠️ Không tìm thấy truy vấn nào cho database "DATABASE_TRONG_RONG"
Vui lòng chọn database khác hoặc xem tất cả databases.
```

### 4. Test Database có dữ liệu nhưng exec_count = 0
**URL**: http://127.0.0.1:8000/?database=DB_KHONG_DU_LIEU
**Kết quả mong đợi**: Hiển thị log với exec_count = 0

### 5. Test Trang thống kê
**URL**: http://127.0.0.1:8000/statistics/
**Kết quả mong đợi**: 
- Hiển thị section "Databases không có dữ liệu" nếu có
- Liệt kê các database không có truy vấn nào

## 🔧 Scripts Test

### Test kết nối PostgreSQL:
```bash
python test_postgres.py
```

### Test databases không có dữ liệu:
```bash
python test_empty_db.py
```

### Test các trường hợp không có dữ liệu:
```bash
python test_no_data.py
```

## 📝 Ghi chú

- Database `DB_KHONG_DU_LIEU` và `DATABASE_KHONG_TON_TAI` có dữ liệu nhưng với exec_count = 0
- Database `DATABASE_HOAN_TOAN_KHONG_TON_TAI` và `DATABASE_TRONG_RONG` hoàn toàn không có dữ liệu
- Giao diện sẽ hiển thị thông báo khác nhau tùy theo trường hợp
- Trang thống kê sẽ phân loại databases có dữ liệu và không có dữ liệu
