#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để test database hoàn toàn không có dữ liệu
"""

import os
import sys
import django
from django.conf import settings

# Thiết lập Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'log_analyzer.settings')
django.setup()

from logs.models import SqlLog

def test_no_data_scenarios():
    """Test các trường hợp không có dữ liệu"""
    print("=== TEST CÁC TRƯỜNG HỢP KHÔNG CÓ DỮ LIỆU ===")
    
    # Test database hoàn toàn không tồn tại
    non_existent_db = SqlLog.objects.filter(database_name='DATABASE_HOAN_TOAN_KHONG_TON_TAI')
    print(f"Số logs cho DATABASE_HOAN_TOAN_KHONG_TON_TAI: {non_existent_db.count()}")
    
    # Test database có tên nhưng không có dữ liệu thực sự
    empty_db = SqlLog.objects.filter(database_name='DATABASE_TRONG_RONG')
    print(f"Số logs cho DATABASE_TRONG_RONG: {empty_db.count()}")
    
    # Test database có dữ liệu nhưng exec_count = 0
    zero_exec_db = SqlLog.objects.filter(database_name='DB_KHONG_DU_LIEU')
    print(f"Số logs cho DB_KHONG_DU_LIEU: {zero_exec_db.count()}")
    
    if zero_exec_db.exists():
        log = zero_exec_db.first()
        print(f"  - SQL: {log.sql_query}")
        print(f"  - Thời gian: {log.exec_time_ms} ms")
        print(f"  - Số lần thực thi: {log.exec_count}")
    
    # Danh sách tất cả databases
    all_databases = SqlLog.objects.values_list('database_name', flat=True).distinct().order_by('database_name')
    print(f"\nTất cả databases có trong hệ thống:")
    for db in all_databases:
        count = SqlLog.objects.filter(database_name=db).count()
        print(f"  - {db}: {count} logs")

if __name__ == "__main__":
    test_no_data_scenarios()
