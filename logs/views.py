from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import pandas as pd
import io
import csv
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
import json
from .models import SqlLog, LogFile


def register_vietnamese_font():
    """Đăng ký font hỗ trợ tiếng Việt cho ReportLab"""
    try:
        # Thử các font hệ thống Windows có sẵn
        font_paths = [
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/arialuni.ttf', 
            'C:/Windows/Fonts/tahoma.ttf',
            'C:/Windows/Fonts/calibri.ttf',
            'C:/Windows/Fonts/segoeui.ttf'
        ]
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('VietnameseFont', font_path))
                    return True
                except:
                    continue
        
        # Fallback: sử dụng font mặc định
        return False
    except:
        return False


def index(request):
    """Trang chủ hiển thị danh sách logs"""
    # Lấy tham số từ request
    page_number = request.GET.get('page', 1)
    database_filter = request.GET.get('database', '')
    per_page = request.GET.get('per_page', 20)
    
    # Query logs
    logs_query = SqlLog.objects.all()
    
    if database_filter:
        logs_query = logs_query.filter(database_name=database_filter)
    
    # Phân trang
    paginator = Paginator(logs_query, per_page)
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách databases để filter
    databases = SqlLog.objects.values_list('database_name', flat=True).distinct().order_by('database_name')
    
    # Kiểm tra có dữ liệu cho database được chọn không
    has_data = logs_query.exists() if database_filter else True
    total_count = paginator.count
    
    context = {
        'page_obj': page_obj,
        'databases': databases,
        'selected_database': database_filter,
        'per_page': per_page,
        'has_data': has_data,
        'total_count': total_count,
    }
    
    return render(request, 'logs/index.html', context)


def statistics(request):
    """Trang thống kê"""
    # Lấy tham số filter database
    database_filter = request.GET.get('database', '')
    
    # Query logs cơ bản
    logs_query = SqlLog.objects.all()
    if database_filter:
        logs_query = logs_query.filter(database_name=database_filter)
    
    # Thống kê tổng quan
    total_logs = logs_query.count()
    total_exec_time = logs_query.aggregate(total=Sum('exec_time_ms'))['total'] or 0
    total_exec_count = logs_query.aggregate(total=Sum('exec_count'))['total'] or 0
    avg_exec_time = logs_query.aggregate(avg=Avg('exec_time_ms'))['avg'] or 0
    
    # Thống kê theo database (tất cả databases)
    db_stats = SqlLog.objects.values('database_name').annotate(
        count=Count('id'),
        total_exec_time=Sum('exec_time_ms'),
        total_exec_count=Sum('exec_count'),
        avg_exec_time=Avg('exec_time_ms')
    ).order_by('-count')
    
    # Phân loại databases
    databases_with_data = [stat['database_name'] for stat in db_stats if stat['count'] > 0]
    databases_without_data = [stat['database_name'] for stat in db_stats if stat['count'] == 0]
    
    # Top queries chậm nhất (theo filter)
    slowest_queries = logs_query.order_by('-exec_time_ms')[:10]
    
    # Top queries được thực thi nhiều nhất (theo filter)
    most_executed = logs_query.order_by('-exec_count')[:10]
    
    # Thống kê theo thời gian (theo filter)
    recent_logs = logs_query.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).count()
    
    # Lấy danh sách databases để filter
    all_databases = SqlLog.objects.values_list('database_name', flat=True).distinct().order_by('database_name')
    
    # Kiểm tra có dữ liệu cho database được chọn không
    has_data = logs_query.exists() if database_filter else True
    
    context = {
        'total_logs': total_logs,
        'total_exec_time': total_exec_time,
        'total_exec_count': total_exec_count,
        'avg_exec_time': round(avg_exec_time, 2) if avg_exec_time else 0,
        'db_stats': db_stats,
        'databases_with_data': databases_with_data,
        'databases_without_data': databases_without_data,
        'slowest_queries': slowest_queries,
        'most_executed': most_executed,
        'recent_logs': recent_logs,
        'all_databases': all_databases,
        'selected_database': database_filter,
        'has_data': has_data,
    }
    
    return render(request, 'logs/statistics.html', context)


def log_files(request):
    """Trang danh sách các file log đã xử lý"""
    log_files = LogFile.objects.all().order_by('-processed_at')
    
    context = {
        'log_files': log_files,
    }
    
    return render(request, 'logs/log_files.html', context)


