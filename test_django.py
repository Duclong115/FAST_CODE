#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test Django app
"""

import os
import sys
import django
from django.conf import settings

# Thiết lập Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'log_analyzer.settings')
django.setup()

from logs.models import SqlLog, LogFile

def test_models():
    """Test các models"""
    print("=== TEST DJANGO MODELS ===")
    
    # Test SqlLog
    print(f"Tổng số SQL logs: {SqlLog.objects.count()}")
    
    if SqlLog.objects.exists():
        log = SqlLog.objects.first()
        print(f"Log đầu tiên: {log}")
        print(f"Database: {log.database_name}")
        print(f"SQL: {log.sql_query[:50]}...")
        print(f"Thời gian: {log.exec_time_ms} ms")
        print(f"Số lần thực thi: {log.exec_count}")
        print(f"Thời gian TB: {log.avg_time_per_execution:.2f} ms")
    
    # Test LogFile
    print(f"\nTổng số file logs: {LogFile.objects.count()}")
    
    if LogFile.objects.exists():
        log_file = LogFile.objects.first()
        print(f"File đầu tiên: {log_file}")
        print(f"Tỷ lệ thành công: {log_file.success_rate:.2f}%")
    
    # Test thống kê
    print("\n=== THỐNG KÊ ===")
    db_stats = SqlLog.objects.values('database_name').annotate(
        count=django.db.models.Count('id'),
        total_time=django.db.models.Sum('exec_time_ms'),
        avg_time=django.db.models.Avg('exec_time_ms')
    ).order_by('-count')
    
    for stat in db_stats:
        print(f"Database {stat['database_name']}: {stat['count']} logs, "
              f"TB: {stat['avg_time']:.2f} ms")

if __name__ == "__main__":
    test_models()
