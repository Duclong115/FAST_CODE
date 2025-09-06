# Test Tính Năng Tạo Báo Cáo CSV và PDF

## 🎯 Mục đích
Test tính năng tạo báo cáo với khả năng xuất file CSV và PDF cho người dùng.

## 📊 Các loại báo cáo

### 1. Báo cáo Tổng hợp (Summary Report)
**Mô tả**: Thống kê tổng quan về hiệu suất SQL logs
**Nội dung**:
- Thống kê tổng quan (tổng số logs, thời gian, số lần thực thi)
- Thống kê theo database
- Top 10 queries chậm nhất
- Top 10 queries được thực thi nhiều nhất

### 2. Báo cáo Chi tiết (Detailed Report)
**Mô tả**: Danh sách đầy đủ tất cả logs với thông tin chi tiết
**Nội dung**:
- ID, Database, SQL Query đầy đủ
- Thời gian thực thi (ms), số lần thực thi
- Thời gian TB, số dòng, thời gian tạo
- Sắp xếp theo thời gian tạo mới nhất

### 3. Báo cáo Truy vấn Bất thường (Abnormal Report)
**Mô tả**: Các truy vấn có hiệu suất bất thường
**Quy tắc**: `exec_time_ms > 500` VÀ `exec_count > 100`
**Nội dung**:
- Phân loại mức độ nghiêm trọng (Rất cao/Cao/Trung bình)
- Thông tin chi tiết truy vấn bất thường
- Sắp xếp theo thời gian thực thi giảm dần

## 📁 Định dạng xuất

### CSV Format
- **Encoding**: UTF-8 với BOM
- **Tên file**: `bao_cao_[loai]_YYYYMMDD_HHMMSS.csv`
- **Tương thích**: Microsoft Excel, LibreOffice Calc
- **Ưu điểm**: Dễ chỉnh sửa, phân tích dữ liệu

### PDF Format
- **Kích thước**: A4
- **Font**: Helvetica
- **Màu sắc**: Professional với header màu xám
- **Tên file**: `bao_cao_[loai]_YYYYMMDD_HHMMSS.pdf`
- **Ưu điểm**: Dễ in, chia sẻ, trình bày

## 🌐 Test Cases

### 1. Truy cập trang Tạo Báo Cáo
**URL**: http://127.0.0.1:8000/generate-report/
**Kết quả mong đợi**: 
- Form với 3 loại báo cáo
- 2 định dạng xuất (CSV/PDF)
- Dropdown lọc database
- Thông tin hướng dẫn

### 2. Tạo báo cáo tổng hợp CSV
**Action**: 
- Chọn "Báo cáo tổng hợp"
- Chọn "CSV"
- Chọn database hoặc "Tất cả"
- Nhấn "Tạo Báo Cáo"
**Kết quả mong đợi**: 
- File CSV được tải xuống
- Tên file: `bao_cao_tong_hop_YYYYMMDD_HHMMSS.csv`
- Nội dung: Thống kê tổng quan + top queries

### 3. Tạo báo cáo chi tiết PDF
**Action**: 
- Chọn "Báo cáo chi tiết"
- Chọn "PDF"
- Chọn database cụ thể
- Nhấn "Tạo Báo Cáo"
**Kết quả mong đợi**: 
- File PDF được tải xuống
- Tên file: `bao_cao_chi_tiet_YYYYMMDD_HHMMSS.pdf`
- Nội dung: Bảng chi tiết với header đẹp

### 4. Tạo báo cáo bất thường CSV
**Action**: 
- Chọn "Truy vấn bất thường"
- Chọn "CSV"
- Để trống database filter
- Nhấn "Tạo Báo Cáo"
**Kết quả mong đợi**: 
- File CSV được tải xuống
- Tên file: `bao_cao_bat_thuong_YYYYMMDD_HHMMSS.csv`
- Nội dung: Chỉ các truy vấn bất thường

## 📋 Test Data

### Dữ liệu hiện tại:
- **Tổng số logs**: 20
- **Tổng thời gian**: 15,603 ms
- **Tổng số lần thực thi**: 1,771
- **Thời gian TB**: 780.15 ms
- **Số databases**: 6 (EBANK, WAY4, T24VN, MICRO, BIZ, SALE)
- **Truy vấn bất thường**: 5

### Databases có dữ liệu:
1. **EBANK**: 5 logs, 2,220ms, 470 exec
2. **WAY4**: 5 logs, 7,327ms, 349 exec  
3. **T24VN**: 4 logs, 3,720ms, 414 exec
4. **MICRO**: 4 logs, 1,586ms, 413 exec
5. **BIZ**: 1 log, 300ms, 50 exec
6. **SALE**: 1 log, 450ms, 75 exec

## 🔧 Scripts Test

### Test tính năng báo cáo:
```bash
python test_report_generation.py
```

### Test kết nối PostgreSQL:
```bash
python test_postgres.py
```

### Test xử lý lỗi định dạng:
```bash
python test_error_handling.py
```

## 🎨 Tính năng Giao diện

### 1. Form Tạo Báo Cáo
- **Layout**: 2 cột (form + thông tin)
- **Loại báo cáo**: Radio buttons với icon và mô tả
- **Định dạng**: Radio buttons với icon và mô tả
- **Database filter**: Dropdown với tất cả databases
- **Nút tạo**: Primary button với icon download

### 2. Thông tin Báo Cáo
- **Card thông tin**: Hiển thị nội dung báo cáo được chọn
- **Card hướng dẫn**: Hướng dẫn sử dụng từng bước
- **Alert**: Lưu ý về tên file và timestamp

### 3. Preview (Tùy chọn)
- **Section ẩn**: Hiển thị khi chọn format JSON
- **AJAX loading**: Load preview không reload trang
- **Table responsive**: Hiển thị mẫu dữ liệu

## 📝 Ghi chú

### Định dạng file:
- **CSV**: UTF-8 encoding, comma separator
- **PDF**: A4 size, professional styling
- **Tên file**: Chứa timestamp để tránh trùng lặp

### Tính năng:
- ✅ **3 loại báo cáo**: Tổng hợp, Chi tiết, Bất thường
- ✅ **2 định dạng xuất**: CSV và PDF
- ✅ **Filter database**: Theo database cụ thể hoặc tất cả
- ✅ **Tên file tự động**: Với timestamp
- ✅ **Giao diện thân thiện**: Bootstrap 5 với icon
- ✅ **Preview tương tác**: AJAX loading
- ✅ **Responsive design**: Hoạt động trên mobile

### Navigation:
- **Menu mới**: "Tạo Báo Cáo" với icon download
- **Vị trí**: Giữa "Quét Truy Vấn Bất Thường" và "File Logs"

**Hệ thống đã sẵn sàng tạo báo cáo CSV và PDF cho người dùng!** 🚀
