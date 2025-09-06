#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test đơn giản để kiểm tra việc đọc file log
"""

import re
from typing import List, Dict, Optional

def parse_log_line(line: str) -> Optional[Dict]:
    """Parse một dòng log thành dictionary"""
    try:
        pattern = r'DB:([^,]+),sql:([^,]+),exec_time_ms:(\d+),exec_count:(\d+)'
        match = re.match(pattern, line.strip())
        
        if match:
            database_name, sql_query, exec_time_ms, exec_count = match.groups()
            return {
                'database_name': database_name,
                'sql_query': sql_query,
                'exec_time_ms': int(exec_time_ms),
                'exec_count': int(exec_count)
            }
        return None
    except Exception as e:
        print(f"Lỗi khi parse dòng '{line}': {e}")
        return None

def read_and_parse_log(file_path: str = "logsql.log") -> List[Dict]:
    """Đọc và parse file log"""
    log_entries = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                if line.strip():
                    parsed_data = parse_log_line(line)
                    if parsed_data:
                        parsed_data['line_number'] = line_num
                        log_entries.append(parsed_data)
        
        print(f"Đọc thành công {len(log_entries)} dòng log")
        
    except Exception as e:
        print(f"Lỗi khi đọc file: {e}")
    
    return log_entries

def show_sample_data(log_entries: List[Dict], count: int = 5):
    """Hiển thị mẫu dữ liệu"""
    print(f"\n=== MẪU DỮ LIỆU (Top {count}) ===")
    for i, entry in enumerate(log_entries[:count], 1):
        print(f"{i}. Database: {entry['database_name']}")
        print(f"   SQL: {entry['sql_query'][:80]}...")
        print(f"   Thời gian: {entry['exec_time_ms']} ms")
        print(f"   Số lần thực thi: {entry['exec_count']}")
        print()

def show_statistics(log_entries: List[Dict]):
    """Hiển thị thống kê đơn giản"""
    if not log_entries:
        return
    
    # Thống kê theo database
    db_stats = {}
    total_exec_time = 0
    total_exec_count = 0
    
    for entry in log_entries:
        db_name = entry['database_name']
        if db_name not in db_stats:
            db_stats[db_name] = {
                'count': 0,
                'total_time': 0,
                'total_exec_count': 0
            }
        
        db_stats[db_name]['count'] += 1
        db_stats[db_name]['total_time'] += entry['exec_time_ms']
        db_stats[db_name]['total_exec_count'] += entry['exec_count']
        
        total_exec_time += entry['exec_time_ms']
        total_exec_count += entry['exec_count']
    
    print("\n=== THỐNG KÊ ===")
    print(f"Tổng số bản ghi: {len(log_entries)}")
    print(f"Tổng thời gian thực thi: {total_exec_time} ms")
    print(f"Tổng số lần thực thi: {total_exec_count}")
    
    print("\n--- Thống kê theo Database ---")
    for db_name, stats in db_stats.items():
        avg_time = stats['total_time'] / stats['count']
        print(f"Database: {db_name}")
        print(f"  - Số bản ghi: {stats['count']}")
        print(f"  - Thời gian TB: {avg_time:.2f} ms")
        print(f"  - Tổng thời gian: {stats['total_time']} ms")
        print(f"  - Tổng số lần thực thi: {stats['total_exec_count']}")
        print()
    
    # Top 5 queries chậm nhất
    sorted_entries = sorted(log_entries, key=lambda x: x['exec_time_ms'], reverse=True)
    print("--- Top 5 queries chậm nhất ---")
    for i, entry in enumerate(sorted_entries[:5], 1):
        print(f"{i}. Database: {entry['database_name']}")
        print(f"   SQL: {entry['sql_query'][:60]}...")
        print(f"   Thời gian: {entry['exec_time_ms']} ms")
        print(f"   Số lần thực thi: {entry['exec_count']}")
        print()

def main():
    """Hàm main"""
    print("=== SQL LOG PROCESSOR - TEST MODE ===")
    
    # Đọc và parse file log
    log_entries = read_and_parse_log()
    
    if log_entries:
        # Hiển thị mẫu dữ liệu
        show_sample_data(log_entries)
        
        # Hiển thị thống kê
        show_statistics(log_entries)
        
        print("Test hoàn thành thành công!")
    else:
        print("Không có dữ liệu để xử lý")

if __name__ == "__main__":
    main()
