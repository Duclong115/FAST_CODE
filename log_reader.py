#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script đơn giản để đọc file logsql.log và hiển thị thống kê
Không cần database, chỉ đọc và phân tích dữ liệu
"""

import re
import json
from typing import List, Dict, Optional
from datetime import datetime
import os

class SimpleLogReader:
    """Class đơn giản để đọc và phân tích file log"""
    
    def __init__(self, log_file_path: str = "logsql.log"):
        self.log_file_path = log_file_path
        self.log_entries = []
    
    def parse_log_line(self, line: str) -> Optional[Dict]:
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
    
    def read_log_file(self) -> List[Dict]:
        """Đọc file log và parse thành danh sách dictionary"""
        self.log_entries = []
        
        try:
            if not os.path.exists(self.log_file_path):
                print(f"File {self.log_file_path} không tồn tại")
                return self.log_entries
            
            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    if line.strip():
                        parsed_data = self.parse_log_line(line)
                        if parsed_data:
                            parsed_data['line_number'] = line_num
                            self.log_entries.append(parsed_data)
            
            print(f"Đọc thành công {len(self.log_entries)} dòng log từ file {self.log_file_path}")
            
        except Exception as e:
            print(f"Lỗi khi đọc file log: {e}")
        
        return self.log_entries
    
    def get_database_statistics(self) -> Dict:
        """Lấy thống kê theo database"""
        if not self.log_entries:
            return {}
        
        db_stats = {}
        total_exec_time = 0
        total_exec_count = 0
        
        for entry in self.log_entries:
            db_name = entry['database_name']
            if db_name not in db_stats:
                db_stats[db_name] = {
                    'record_count': 0,
                    'total_exec_time': 0,
                    'total_exec_count': 0,
                    'queries': []
                }
            
            db_stats[db_name]['record_count'] += 1
            db_stats[db_name]['total_exec_time'] += entry['exec_time_ms']
            db_stats[db_name]['total_exec_count'] += entry['exec_count']
            db_stats[db_name]['queries'].append(entry['sql_query'])
            
            total_exec_time += entry['exec_time_ms']
            total_exec_count += entry['exec_count']
        
        # Tính toán thống kê
        for db_name, stats in db_stats.items():
            stats['avg_exec_time'] = round(stats['total_exec_time'] / stats['record_count'], 2)
            stats['unique_queries'] = len(set(stats['queries']))
            del stats['queries']  # Xóa để giảm kích thước
        
        return {
            'total_records': len(self.log_entries),
            'total_exec_time': total_exec_time,
            'total_exec_count': total_exec_count,
            'database_stats': db_stats
        }
    
    def get_slowest_queries(self, limit: int = 10) -> List[Dict]:
        """Lấy danh sách queries chậm nhất"""
        if not self.log_entries:
            return []
        
        sorted_entries = sorted(self.log_entries, key=lambda x: x['exec_time_ms'], reverse=True)
        return sorted_entries[:limit]
    
    def get_most_executed_queries(self, limit: int = 10) -> List[Dict]:
        """Lấy danh sách queries được thực thi nhiều nhất"""
        if not self.log_entries:
            return []
        
        sorted_entries = sorted(self.log_entries, key=lambda x: x['exec_count'], reverse=True)
        return sorted_entries[:limit]
    
    def export_to_json(self, output_file: str = "log_analysis.json"):
        """Xuất kết quả phân tích ra file JSON"""
        try:
            analysis_data = {
                'timestamp': datetime.now().isoformat(),
                'file_analyzed': self.log_file_path,
                'statistics': self.get_database_statistics(),
                'slowest_queries': self.get_slowest_queries(),
                'most_executed_queries': self.get_most_executed_queries()
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(analysis_data, f, ensure_ascii=False, indent=2)
            
            print(f"Đã xuất kết quả phân tích ra file: {output_file}")
            
        except Exception as e:
            print(f"Lỗi khi xuất file JSON: {e}")
    
    def print_report(self):
        """In báo cáo phân tích"""
        if not self.log_entries:
            print("Không có dữ liệu để phân tích")
            return
        
        stats = self.get_database_statistics()
        
        print("\n" + "="*60)
        print("BÁO CÁO PHÂN TÍCH SQL LOG")
        print("="*60)
        print(f"File phân tích: {self.log_file_path}")
        print(f"Thời gian phân tích: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        print(f"\nTỔNG QUAN:")
        print(f"- Tổng số bản ghi: {stats['total_records']}")
        print(f"- Tổng thời gian thực thi: {stats['total_exec_time']:,} ms")
        print(f"- Tổng số lần thực thi: {stats['total_exec_count']:,}")
        
        print(f"\nTHỐNG KÊ THEO DATABASE:")
        print("-" * 60)
        for db_name, db_stat in stats['database_stats'].items():
            print(f"Database: {db_name}")
            print(f"  - Số bản ghi: {db_stat['record_count']}")
            print(f"  - Thời gian TB: {db_stat['avg_exec_time']} ms")
            print(f"  - Tổng thời gian: {db_stat['total_exec_time']:,} ms")
            print(f"  - Tổng số lần thực thi: {db_stat['total_exec_count']:,}")
            print(f"  - Số queries duy nhất: {db_stat['unique_queries']}")
            print()
        
        print("TOP 10 QUERIES CHẬM NHẤT:")
        print("-" * 60)
        slowest = self.get_slowest_queries(10)
        for i, query in enumerate(slowest, 1):
            print(f"{i:2d}. Database: {query['database_name']}")
            print(f"    SQL: {query['sql_query'][:80]}...")
            print(f"    Thời gian: {query['exec_time_ms']:,} ms")
            print(f"    Số lần thực thi: {query['exec_count']}")
            print()
        
        print("TOP 10 QUERIES ĐƯỢC THỰC THI NHIỀU NHẤT:")
        print("-" * 60)
        most_executed = self.get_most_executed_queries(10)
        for i, query in enumerate(most_executed, 1):
            print(f"{i:2d}. Database: {query['database_name']}")
            print(f"    SQL: {query['sql_query'][:80]}...")
            print(f"    Số lần thực thi: {query['exec_count']}")
            print(f"    Thời gian: {query['exec_time_ms']:,} ms")
            print()

def main():
    """Hàm main"""
    reader = SimpleLogReader()
    
    # Đọc file log
    log_entries = reader.read_log_file()
    
    if log_entries:
        # In báo cáo
        reader.print_report()
        
        # Xuất ra file JSON
        reader.export_to_json()
        
        print("\nPhân tích hoàn thành!")
    else:
        print("Không có dữ liệu để phân tích")

if __name__ == "__main__":
    main()
