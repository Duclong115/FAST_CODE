from django.db import models
from django.utils import timezone


class SqlLog(models.Model):
    """Model để lưu trữ dữ liệu SQL log"""
    
    database_name = models.CharField(
        max_length=50, 
        verbose_name="Tên Database",
        help_text="Tên của database (VD: T24VN, WAY4, EBANK)"
    )
    
    sql_query = models.TextField(
        verbose_name="Câu SQL",
        help_text="Câu SQL được thực thi"
    )
    
    exec_time_ms = models.PositiveIntegerField(
        verbose_name="Thời gian thực thi (ms)",
        help_text="Thời gian thực thi câu SQL tính bằng milliseconds"
    )
    
    exec_count = models.PositiveIntegerField(
        verbose_name="Số lần thực thi",
        help_text="Số lần câu SQL được thực thi"
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Thời gian tạo",
        help_text="Thời gian bản ghi được tạo"
    )
    
    line_number = models.PositiveIntegerField(
        null=True, 
        blank=True,
        verbose_name="Số dòng trong file",
        help_text="Số dòng trong file log gốc"
    )
    
    class Meta:
        verbose_name = "SQL Log"
        verbose_name_plural = "SQL Logs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['database_name']),
            models.Index(fields=['exec_time_ms']),
            models.Index(fields=['exec_count']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.database_name} - {self.sql_query[:50]}..."
    
    @property
    def exec_time_seconds(self):
        """Trả về thời gian thực thi tính bằng giây"""
        return self.exec_time_ms / 1000.0
    
    @property
    def avg_time_per_execution(self):
        """Trả về thời gian trung bình cho mỗi lần thực thi"""
        if self.exec_count > 0:
            return self.exec_time_ms / self.exec_count
        return 0


class LogFile(models.Model):
    """Model để lưu thông tin về file log đã được xử lý"""
    
    file_name = models.CharField(
        max_length=255,
        verbose_name="Tên file",
        help_text="Tên file log"
    )
    
    file_path = models.CharField(
        max_length=500,
        verbose_name="Đường dẫn file",
        help_text="Đường dẫn đầy đủ đến file log"
    )
    
    file_size = models.BigIntegerField(
        verbose_name="Kích thước file (bytes)",
        help_text="Kích thước file tính bằng bytes"
    )
    
    total_lines = models.PositiveIntegerField(
        verbose_name="Tổng số dòng",
        help_text="Tổng số dòng trong file"
    )
    
    processed_lines = models.PositiveIntegerField(
        verbose_name="Số dòng đã xử lý",
        help_text="Số dòng đã được xử lý thành công"
    )
    
    failed_lines = models.PositiveIntegerField(
        default=0,
        verbose_name="Số dòng lỗi",
        help_text="Số dòng không thể xử lý"
    )
    
    processed_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Thời gian xử lý",
        help_text="Thời gian file được xử lý"
    )
    
    processing_time = models.DurationField(
        null=True,
        blank=True,
        verbose_name="Thời gian xử lý",
        help_text="Thời gian để xử lý file"
    )
    
    error_details = models.TextField(
        blank=True,
        null=True,
        verbose_name="Chi tiết lỗi",
        help_text="Chi tiết các dòng lỗi không thể xử lý"
    )
    
    class Meta:
        verbose_name = "Log File"
        verbose_name_plural = "Log Files"
        ordering = ['-processed_at']
    
    def __str__(self):
        return f"{self.file_name} - {self.processed_lines}/{self.total_lines} dòng"
    
    @property
    def success_rate(self):
        """Tỷ lệ thành công"""
        if self.total_lines > 0:
            return (self.processed_lines / self.total_lines) * 100
        return 0