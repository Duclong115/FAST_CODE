#!/usr/bin/env python3
"""
Utility functions để ghi log các hoạt động người dùng
"""

import logging
import json
from datetime import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# Loggers
web_activity_logger = logging.getLogger('web_activity')
security_logger = logging.getLogger('security')
general_logger = logging.getLogger('logs')


class ActivityLogger:
    """
    Class để ghi log các hoạt động người dùng
    """
    
    @staticmethod
    def log_user_login(request, user, success=True, failure_reason=None, mfa_pending=False, mfa_completed=False, mfa_method=None):
        """Ghi log đăng nhập"""
        ip_address = ActivityLogger._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        if success:
            if mfa_pending:
                web_activity_logger.info(
                    f"USER_LOGIN_SUCCESS_MFA_PENDING | User: {user.username} (ID: {user.id}) | "
                    f"IP: {ip_address} | User-Agent: {user_agent[:100]}"
                )
            elif mfa_completed:
                mfa_info = f" | MFA Method: {mfa_method}" if mfa_method else ""
                web_activity_logger.info(
                    f"USER_LOGIN_SUCCESS_MFA_COMPLETED | User: {user.username} (ID: {user.id}) | "
                    f"IP: {ip_address} | User-Agent: {user_agent[:100]}{mfa_info}"
                )
            else:
                web_activity_logger.info(
                    f"USER_LOGIN_SUCCESS | User: {user.username} (ID: {user.id}) | "
                    f"IP: {ip_address} | User-Agent: {user_agent[:100]}"
                )
        else:
            security_logger.warning(
                f"USER_LOGIN_FAILED | Username: {request.POST.get('username', 'Unknown')} | "
                f"Reason: {failure_reason} | IP: {ip_address} | "
                f"User-Agent: {user_agent[:100]}"
            )
    
    @staticmethod
    def log_user_logout(request, user):
        """Ghi log đăng xuất"""
        ip_address = ActivityLogger._get_client_ip(request)
        
        web_activity_logger.info(
            f"USER_LOGOUT | User: {user.username} (ID: {user.id}) | "
            f"IP: {ip_address}"
        )
    
    @staticmethod
    def log_user_registration(request, user, success=True, failure_reason=None):
        """Ghi log đăng ký"""
        ip_address = ActivityLogger._get_client_ip(request)
        
        if success:
            web_activity_logger.info(
                f"USER_REGISTRATION_SUCCESS | User: {user.username} (ID: {user.id}) | "
                f"Email: {user.email} | IP: {ip_address}"
            )
        else:
            security_logger.warning(
                f"USER_REGISTRATION_FAILED | Username: {request.POST.get('username', 'Unknown')} | "
                f"Reason: {failure_reason} | IP: {ip_address}"
            )
    
    @staticmethod
    def log_password_change(request, user, success=True):
        """Ghi log đổi mật khẩu"""
        ip_address = ActivityLogger._get_client_ip(request)
        
        if success:
            web_activity_logger.info(
                f"PASSWORD_CHANGE_SUCCESS | User: {user.username} (ID: {user.id}) | "
                f"IP: {ip_address}"
            )
        else:
            security_logger.warning(
                f"PASSWORD_CHANGE_FAILED | User: {user.username} (ID: {user.id}) | "
                f"IP: {ip_address}"
            )
    
    @staticmethod
    def log_database_permission_action(request, action, permission_id=None, user_id=None, database_name=None):
        """Ghi log các hoạt động phân quyền database"""
        current_user = request.user if hasattr(request, 'user') else None
        ip_address = ActivityLogger._get_client_ip(request)
        
        log_message = f"DB_PERMISSION_{action.upper()}"
        
        if current_user:
            log_message += f" | Admin: {current_user.username} (ID: {current_user.id})"
        
        if permission_id:
            log_message += f" | Permission ID: {permission_id}"
        
        if user_id:
            log_message += f" | Target User ID: {user_id}"
        
        if database_name:
            log_message += f" | Database: {database_name}"
        
        log_message += f" | IP: {ip_address}"
        
        web_activity_logger.info(log_message)
    
    @staticmethod
    def log_admin_action(request, action, details=None):
        """Ghi log các hoạt động admin"""
        current_user = request.user if hasattr(request, 'user') else None
        ip_address = ActivityLogger._get_client_ip(request)
        
        log_message = f"ADMIN_ACTION | {action}"
        
        if current_user:
            log_message += f" | Admin: {current_user.username} (ID: {current_user.id})"
        
        if details:
            log_message += f" | Details: {details}"
        
        log_message += f" | IP: {ip_address}"
        
        web_activity_logger.info(log_message)
    
    @staticmethod
    def log_data_access(request, action, database_name=None, table_name=None, record_count=None):
        """Ghi log truy cập dữ liệu"""
        current_user = request.user if hasattr(request, 'user') else None
        ip_address = ActivityLogger._get_client_ip(request)
        
        log_message = f"DATA_ACCESS | {action}"
        
        if current_user:
            log_message += f" | User: {current_user.username} (ID: {current_user.id})"
        
        if database_name:
            log_message += f" | Database: {database_name}"
        
        if table_name:
            log_message += f" | Table: {table_name}"
        
        if record_count:
            log_message += f" | Records: {record_count}"
        
        log_message += f" | IP: {ip_address}"
        
        web_activity_logger.info(log_message)
    
    @staticmethod
    def log_security_event(request, event_type, details=None, severity='WARNING'):
        """Ghi log các sự kiện bảo mật"""
        ip_address = ActivityLogger._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
        
        log_message = f"SECURITY_EVENT | {event_type}"
        
        if details:
            log_message += f" | Details: {details}"
        
        log_message += f" | IP: {ip_address} | User-Agent: {user_agent[:100]}"
        
        if severity == 'ERROR':
            security_logger.error(log_message)
        elif severity == 'WARNING':
            security_logger.warning(log_message)
        else:
            security_logger.info(log_message)
    
    @staticmethod
    def log_system_event(event_type, details=None, level='INFO'):
        """Ghi log các sự kiện hệ thống"""
        log_message = f"SYSTEM_EVENT | {event_type}"
        
        if details:
            log_message += f" | Details: {details}"
        
        if level == 'ERROR':
            general_logger.error(log_message)
        elif level == 'WARNING':
            general_logger.warning(log_message)
        else:
            general_logger.info(log_message)
    
    @staticmethod
    def log_mfa_setup(request, user, action):
        """Ghi log thiết lập MFA"""
        ip_address = ActivityLogger._get_client_ip(request)
        
        web_activity_logger.info(
            f"MFA_SETUP | User: {user.username} (ID: {user.id}) | "
            f"Action: {action} | IP: {ip_address}"
        )
    
    @staticmethod
    def log_mfa_verification(request, user, success=True, method=None, failure_reason=None):
        """Ghi log xác thực MFA"""
        ip_address = ActivityLogger._get_client_ip(request)
        
        if success:
            web_activity_logger.info(
                f"MFA_VERIFICATION_SUCCESS | User: {user.username} (ID: {user.id}) | "
                f"Method: {method} | IP: {ip_address}"
            )
        else:
            security_logger.warning(
                f"MFA_VERIFICATION_FAILED | User: {user.username} (ID: {user.id}) | "
                f"Reason: {failure_reason} | IP: {ip_address}"
            )
    
    @staticmethod
    def log_backup_code_usage(request, user, success=True):
        """Ghi log sử dụng backup code"""
        ip_address = ActivityLogger._get_client_ip(request)
        
        if success:
            web_activity_logger.info(
                f"BACKUP_CODE_USED | User: {user.username} (ID: {user.id}) | "
                f"IP: {ip_address}"
            )
        else:
            security_logger.warning(
                f"BACKUP_CODE_FAILED | User: {user.username} (ID: {user.id}) | "
                f"IP: {ip_address}"
            )

    @staticmethod
    def _get_client_ip(request):
        """Lấy IP address của client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


# Decorator để tự động ghi log cho các view
def log_view_activity(action_name):
    """
    Decorator để tự động ghi log hoạt động của view
    """
    def decorator(view_func):
        def wrapper(request, *args, **kwargs):
            # Ghi log trước khi thực hiện
            ActivityLogger.log_admin_action(request, f"VIEW_ACCESS_{action_name}")
            
            try:
                response = view_func(request, *args, **kwargs)
                
                # Ghi log sau khi thực hiện thành công
                ActivityLogger.log_admin_action(request, f"VIEW_SUCCESS_{action_name}")
                
                return response
            except Exception as e:
                # Ghi log khi có lỗi
                ActivityLogger.log_security_event(
                    request, 
                    f"VIEW_ERROR_{action_name}", 
                    f"Exception: {str(e)}", 
                    'ERROR'
                )
                raise
        
        return wrapper
    return decorator
