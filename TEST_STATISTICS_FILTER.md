# Test Tính Năng Lọc Database Trong Trang Thống Kê

## 🎯 Mục đích
Test tính năng lọc database trong trang thống kê và hiển thị thông báo "Không tìm thấy truy vấn nào cho DB này" khi không có dữ liệu.

## 📊 Dữ liệu Test

### Danh sách Databases:
- **BIZ**: 17 logs, 5596 ms, 853 lần thực thi
- **DATABASE_KHONG_TON_TAI**: 1 log, 0 ms, 0 lần thực thi (không có dữ liệu thực)
- **DB_KHONG_DU_LIEU**: 1 log, 0 ms, 0 lần thực thi (không có dữ liệu thực)
- **EBANK**: 114 logs, 30040 ms, 7227 lần thực thi
- **MICRO**: 21 logs, 5697 ms, 1195 lần thực thi
- **SALE**: 4 logs, 757 ms, 315 lần thực thi
- **T24VN**: 104 logs, 28610 ms, 6165 lần thực thi
- **WAY4**: 39 logs, 14539 ms, 1785 lần thực thi

## 🌐 Test Cases

### 1. Truy cập trang thống kê tổng quan
**URL**: http://127.0.0.1:8000/statistics/
**Kết quả mong đợi**: 
- Hiển thị tất cả thống kê tổng quan
- Tổng số logs: 301
- Hiển thị dropdown lọc database
- Hiển thị tất cả bảng thống kê

### 2. Lọc theo Database có dữ liệu
**URL**: http://127.0.0.1:8000/statistics/?database=T24VN
**Kết quả mong đợi**: 
- Hiển thị thống kê chỉ cho T24VN
- Tổng số logs: 104
- Tổng thời gian: 28610 ms
- Tổng số lần thực thi: 6165
- Thời gian TB: 275.10 ms

**URL**: http://127.0.0.1:8000/statistics/?database=EBANK
**Kết quả mong đợi**: 
- Hiển thị thống kê chỉ cho EBANK
- Tổng số logs: 114
- Tổng thời gian: 30040 ms
- Tổng số lần thực thi: 7227
- Thời gian TB: 263.51 ms

### 3. Test Database không có dữ liệu thực
**URL**: http://127.0.0.1:8000/statistics/?database=DB_KHONG_DU_LIEU
**Kết quả mong đợi**: 
```
⚠️ Không tìm thấy truy vấn nào cho database "DB_KHONG_DU_LIEU"
Vui lòng chọn database khác hoặc xem tất cả databases.
```
- Không hiển thị các bảng thống kê
- Chỉ hiển thị thông báo cảnh báo

**URL**: http://127.0.0.1:8000/statistics/?database=DATABASE_KHONG_TON_TAI
**Kết quả mong đợi**: 
```
⚠️ Không tìm thấy truy vấn nào cho database "DATABASE_KHONG_TON_TAI"
Vui lòng chọn database khác hoặc xem tất cả databases.
```

### 4. Test Database hoàn toàn không tồn tại
**URL**: http://127.0.0.1:8000/statistics/?database=DATABASE_HOAN_TOAN_KHONG_TON_TAI
**Kết quả mong đợi**: 
```
⚠️ Không tìm thấy truy vấn nào cho database "DATABASE_HOAN_TOAN_KHONG_TON_TAI"
Vui lòng chọn database khác hoặc xem tất cả databases.
```

### 5. Test Database có ít dữ liệu
**URL**: http://127.0.0.1:8000/statistics/?database=SALE
**Kết quả mong đợi**: 
- Hiển thị thống kê cho SALE
- Tổng số logs: 4
- Tổng thời gian: 757 ms
- Tổng số lần thực thi: 315
- Thời gian TB: 189.25 ms

## 🎨 Tính năng Giao diện

### 1. Form lọc database
- Dropdown chứa tất cả databases
- Nút "Lọc" để áp dụng filter
- Giữ nguyên giá trị đã chọn sau khi submit

### 2. Thông báo khi không có dữ liệu
- Alert màu vàng với icon cảnh báo
- Hiển thị tên database được chọn
- Gợi ý chọn database khác

### 3. Ẩn/hiện nội dung
- **Khi có dữ liệu**: Hiển thị tất cả thống kê
- **Khi không có dữ liệu**: Chỉ hiển thị thông báo cảnh báo

### 4. Thống kê được lọc
- Tổng quan: Số logs, thời gian, số lần thực thi
- Thống kê theo database: Chỉ hiển thị database được chọn
- Top queries: Chỉ hiển thị queries của database được chọn

## 🔧 Scripts Test

### Test tính năng lọc database:
```bash
python test_statistics_filter.py
```

### Test kết nối PostgreSQL:
```bash
python test_postgres.py
```

## 📝 Ghi chú

- Tính năng lọc database hoạt động trên tất cả thống kê
- Thông báo "Không tìm thấy truy vấn nào cho DB này" chỉ hiển thị khi có database được chọn nhưng không có dữ liệu
- Các database có exec_count = 0 được coi là không có dữ liệu thực
- Giao diện responsive và thân thiện với người dùng
