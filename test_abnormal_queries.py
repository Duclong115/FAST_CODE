#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test tính năng quét truy vấn bất thường
"""

import os
import sys
import django
from django.conf import settings

# Thiết lập Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'log_analyzer.settings')
django.setup()

from logs.models import SqlLog

def test_abnormal_queries():
    """Test tính năng quét truy vấn bất thường"""
    print("=== TEST QUÉT TRUY VẤN BẤT THƯỜNG ===")
    
    # Quy tắc: exec_time_ms > 500 VÀ exec_count > 100
    abnormal_queries = SqlLog.objects.filter(
        exec_time_ms__gt=500,
        exec_count__gt=100
    )
    
    print(f"Quy tắc: exec_time_ms > 500 VÀ exec_count > 100")
    print(f"Tổng số truy vấn bất thường: {abnormal_queries.count()}")
    
    if abnormal_queries.exists():
        print("\n--- Danh sách truy vấn bất thường ---")
        for i, query in enumerate(abnormal_queries[:10], 1):
            print(f"{i}. Database: {query.database_name}")
            print(f"   SQL: {query.sql_query[:60]}...")
            print(f"   Thời gian: {query.exec_time_ms} ms")
            print(f"   Số lần thực thi: {query.exec_count}")
            print(f"   Thời gian TB: {query.avg_time_per_execution:.2f} ms")
            print()
    
    # Thống kê theo database
    print("--- Thống kê theo Database ---")
    db_stats = abnormal_queries.values('database_name').annotate(
        count=django.db.models.Count('id'),
        avg_exec_time=django.db.models.Avg('exec_time_ms'),
        avg_exec_count=django.db.models.Avg('exec_count')
    ).order_by('-count')
    
    for stat in db_stats:
        print(f"Database {stat['database_name']}: {stat['count']} truy vấn bất thường")
        print(f"  - Thời gian TB: {stat['avg_exec_time']:.2f} ms")
        print(f"  - Số lần thực thi TB: {stat['avg_exec_count']:.2f}")
        print()
    
    # Thống kê tổng quan
    total_logs = SqlLog.objects.count()
    abnormal_count = abnormal_queries.count()
    normal_count = total_logs - abnormal_count
    abnormal_percentage = (abnormal_count / total_logs * 100) if total_logs > 0 else 0
    
    print("--- Thống kê tổng quan ---")
    print(f"Tổng số logs: {total_logs}")
    print(f"Truy vấn bất thường: {abnormal_count}")
    print(f"Truy vấn bình thường: {normal_count}")
    print(f"Tỷ lệ bất thường: {abnormal_percentage:.2f}%")
    
    # Top truy vấn chậm nhất trong số bất thường
    print("\n--- Top 5 truy vấn chậm nhất (trong số bất thường) ---")
    slowest_abnormal = abnormal_queries.order_by('-exec_time_ms')[:5]
    for i, query in enumerate(slowest_abnormal, 1):
        print(f"{i}. Database: {query.database_name}")
        print(f"   Thời gian: {query.exec_time_ms} ms")
        print(f"   Số lần thực thi: {query.exec_count}")
        print(f"   SQL: {query.sql_query[:50]}...")
        print()

if __name__ == "__main__":
    test_abnormal_queries()
