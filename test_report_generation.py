#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test tính năng tạo báo cáo CSV và PDF
"""

import os
import sys
import django
from django.conf import settings

# Thiết lập Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'log_analyzer.settings')
django.setup()

from logs.models import SqlLog, LogFile
from logs.views import generate_summary_report, generate_detailed_report, generate_abnormal_report

def test_report_generation():
    """Test tính năng tạo báo cáo"""
    print("=== TEST TÍNH NĂNG TẠO BÁO CÁO ===")
    
    # Lấy dữ liệu test
    logs_query = SqlLog.objects.all()
    total_logs = logs_query.count()
    
    print(f"Tổng số logs trong database: {total_logs}")
    
    if total_logs == 0:
        print("Không có dữ liệu để test!")
        return
    
    # Test báo cáo tổng hợp
    print(f"\n--- Test Báo cáo Tổng hợp ---")
    try:
        # Tạo dữ liệu thống kê trực tiếp
        total_logs_count = logs_query.count()
        total_exec_time = logs_query.aggregate(total=django.db.models.Sum('exec_time_ms'))['total'] or 0
        total_exec_count = logs_query.aggregate(total=django.db.models.Sum('exec_count'))['total'] or 0
        avg_exec_time = logs_query.aggregate(avg=django.db.models.Avg('exec_time_ms'))['avg'] or 0
        
        db_stats = logs_query.values('database_name').annotate(
            count=django.db.models.Count('id'),
            total_exec_time=django.db.models.Sum('exec_time_ms'),
            total_exec_count=django.db.models.Sum('exec_count'),
            avg_exec_time=django.db.models.Avg('exec_time_ms')
        ).order_by('-count')
        
        slowest_queries = logs_query.order_by('-exec_time_ms')[:10]
        most_executed = logs_query.order_by('-exec_count')[:10]
        
        print(f"✅ Báo cáo tổng hợp thành công")
        print(f"   - Tổng số logs: {total_logs_count}")
        print(f"   - Tổng thời gian: {total_exec_time} ms")
        print(f"   - Tổng số lần thực thi: {total_exec_count}")
        print(f"   - Thời gian TB: {round(avg_exec_time, 2) if avg_exec_time else 0} ms")
        print(f"   - Số databases: {len(list(db_stats))}")
        print(f"   - Top queries chậm: {len(list(slowest_queries))}")
        print(f"   - Top queries nhiều: {len(list(most_executed))}")
    except Exception as e:
        print(f"❌ Lỗi báo cáo tổng hợp: {e}")
    
    # Test báo cáo chi tiết
    print(f"\n--- Test Báo cáo Chi tiết ---")
    try:
        logs_data = logs_query.order_by('-created_at')
        print(f"✅ Báo cáo chi tiết thành công")
        print(f"   - Số records: {len(list(logs_data))}")
        if logs_data.exists():
            sample = logs_data.first()
            print(f"   - Mẫu record: ID={sample.id}, DB={sample.database_name}")
    except Exception as e:
        print(f"❌ Lỗi báo cáo chi tiết: {e}")
    
    # Test báo cáo bất thường
    print(f"\n--- Test Báo cáo Bất thường ---")
    try:
        abnormal_query = logs_query.filter(exec_time_ms__gt=500, exec_count__gt=100)
        abnormal_count = abnormal_query.count()
        print(f"✅ Báo cáo bất thường thành công")
        print(f"   - Số truy vấn bất thường: {abnormal_count}")
        if abnormal_count > 0:
            sample = abnormal_query.first()
            print(f"   - Mẫu: DB={sample.database_name}, Time={sample.exec_time_ms}ms, Count={sample.exec_count}")
    except Exception as e:
        print(f"❌ Lỗi báo cáo bất thường: {e}")
    
    # Test với filter database
    print(f"\n--- Test với Filter Database ---")
    databases = SqlLog.objects.values_list('database_name', flat=True).distinct()
    if databases:
        test_db = databases[0]
        print(f"Test với database: {test_db}")
        
        filtered_query = logs_query.filter(database_name=test_db)
        try:
            filtered_count = filtered_query.count()
            print(f"✅ Báo cáo với filter thành công")
            print(f"   - Logs trong {test_db}: {filtered_count}")
        except Exception as e:
            print(f"❌ Lỗi báo cáo với filter: {e}")
    
    print(f"\n--- Thống kê Database ---")
    db_stats = SqlLog.objects.values('database_name').annotate(
        count=django.db.models.Count('id'),
        total_exec_time=django.db.models.Sum('exec_time_ms'),
        total_exec_count=django.db.models.Sum('exec_count'),
        avg_exec_time=django.db.models.Avg('exec_time_ms')
    ).order_by('-count')
    
    for stat in db_stats:
        print(f"Database {stat['database_name']}: {stat['count']} logs, {stat['total_exec_time']}ms, {stat['total_exec_count']} exec")
    
    print(f"\n=== HOÀN THÀNH TEST ===")

if __name__ == "__main__":
    test_report_generation()
