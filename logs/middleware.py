#!/usr/bin/env python3
"""
Middleware để ghi log tất cả các hoạt động web
"""

import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import JsonResponse
from django.urls import resolve, Resolver404

# Logger cho web activity
web_activity_logger = logging.getLogger('web_activity')
security_logger = logging.getLogger('security')
general_logger = logging.getLogger('logs')


class WebActivityLoggingMiddleware(MiddlewareMixin):
    """
    Middleware để ghi log tất cả các request/response
    """
    
    def process_request(self, request):
        """Ghi log khi có request"""
        request._start_time = time.time()
        
        # Lấy thông tin cơ bản
        user_info = self._get_user_info(request)
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Ghi log request
        web_activity_logger.info(
            f"REQUEST | {request.method} {request.path} | "
            f"User: {user_info} | IP: {ip_address} | "
            f"User-Agent: {user_agent[:100]}"
        )
        
        # Log POST data nếu có (trừ password)
        if request.method == 'POST' and request.POST:
            safe_post_data = self._sanitize_post_data(request.POST.dict())
            if safe_post_data:
                web_activity_logger.info(f"POST_DATA | {request.path} | Data: {safe_post_data}")
    
    def process_response(self, request, response):
        """Ghi log khi có response"""
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            user_info = self._get_user_info(request)
            ip_address = self._get_client_ip(request)
            
            # Ghi log response
            web_activity_logger.info(
                f"RESPONSE | {request.method} {request.path} | "
                f"Status: {response.status_code} | "
                f"Duration: {duration:.3f}s | "
                f"User: {user_info} | IP: {ip_address}"
            )
            
            # Log lỗi nếu có
            if response.status_code >= 400:
                security_logger.warning(
                    f"HTTP_ERROR | {request.method} {request.path} | "
                    f"Status: {response.status_code} | "
                    f"User: {user_info} | IP: {ip_address}"
                )
        
        return response
    
    def process_exception(self, request, exception):
        """Ghi log khi có exception"""
        user_info = self._get_user_info(request)
        ip_address = self._get_client_ip(request)
        
        security_logger.error(
            f"EXCEPTION | {request.method} {request.path} | "
            f"Exception: {type(exception).__name__}: {str(exception)} | "
            f"User: {user_info} | IP: {ip_address}"
        )
        
        return None
    
    def _get_user_info(self, request):
        """Lấy thông tin user"""
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"{request.user.username} (ID: {request.user.id})"
        return "Anonymous"
    
    def _get_client_ip(self, request):
        """Lấy IP address của client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _sanitize_post_data(self, post_data):
        """Loại bỏ thông tin nhạy cảm khỏi POST data"""
        sensitive_fields = ['password', 'csrfmiddlewaretoken', 'secret', 'token']
        sanitized = {}
        
        for key, value in post_data.items():
            if any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = '[REDACTED]'
            else:
                sanitized[key] = str(value)[:200]  # Giới hạn độ dài
        
        return sanitized


class SecurityLoggingMiddleware(MiddlewareMixin):
    """
    Middleware để ghi log các hoạt động bảo mật
    """
    
    def process_request(self, request):
        """Kiểm tra và ghi log các hoạt động bảo mật"""
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        # Kiểm tra suspicious patterns
        suspicious_patterns = [
            'admin', 'login', 'password', 'sql', 'script', 'eval',
            'union', 'select', 'drop', 'delete', 'insert', 'update'
        ]
        
        path_lower = request.path.lower()
        if any(pattern in path_lower for pattern in suspicious_patterns):
            security_logger.info(
                f"SUSPICIOUS_REQUEST | {request.method} {request.path} | "
                f"IP: {ip_address} | User-Agent: {user_agent[:100]}"
            )
        
        # Kiểm tra rate limiting (có thể mở rộng)
        self._check_rate_limiting(request, ip_address)
    
    def _get_client_ip(self, request):
        """Lấy IP address của client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def _check_rate_limiting(self, request, ip_address):
        """Kiểm tra rate limiting (placeholder)"""
        # Có thể implement rate limiting logic ở đây
        pass
