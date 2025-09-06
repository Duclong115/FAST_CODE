#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để test database không có dữ liệu
"""

import os
import sys
import django
from django.conf import settings

# Thiết lập Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'log_analyzer.settings')
django.setup()

from logs.models import SqlLog

def test_empty_database():
    """Test database không có dữ liệu"""
    print("=== TEST DATABASE KHÔNG CÓ DỮ LIỆU ===")
    
    # Kiểm tra database DB_KHONG_DU_LIEU
    empty_db_logs = SqlLog.objects.filter(database_name='DB_KHONG_DU_LIEU')
    print(f"Số logs cho DB_KHONG_DU_LIEU: {empty_db_logs.count()}")
    
    if empty_db_logs.exists():
        log = empty_db_logs.first()
        print(f"Log đầu tiên:")
        print(f"  Database: {log.database_name}")
        print(f"  SQL: {log.sql_query}")
        print(f"  Thời gian: {log.exec_time_ms} ms")
        print(f"  Số lần thực thi: {log.exec_count}")
    
    # Kiểm tra database không tồn tại
    non_existent_db = SqlLog.objects.filter(database_name='DATABASE_KHONG_TON_TAI')
    print(f"\nSố logs cho DATABASE_KHONG_TON_TAI: {non_existent_db.count()}")
    
    # Danh sách tất cả databases
    all_databases = SqlLog.objects.values_list('database_name', flat=True).distinct().order_by('database_name')
    print(f"\nTất cả databases có trong hệ thống:")
    for db in all_databases:
        count = SqlLog.objects.filter(database_name=db).count()
        print(f"  - {db}: {count} logs")

if __name__ == "__main__":
    test_empty_database()
