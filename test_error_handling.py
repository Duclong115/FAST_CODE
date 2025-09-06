#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test tính năng xử lý lỗi định dạng trong file log
"""

import os
import sys
import django
from django.conf import settings

# Thiết lập Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'log_analyzer.settings')
django.setup()

from logs.models import LogFile, SqlLog

def test_error_handling():
    """Test tính năng xử lý lỗi định dạng"""
    print("=== TEST XỬ LÝ LỖI ĐỊNH DẠNG TRONG FILE LOG ===")
    
    # Lấy file log mới nhất
    latest_log_file = LogFile.objects.order_by('-processed_at').first()
    
    if not latest_log_file:
        print("Không có file log nào được xử lý!")
        return
    
    print(f"File log: {latest_log_file.file_name}")
    print(f"Tổng số dòng: {latest_log_file.total_lines}")
    print(f"Đã xử lý thành công: {latest_log_file.processed_lines}")
    print(f"Số dòng lỗi: {latest_log_file.failed_lines}")
    print(f"Tỷ lệ thành công: {latest_log_file.success_rate:.2f}%")
    print(f"Thời gian xử lý: {latest_log_file.processing_time}")
    
    if latest_log_file.error_details:
        print(f"\n--- Chi tiết các dòng lỗi ---")
        error_lines = latest_log_file.error_details.split('\n')
        for i, error_line in enumerate(error_lines, 1):
            print(f"{i}. {error_line}")
    else:
        print("\nKhông có lỗi nào!")
    
    # Kiểm tra dữ liệu đã được lưu
    print(f"\n--- Kiểm tra dữ liệu đã lưu ---")
    total_logs = SqlLog.objects.count()
    print(f"Tổng số logs trong database: {total_logs}")
    
    # Thống kê theo database
    db_stats = SqlLog.objects.values('database_name').annotate(
        count=django.db.models.Count('id')
    ).order_by('-count')
    
    print(f"\n--- Thống kê theo Database ---")
    for stat in db_stats:
        print(f"Database {stat['database_name']}: {stat['count']} logs")
    
    # Kiểm tra các dòng đã được xử lý đúng
    print(f"\n--- Mẫu dữ liệu đã xử lý ---")
    sample_logs = SqlLog.objects.order_by('-created_at')[:5]
    for i, log in enumerate(sample_logs, 1):
        print(f"{i}. Database: {log.database_name}")
        print(f"   SQL: {log.sql_query[:50]}...")
        print(f"   Thời gian: {log.exec_time_ms} ms")
        print(f"   Số lần thực thi: {log.exec_count}")
        print(f"   Dòng số: {log.line_number}")
        print()

if __name__ == "__main__":
    test_error_handling()
