#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test tính năng lọc database trong trang thống kê
"""

import os
import sys
import django
from django.conf import settings

# Thiết lập Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'log_analyzer.settings')
django.setup()

from logs.models import SqlLog

def test_statistics_filter():
    """Test tính năng lọc database trong trang thống kê"""
    print("=== TEST LỌC DATABASE TRONG TRANG THỐNG KÊ ===")
    
    # Danh sách tất cả databases
    all_databases = SqlLog.objects.values_list('database_name', flat=True).distinct().order_by('database_name')
    print(f"Tất cả databases: {list(all_databases)}")
    
    # Test từng database
    for db in all_databases:
        logs_query = SqlLog.objects.filter(database_name=db)
        count = logs_query.count()
        
        if count > 0:
            total_exec_time = logs_query.aggregate(total=django.db.models.Sum('exec_time_ms'))['total'] or 0
            total_exec_count = logs_query.aggregate(total=django.db.models.Sum('exec_count'))['total'] or 0
            avg_exec_time = logs_query.aggregate(avg=django.db.models.Avg('exec_time_ms'))['avg'] or 0
            
            print(f"\nDatabase {db}:")
            print(f"  - Số logs: {count}")
            print(f"  - Tổng thời gian: {total_exec_time} ms")
            print(f"  - Tổng số lần thực thi: {total_exec_count}")
            print(f"  - Thời gian TB: {avg_exec_time:.2f} ms")
        else:
            print(f"\nDatabase {db}: KHÔNG CÓ DỮ LIỆU")
    
    # Test database không tồn tại
    print(f"\n--- Test database không tồn tại ---")
    non_existent_db = SqlLog.objects.filter(database_name='DATABASE_HOAN_TOAN_KHONG_TON_TAI')
    print(f"DATABASE_HOAN_TOAN_KHONG_TON_TAI: {non_existent_db.count()} logs")
    
    # Test database trống rỗng
    empty_db = SqlLog.objects.filter(database_name='DATABASE_TRONG_RONG')
    print(f"DATABASE_TRONG_RONG: {empty_db.count()} logs")
    
    # Thống kê tổng quan
    print(f"\n--- Thống kê tổng quan ---")
    total_logs = SqlLog.objects.count()
    print(f"Tổng số logs: {total_logs}")
    
    # Top queries chậm nhất
    print(f"\n--- Top 5 queries chậm nhất ---")
    slowest_queries = SqlLog.objects.order_by('-exec_time_ms')[:5]
    for i, query in enumerate(slowest_queries, 1):
        print(f"{i}. Database: {query.database_name}")
        print(f"   Thời gian: {query.exec_time_ms} ms")
        print(f"   Số lần thực thi: {query.exec_count}")
        print(f"   SQL: {query.sql_query[:50]}...")
        print()
    
    # Top queries được thực thi nhiều nhất
    print(f"--- Top 5 queries được thực thi nhiều nhất ---")
    most_executed = SqlLog.objects.order_by('-exec_count')[:5]
    for i, query in enumerate(most_executed, 1):
        print(f"{i}. Database: {query.database_name}")
        print(f"   Số lần thực thi: {query.exec_count}")
        print(f"   Thời gian: {query.exec_time_ms} ms")
        print(f"   SQL: {query.sql_query[:50]}...")
        print()

if __name__ == "__main__":
    test_statistics_filter()
