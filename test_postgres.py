#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test kết nối PostgreSQL
"""

import os
import sys
import django
from django.conf import settings

# Thiết lập Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'log_analyzer.settings')
django.setup()

from logs.models import SqlLog, LogFile
import psycopg2

def test_postgres_connection():
    """Test kết nối PostgreSQL"""
    print("=== TEST KẾT NỐI POSTGRESQL ===")
    
    try:
        # Test kết nối trực tiếp
        conn = psycopg2.connect(
            host='localhost',
            port=5432,
            user='postgres',
            password='1',
            database='sql_log_analyzer'
        )
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"PostgreSQL Version: {version[0]}")
        
        # Test Django ORM
        print(f"\nTổng số SQL logs trong PostgreSQL: {SqlLog.objects.count()}")
        print(f"Tổng số file logs trong PostgreSQL: {LogFile.objects.count()}")
        
        if SqlLog.objects.exists():
            log = SqlLog.objects.first()
            print(f"\nLog đầu tiên:")
            print(f"  Database: {log.database_name}")
            print(f"  SQL: {log.sql_query[:50]}...")
            print(f"  Thời gian: {log.exec_time_ms} ms")
            print(f"  Số lần thực thi: {log.exec_count}")
        
        cursor.close()
        conn.close()
        print("\n✅ Kết nối PostgreSQL thành công!")
        
    except Exception as e:
        print(f"❌ Lỗi kết nối PostgreSQL: {e}")

if __name__ == "__main__":
    test_postgres_connection()