def abnormal_queries(request):
    """Trang quét truy vấn bất thường"""
    # Lấy tham số từ request
    page_number = request.GET.get('page', 1)
    database_filter = request.GET.get('database', '')
    per_page = request.GET.get('per_page', 20)
    
    # Query logs bất thường: exec_time_ms > 500 VÀ exec_count > 100
    abnormal_query = SqlLog.objects.filter(
        exec_time_ms__gt=500,
        exec_count__gt=100
    )
    
    if database_filter:
        abnormal_query = abnormal_query.filter(database_name=database_filter)
    
    # Phân trang
    paginator = Paginator(abnormal_query, per_page)
    page_obj = paginator.get_page(page_number)
    
    # Lấy danh sách databases để filter
    databases = SqlLog.objects.values_list('database_name', flat=True).distinct().order_by('database_name')
    
    # Thống kê truy vấn bất thường
    total_abnormal = abnormal_query.count()
    total_logs = SqlLog.objects.count()
    abnormal_percentage = (total_abnormal / total_logs * 100) if total_logs > 0 else 0
    
    # Thống kê theo database
    db_abnormal_stats = abnormal_query.values('database_name').annotate(
        count=Count('id'),
        avg_exec_time=Avg('exec_time_ms'),
        avg_exec_count=Avg('exec_count')
    ).order_by('-count')
    
    context = {
        'page_obj': page_obj,
        'databases': databases,
        'selected_database': database_filter,
        'per_page': per_page,
        'total_abnormal': total_abnormal,
        'total_logs': total_logs,
        'abnormal_percentage': round(abnormal_percentage, 2),
        'db_abnormal_stats': db_abnormal_stats,
        'has_data': abnormal_query.exists() if database_filter else True,
    }
    
    return render(request, 'logs/abnormal_queries.html', context)


def api_logs(request):
    """API endpoint để lấy dữ liệu logs dưới dạng JSON"""
    page_number = request.GET.get('page', 1)
    database_filter = request.GET.get('database', '')
    per_page = min(int(request.GET.get('per_page', 20)), 100)  # Giới hạn tối đa 100
    
    # Query logs
    logs_query = SqlLog.objects.all()
    
    if database_filter:
        logs_query = logs_query.filter(database_name=database_filter)
    
    # Phân trang
    paginator = Paginator(logs_query, per_page)
    page_obj = paginator.get_page(page_number)
    
    # Chuyển đổi thành JSON
    logs_data = []
    for log in page_obj:
        logs_data.append({
            'id': log.id,
            'database_name': log.database_name,
            'sql_query': log.sql_query,
            'exec_time_ms': log.exec_time_ms,
            'exec_count': log.exec_count,
            'created_at': log.created_at.isoformat(),
            'line_number': log.line_number,
        })
    
    return JsonResponse({
        'logs': logs_data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_count': paginator.count,
            'has_next': page_obj.has_next(),
            'has_previous': page_obj.has_previous(),
        }
    })


def generate_report(request):
    """Trang tạo báo cáo"""
    if request.method == 'POST':
        report_type = request.POST.get('report_type')
        format_type = request.POST.get('format_type')
        database_filter = request.POST.get('database_filter', '')
        
        # Lấy dữ liệu theo filter
        logs_query = SqlLog.objects.all()
        if database_filter:
            logs_query = logs_query.filter(database_name=database_filter)
        
        if report_type == 'summary':
            return generate_summary_report(logs_query, format_type, database_filter)
        elif report_type == 'detailed':
            return generate_detailed_report(logs_query, format_type, database_filter)
        elif report_type == 'abnormal':
            abnormal_query = logs_query.filter(exec_time_ms__gt=500, exec_count__gt=100)
            return generate_abnormal_report(abnormal_query, format_type, database_filter)
    
    # GET request - hiển thị form
    databases = SqlLog.objects.values_list('database_name', flat=True).distinct().order_by('database_name')
    context = {
        'databases': databases,
    }
    return render(request, 'logs/report.html', context)


