import re
import os
import time
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from logs.models import SqlLog, LogFile


class Command(BaseCommand):
    help = 'Import SQL logs from file into database'

    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to the log file to import'
        )
        parser.add_argument(
            '--database',
            type=str,
            default='default',
            help='Database to use (default: default)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process in each batch (default: 100)'
        )
        parser.add_argument(
            '--clear-existing',
            action='store_true',
            help='Clear existing logs before importing'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        database = options['database']
        batch_size = options['batch_size']
        clear_existing = options['clear_existing']

        # Kiểm tra file tồn tại
        if not os.path.exists(file_path):
            raise CommandError(f'File "{file_path}" does not exist.')

        # Lấy thông tin file
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        self.stdout.write(f'Processing file: {file_name}')
        self.stdout.write(f'File size: {file_size:,} bytes')
        self.stdout.write(f'Database: {database}')
        self.stdout.write(f'Batch size: {batch_size}')

        start_time = time.time()

        try:
            # Đếm tổng số dòng
            total_lines = self.count_lines(file_path)
            self.stdout.write(f'Total lines: {total_lines:,}')

            # Xóa dữ liệu cũ nếu được yêu cầu
            if clear_existing:
                self.stdout.write('Clearing existing logs...')
                SqlLog.objects.using(database).all().delete()
                self.stdout.write('Existing logs cleared.')

            # Xử lý file
            processed_lines, failed_lines, error_details = self.process_file(
                file_path, database, batch_size, total_lines
            )

            # Tính thời gian xử lý
            processing_time = time.time() - start_time
            processing_duration = timedelta(seconds=processing_time)

            # Lưu thông tin file đã xử lý
            log_file = LogFile.objects.create(
                file_name=file_name,
                file_path=file_path,
                file_size=file_size,
                total_lines=total_lines,
                processed_lines=processed_lines,
                failed_lines=failed_lines,
                processing_time=processing_duration,
                error_details='\n'.join(error_details) if error_details else None
            )

            # Hiển thị kết quả
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nImport completed successfully!'
                )
            )
            self.stdout.write(f'Processed: {processed_lines:,} lines')
            self.stdout.write(f'Failed: {failed_lines:,} lines')
            self.stdout.write(f'Success rate: {(processed_lines/total_lines)*100:.2f}%')
            self.stdout.write(f'Processing time: {processing_duration}')
            self.stdout.write(f'Log file record ID: {log_file.id}')

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error processing file: {str(e)}')
            )
            raise CommandError(f'Import failed: {str(e)}')

    def count_lines(self, file_path):
        """Đếm tổng số dòng trong file"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return sum(1 for line in file if line.strip())

    def parse_log_line(self, line):
        """Parse một dòng log thành dictionary"""
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
            return None
        except Exception:
            return None

    def process_file(self, file_path, database, batch_size, total_lines):
        """Xử lý file log và import vào database"""
        processed_lines = 0
        failed_lines = 0
        batch_data = []
        error_details = []

        with open(file_path, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                if line.strip():  # Bỏ qua dòng trống
                    parsed_data = self.parse_log_line(line)
                    
                    if parsed_data:
                        parsed_data['line_number'] = line_num
                        batch_data.append(SqlLog(**parsed_data))
                        processed_lines += 1
                    else:
                        failed_lines += 1
                        error_details.append(f"Dòng {line_num}: {line.strip()}")
                        if failed_lines <= 10:  # Chỉ hiển thị 10 lỗi đầu tiên
                            self.stdout.write(
                                self.style.WARNING(
                                    f'Failed to parse line {line_num}: {line.strip()[:100]}...'
                                )
                            )

                    # Xử lý batch khi đủ số lượng
                    if len(batch_data) >= batch_size:
                        self.save_batch(batch_data, database)
                        batch_data = []
                        
                        # Hiển thị tiến trình
                        progress = (line_num / total_lines) * 100
                        self.stdout.write(f'Progress: {progress:.1f}% ({line_num:,}/{total_lines:,})')

            # Xử lý batch cuối cùng
            if batch_data:
                self.save_batch(batch_data, database)

        return processed_lines, failed_lines, error_details

    def save_batch(self, batch_data, database):
        """Lưu batch dữ liệu vào database"""
        try:
            with transaction.atomic(using=database):
                SqlLog.objects.using(database).bulk_create(batch_data)
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error saving batch: {str(e)}')
            )
            raise
