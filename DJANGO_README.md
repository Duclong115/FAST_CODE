# Django SQL Log Analyzer

Ứng dụng Django để đọc file `logsql.log` và lưu vào database với giao diện web.

## Cài đặt và chạy

### 1. Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### 2. Chạy migrations
```bash
python manage.py migrate
```

### 3. Import dữ liệu từ file log
```bash
python manage.py import_logs logsql.log
```

### 4. Chạy development server
```bash
python manage.py runserver
```

Truy cập: http://127.0.0.1:8000

## Tính năng

### 1. Management Command
- `python manage.py import_logs logsql.log`: Import dữ liệu từ file log
- `python manage.py import_logs logsql.log --clear-existing`: Xóa dữ liệu cũ trước khi import
- `python manage.py import_logs logsql.log --batch-size 50`: Thay đổi kích thước batch
- `python manage.py import_logs logsql.log --database h2`: Sử dụng database khác

### 2. Web Interface

#### Trang chủ (/)
- Danh sách tất cả SQL logs
- Phân trang và lọc theo database
- Hiển thị thông tin chi tiết: thời gian thực thi, số lần thực thi, SQL query

#### Trang thống kê (/statistics/)
- Tổng quan: tổng số logs, thời gian thực thi, số lần thực thi
- Thống kê theo database
- Top 10 queries chậm nhất
- Top 10 queries được thực thi nhiều nhất
- Biểu đồ phân bố theo database

#### Trang file logs (/log-files/)
- Danh sách các file log đã được xử lý
- Thống kê tỷ lệ thành công
- Thời gian xử lý

#### API (/api/logs/)
- Endpoint JSON để lấy dữ liệu logs
- Hỗ trợ phân trang và lọc

### 3. Admin Interface (/admin/)
- Quản lý dữ liệu SQL logs
- Quản lý thông tin file logs đã xử lý
- Tìm kiếm và lọc dữ liệu

## Models

### SqlLog
- `database_name`: Tên database
- `sql_query`: Câu SQL
- `exec_time_ms`: Thời gian thực thi (ms)
- `exec_count`: Số lần thực thi
- `created_at`: Thời gian tạo bản ghi
- `line_number`: Số dòng trong file gốc

### LogFile
- `file_name`: Tên file
- `file_path`: Đường dẫn file
- `file_size`: Kích thước file
- `total_lines`: Tổng số dòng
- `processed_lines`: Số dòng đã xử lý
- `failed_lines`: Số dòng lỗi
- `processed_at`: Thời gian xử lý
- `processing_time`: Thời gian để xử lý

## Cấu trúc Project

```
log_analyzer/
├── logs/
│   ├── models.py          # Models SqlLog và LogFile
│   ├── views.py           # Views cho web interface
│   ├── urls.py            # URL patterns
│   ├── admin.py           # Admin configuration
│   ├── management/
│   │   └── commands/
│   │       └── import_logs.py  # Management command
│   └── templates/
│       └── logs/
│           ├── base.html       # Template cơ sở
│           ├── index.html      # Trang danh sách logs
│           ├── statistics.html # Trang thống kê
│           └── log_files.html  # Trang file logs
├── log_analyzer/
│   ├── settings.py        # Django settings
│   └── urls.py            # Main URL configuration
└── manage.py              # Django management script
```

## Lưu ý

- Database mặc định sử dụng SQLite (có thể thay đổi trong settings.py)
- File log được parse theo format: `DB:database_name,sql:SQL_query,exec_time_ms:time,exec_count:count`
- Ứng dụng hỗ trợ phân trang và lọc dữ liệu
- Giao diện responsive với Bootstrap 5
- Có thể mở rộng để hỗ trợ H2 database thực sự

## Troubleshooting

### Lỗi import
- Kiểm tra file log tồn tại và có quyền đọc
- Kiểm tra format file log đúng chuẩn
- Xem log lỗi trong console

### Lỗi database
- Chạy `python manage.py migrate` để tạo bảng
- Kiểm tra quyền ghi database
- Xóa file database cũ nếu cần

### Lỗi template
- Kiểm tra đường dẫn template trong settings.py
- Đảm bảo thư mục templates tồn tại