def generate_summary_report(logs_query, format_type, database_filter):
    """Tạo báo cáo tổng hợp"""
    # Thống kê tổng quan
    total_logs = logs_query.count()
    total_exec_time = logs_query.aggregate(total=Sum('exec_time_ms'))['total'] or 0
    total_exec_count = logs_query.aggregate(total=Sum('exec_count'))['total'] or 0
    avg_exec_time = logs_query.aggregate(avg=Avg('exec_time_ms'))['avg'] or 0
    
    # Thống kê theo database
    db_stats = logs_query.values('database_name').annotate(
        count=Count('id'),
        total_exec_time=Sum('exec_time_ms'),
        total_exec_count=Sum('exec_count'),
        avg_exec_time=Avg('exec_time_ms')
    ).order_by('-count')
    
    # Top queries chậm nhất
    slowest_queries = logs_query.order_by('-exec_time_ms')[:10]
    
    # Top queries được thực thi nhiều nhất
    most_executed = logs_query.order_by('-exec_count')[:10]
    
    data = {
        'summary': {
            'total_logs': total_logs,
            'total_exec_time': total_exec_time,
            'total_exec_count': total_exec_count,
            'avg_exec_time': round(avg_exec_time, 2) if avg_exec_time else 0,
            'database_filter': database_filter,
            'generated_at': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        },
        'db_stats': list(db_stats),
        'slowest_queries': [
            {
                'database_name': q.database_name,
                'sql_query': q.sql_query[:100] + '...' if len(q.sql_query) > 100 else q.sql_query,
                'exec_time_ms': q.exec_time_ms,
                'exec_count': q.exec_count,
                'avg_time_per_execution': float(q.avg_time_per_execution)
            } for q in slowest_queries
        ],
        'most_executed': [
            {
                'database_name': q.database_name,
                'sql_query': q.sql_query[:100] + '...' if len(q.sql_query) > 100 else q.sql_query,
                'exec_time_ms': q.exec_time_ms,
                'exec_count': q.exec_count,
                'avg_time_per_execution': float(q.avg_time_per_execution)
            } for q in most_executed
        ]
    }
    
    if format_type == 'csv':
        return export_summary_csv(data)
    elif format_type == 'pdf':
        return export_summary_pdf(data)
    else:
        return JsonResponse(data)


def generate_detailed_report(logs_query, format_type, database_filter):
    """Tạo báo cáo chi tiết"""
    logs_data = logs_query.order_by('-created_at')
    
    data = [
        {
            'ID': log.id,
            'Database': log.database_name,
            'SQL Query': log.sql_query,
            'Thời gian (ms)': log.exec_time_ms,
            'Số lần thực thi': log.exec_count,
            'Thời gian TB (ms)': round(float(log.avg_time_per_execution), 2),
            'Dòng số': log.line_number or '',
            'Thời gian tạo': log.created_at.strftime('%d/%m/%Y %H:%M:%S')
        } for log in logs_data
    ]
    
    if format_type == 'csv':
        return export_detailed_csv(data, database_filter)
    elif format_type == 'pdf':
        return export_detailed_pdf(data, database_filter)
    else:
        return JsonResponse({'logs': data})


def generate_abnormal_report(abnormal_query, format_type, database_filter):
    """Tạo báo cáo truy vấn bất thường"""
    abnormal_data = abnormal_query.order_by('-exec_time_ms')
    
    data = [
        {
            'ID': log.id,
            'Database': log.database_name,
            'SQL Query': log.sql_query[:100] + '...' if len(log.sql_query) > 100 else log.sql_query,
            'Thời gian (ms)': log.exec_time_ms,
            'Số lần thực thi': log.exec_count,
            'Thời gian TB (ms)': round(float(log.avg_time_per_execution), 2),
            'Mức độ nghiêm trọng': 'Rất cao' if log.exec_time_ms > 2000 and log.exec_count > 500 else 
                                  'Cao' if log.exec_time_ms > 1000 and log.exec_count > 200 else 'Trung bình',
            'Dòng số': log.line_number or '',
            'Thời gian tạo': log.created_at.strftime('%d/%m/%Y %H:%M:%S')
        } for log in abnormal_data
    ]
    
    if format_type == 'csv':
        return export_abnormal_csv(data, database_filter)
    elif format_type == 'pdf':
        return export_abnormal_pdf(data, database_filter)
    else:
        return JsonResponse({'abnormal_logs': data})


