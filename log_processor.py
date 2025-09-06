#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để đọc file logsql.log và lưu vào H2 database in-memory
"""

import re
import logging
from typing import List, Dict, Optional
from sqlalchemy import create_engine, Column, Integer, String, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Thiết lập logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

Base = declarative_base()

class SqlLog(Base):
    """Model cho bảng sql_log"""
    __tablename__ = 'sql_log'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    database_name = Column(String(50), nullable=False)
    sql_query = Column(String(1000), nullable=False)
    exec_time_ms = Column(Integer, nullable=False)
    exec_count = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

class LogProcessor:
    """Class để xử lý file log và lưu vào database"""
    
    def __init__(self, log_file_path: str = "logsql.log"):
        """
        Khởi tạo LogProcessor
        
        Args:
            log_file_path: Đường dẫn đến file log
        """
        self.log_file_path = log_file_path
        self.engine = None
        self.session = None
        
    def setup_database(self):
        """Thiết lập kết nối H2 database in-memory"""
        try:
            # Tạo engine cho H2 in-memory database
            # Sử dụng JDBC URL cho H2 in-memory
            database_url = "h2:///mem:testdb"
            
            # Tạo engine
            self.engine = create_engine(
                database_url,
                echo=False,  # Set True để debug SQL queries
                pool_pre_ping=True
            )
            
            # Tạo session
            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            
            # Tạo bảng
            Base.metadata.create_all(self.engine)
            
            logger.info("Kết nối H2 database thành công")
            
        except Exception as e:
            logger.error(f"Lỗi khi thiết lập database: {e}")
            raise
    
    def parse_log_line(self, line: str) -> Optional[Dict]:
        """
        Parse một dòng log thành dictionary
        
        Args:
            line: Dòng log cần parse
            
        Returns:
            Dictionary chứa thông tin đã parse hoặc None nếu không parse được
        """
        try:
            # Pattern để parse log line
            # Format: DB:database_name,sql:SQL_query,exec_time_ms:time,exec_count:count
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
            else:
                logger.warning(f"Không thể parse dòng: {line.strip()}")
                return None
                
        except Exception as e:
            logger.error(f"Lỗi khi parse dòng '{line}': {e}")
            return None
    
    def read_log_file(self) -> List[Dict]:
        """
        Đọc file log và parse thành danh sách dictionary
        
        Returns:
            List các dictionary chứa thông tin log
        """
        log_entries = []
        
        try:
            if not os.path.exists(self.log_file_path):
                logger.error(f"File {self.log_file_path} không tồn tại")
                return log_entries
            
            with open(self.log_file_path, 'r', encoding='utf-8') as file:
                for line_num, line in enumerate(file, 1):
                    if line.strip():  # Bỏ qua dòng trống
                        parsed_data = self.parse_log_line(line)
                        if parsed_data:
                            parsed_data['line_number'] = line_num
                            log_entries.append(parsed_data)
            
            logger.info(f"Đọc thành công {len(log_entries)} dòng log từ file {self.log_file_path}")
            
        except Exception as e:
            logger.error(f"Lỗi khi đọc file log: {e}")
            
        return log_entries
    
    def save_to_database(self, log_entries: List[Dict]):
        """
        Lưu danh sách log entries vào database
        
        Args:
            log_entries: Danh sách các dictionary chứa thông tin log
        """
        try:
            saved_count = 0
            
            for entry in log_entries:
                # Tạo object SqlLog
                sql_log = SqlLog(
                    database_name=entry['database_name'],
                    sql_query=entry['sql_query'],
                    exec_time_ms=entry['exec_time_ms'],
                    exec_count=entry['exec_count']
                )
                
                # Thêm vào session
                self.session.add(sql_log)
                saved_count += 1
            
            # Commit transaction
            self.session.commit()
            logger.info(f"Đã lưu thành công {saved_count} bản ghi vào database")
            
        except Exception as e:
            logger.error(f"Lỗi khi lưu vào database: {e}")
            self.session.rollback()
            raise
    
    def get_statistics(self) -> Dict:
        """
        Lấy thống kê từ database
        
        Returns:
            Dictionary chứa các thống kê
        """
        try:
            stats = {}
            
            # Tổng số bản ghi
            total_records = self.session.query(SqlLog).count()
            stats['total_records'] = total_records
            
            # Thống kê theo database
            db_stats = self.session.execute(text("""
                SELECT database_name, 
                       COUNT(*) as record_count,
                       AVG(exec_time_ms) as avg_exec_time,
                       SUM(exec_count) as total_exec_count
                FROM sql_log 
                GROUP BY database_name
                ORDER BY record_count DESC
            """)).fetchall()
            
            stats['database_stats'] = [
                {
                    'database_name': row[0],
                    'record_count': row[1],
                    'avg_exec_time_ms': round(row[2], 2),
                    'total_exec_count': row[3]
                }
                for row in db_stats
            ]
            
            # Top 10 queries chậm nhất
            slowest_queries = self.session.execute(text("""
                SELECT sql_query, exec_time_ms, exec_count, database_name
                FROM sql_log 
                ORDER BY exec_time_ms DESC 
                LIMIT 10
            """)).fetchall()
            
            stats['slowest_queries'] = [
                {
                    'sql_query': row[0],
                    'exec_time_ms': row[1],
                    'exec_count': row[2],
                    'database_name': row[3]
                }
                for row in slowest_queries
            ]
            
            return stats
            
        except Exception as e:
            logger.error(f"Lỗi khi lấy thống kê: {e}")
            return {}
    
    def close_connection(self):
        """Đóng kết nối database"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()
        logger.info("Đã đóng kết nối database")

def main():
    """Hàm main để chạy toàn bộ quá trình"""
    processor = LogProcessor()
    
    try:
        # Thiết lập database
        processor.setup_database()
        
        # Đọc file log
        log_entries = processor.read_log_file()
        
        if log_entries:
            # Lưu vào database
            processor.save_to_database(log_entries)
            
            # Hiển thị thống kê
            stats = processor.get_statistics()
            
            print("\n=== THỐNG KÊ LOG SQL ===")
            print(f"Tổng số bản ghi: {stats.get('total_records', 0)}")
            
            print("\n--- Thống kê theo Database ---")
            for db_stat in stats.get('database_stats', []):
                print(f"Database: {db_stat['database_name']}")
                print(f"  - Số bản ghi: {db_stat['record_count']}")
                print(f"  - Thời gian thực thi trung bình: {db_stat['avg_exec_time_ms']} ms")
                print(f"  - Tổng số lần thực thi: {db_stat['total_exec_count']}")
                print()
            
            print("--- Top 10 queries chậm nhất ---")
            for i, query in enumerate(stats.get('slowest_queries', []), 1):
                print(f"{i}. Database: {query['database_name']}")
                print(f"   Query: {query['sql_query'][:100]}...")
                print(f"   Thời gian: {query['exec_time_ms']} ms")
                print(f"   Số lần thực thi: {query['exec_count']}")
                print()
        
        else:
            print("Không có dữ liệu để xử lý")
            
    except Exception as e:
        logger.error(f"Lỗi trong quá trình xử lý: {e}")
        
    finally:
        # Đóng kết nối
        processor.close_connection()

if __name__ == "__main__":
    main()