def export_summary_csv(data):
    """Xuất báo cáo tổng hợp ra CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="bao_cao_tong_hop_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Header
    writer.writerow(['BÁO CÁO TỔNG HỢP SQL LOGS'])
    writer.writerow(['Thời gian tạo:', data['summary']['generated_at']])
    writer.writerow(['Database filter:', data['summary']['database_filter'] or 'Tất cả'])
    writer.writerow([])
    
    # Thống kê tổng quan
    writer.writerow(['THỐNG KÊ TỔNG QUAN'])
    writer.writerow(['Tổng số logs:', data['summary']['total_logs']])
    writer.writerow(['Tổng thời gian (ms):', data['summary']['total_exec_time']])
    writer.writerow(['Tổng số lần thực thi:', data['summary']['total_exec_count']])
    writer.writerow(['Thời gian TB (ms):', data['summary']['avg_exec_time']])
    writer.writerow([])
    
    # Thống kê theo database
    writer.writerow(['THỐNG KÊ THEO DATABASE'])
    writer.writerow(['Database', 'Số logs', 'Tổng thời gian (ms)', 'Tổng số lần thực thi', 'Thời gian TB (ms)'])
    for stat in data['db_stats']:
        writer.writerow([
            stat['database_name'],
            stat['count'],
            stat['total_exec_time'],
            stat['total_exec_count'],
            round(stat['avg_exec_time'], 2) if stat['avg_exec_time'] else 0
        ])
    writer.writerow([])
    
    # Top queries chậm nhất
    writer.writerow(['TOP 10 QUERIES CHẬM NHẤT'])
    writer.writerow(['Database', 'SQL Query', 'Thời gian (ms)', 'Số lần thực thi', 'Thời gian TB (ms)'])
    for query in data['slowest_queries']:
        writer.writerow([
            query['database_name'],
            query['sql_query'],
            query['exec_time_ms'],
            query['exec_count'],
            query['avg_time_per_execution']
        ])
    writer.writerow([])
    
    # Top queries được thực thi nhiều nhất
    writer.writerow(['TOP 10 QUERIES ĐƯỢC THỰC THI NHIỀU NHẤT'])
    writer.writerow(['Database', 'SQL Query', 'Thời gian (ms)', 'Số lần thực thi', 'Thời gian TB (ms)'])
    for query in data['most_executed']:
        writer.writerow([
            query['database_name'],
            query['sql_query'],
            query['exec_time_ms'],
            query['exec_count'],
            query['avg_time_per_execution']
        ])
    
    return response


def export_summary_pdf(data):
    """Xuất báo cáo tổng hợp ra PDF"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bao_cao_tong_hop_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Đăng ký font tiếng Việt
    font_registered = register_vietnamese_font()
    font_name = 'VietnameseFont' if font_registered else 'Helvetica'
    
    # Tạo các style với font tiếng Việt
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        spaceAfter=30,
        alignment=1
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=font_name,
        fontSize=14,
        spaceAfter=12
    )
    story.append(Paragraph("BÁO CÁO TỔNG HỢP SQL LOGS", title_style))
    story.append(Spacer(1, 12))
    
    # Thông tin báo cáo
    info_data = [
        ['Thời gian tạo:', data['summary']['generated_at']],
        ['Database filter:', data['summary']['database_filter'] or 'Tất cả'],
    ]
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Thống kê tổng quan
    story.append(Paragraph("THỐNG KÊ TỔNG QUAN", heading_style))
    summary_data = [
        ['Chỉ số', 'Giá trị'],
        ['Tổng số logs', str(data['summary']['total_logs'])],
        ['Tổng thời gian (ms)', str(data['summary']['total_exec_time'])],
        ['Tổng số lần thực thi', str(data['summary']['total_exec_count'])],
        ['Thời gian TB (ms)', str(data['summary']['avg_exec_time'])],
    ]
    summary_table = Table(summary_data, colWidths=[2*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),  # Set font cho tất cả các dòng
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('FONTSIZE', (0, 1), (-1, -1), 10),  # Font size cho dữ liệu
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Thống kê theo database
    story.append(Paragraph("THỐNG KÊ THEO DATABASE", heading_style))
    db_data = [['Database', 'Số logs', 'Tổng thời gian (ms)', 'Tổng số lần thực thi', 'Thời gian TB (ms)']]
    for stat in data['db_stats']:
        db_data.append([
            stat['database_name'],
            str(stat['count']),
            str(stat['total_exec_time']),
            str(stat['total_exec_count']),
            str(round(stat['avg_exec_time'], 2)) if stat['avg_exec_time'] else '0'
        ])
    
    db_table = Table(db_data, colWidths=[1.2*inch, 0.8*inch, 1.2*inch, 1.2*inch, 1.2*inch])
    db_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),  # Set font cho tất cả các dòng
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(db_table)
    
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def export_detailed_csv(data, database_filter):
    """Xuất báo cáo chi tiết ra CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="bao_cao_chi_tiet_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Header
    writer.writerow(['BÁO CÁO CHI TIẾT SQL LOGS'])
    writer.writerow(['Thời gian tạo:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
    writer.writerow(['Database filter:', database_filter or 'Tất cả'])
    writer.writerow([])
    
    # Data headers
    if data:
        writer.writerow(data[0].keys())
        for row in data:
            writer.writerow(row.values())
    
    return response


def export_detailed_pdf(data, database_filter):
    """Xuất báo cáo chi tiết ra PDF"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bao_cao_chi_tiet_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Đăng ký font tiếng Việt
    font_registered = register_vietnamese_font()
    font_name = 'VietnameseFont' if font_registered else 'Helvetica'
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        spaceAfter=30,
        alignment=1
    )
    story.append(Paragraph("BÁO CÁO CHI TIẾT SQL LOGS", title_style))
    story.append(Spacer(1, 12))
    
    # Thông tin báo cáo
    info_data = [
        ['Thời gian tạo:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
        ['Database filter:', database_filter or 'Tất cả'],
        ['Tổng số records:', str(len(data))],
    ]
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Data table
    if data:
        headers = list(data[0].keys())
        table_data = [headers]
        
        for row in data[:50]:  # Limit to 50 rows for PDF
            table_data.append([str(row[header]) for header in headers])
        
        data_table = Table(table_data, colWidths=[0.8*inch] * len(headers))
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),  # Set font cho tất cả các dòng
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
        ]))
        story.append(data_table)
        
        if len(data) > 50:
            story.append(Spacer(1, 12))
            story.append(Paragraph(f"* Chỉ hiển thị 50 records đầu tiên trong tổng số {len(data)} records", styles['Normal']))
    
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def export_abnormal_csv(data, database_filter):
    """Xuất báo cáo truy vấn bất thường ra CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="bao_cao_bat_thuong_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    writer = csv.writer(response)
    
    # Header
    writer.writerow(['BÁO CÁO TRUY VẤN BẤT THƯỜNG'])
    writer.writerow(['Thời gian tạo:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
    writer.writerow(['Database filter:', database_filter or 'Tất cả'])
    writer.writerow(['Quy tắc: exec_time_ms > 500 VÀ exec_count > 100'])
    writer.writerow([])
    
    # Data headers
    if data:
        writer.writerow(data[0].keys())
        for row in data:
            writer.writerow(row.values())
    
    return response


def export_abnormal_pdf(data, database_filter):
    """Xuất báo cáo truy vấn bất thường ra PDF"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bao_cao_bat_thuong_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Đăng ký font tiếng Việt
    font_registered = register_vietnamese_font()
    font_name = 'VietnameseFont' if font_registered else 'Helvetica'
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=font_name,
        fontSize=18,
        spaceAfter=30,
        alignment=1
    )
    story.append(Paragraph("BÁO CÁO TRUY VẤN BẤT THƯỜNG", title_style))
    story.append(Spacer(1, 12))
    
    # Thông tin báo cáo
    info_data = [
        ['Thời gian tạo:', datetime.now().strftime('%d/%m/%Y %H:%M:%S')],
        ['Database filter:', database_filter or 'Tất cả'],
        ['Quy tắc:', 'exec_time_ms > 500 VÀ exec_count > 100'],
        ['Tổng số records:', str(len(data))],
    ]
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), font_name),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # Data table
    if data:
        headers = list(data[0].keys())
        table_data = [headers]
        
        for row in data:
            table_data.append([str(row[header]) for header in headers])
        
        data_table = Table(table_data, colWidths=[0.7*inch] * len(headers))
        data_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), font_name),  # Set font cho tất cả các dòng
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 6),
        ]))
        story.append(data_table)
    
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response