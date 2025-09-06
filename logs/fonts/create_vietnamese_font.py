#!/usr/bin/env python3
"""
Script tạo font TTF đơn giản hỗ trợ tiếng Việt cho ReportLab
"""

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
import os

def create_vietnamese_font_mapping():
    """Tạo mapping font cho tiếng Việt"""
    
    # Tạo font mapping cho các ký tự tiếng Việt cơ bản
    vietnamese_chars = {
        'A': 'ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬ',
        'a': 'àáảãạăằắẳẵặâầấẩẫậ',
        'E': 'ÈÉẺẼẸÊỀẾỂỄỆ',
        'e': 'èéẻẽẹêềếểễệ',
        'I': 'ÌÍỈĨỊ',
        'i': 'ìíỉĩị',
        'O': 'ÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢ',
        'o': 'òóỏõọôồốổỗộơờớởỡợ',
        'U': 'ÙÚỦŨỤƯỪỨỬỮỰ',
        'u': 'ùúủũụưừứửữự',
        'Y': 'ỲÝỶỸỴ',
        'y': 'ỳýỷỹỵ',
        'D': 'Đ',
        'd': 'đ'
    }
    
    return vietnamese_chars

def register_fonts():
    """Đăng ký font cho ReportLab"""
    try:
        # Thử sử dụng font hệ thống có sẵn
        # Windows thường có font Arial Unicode MS
        font_paths = [
            'C:/Windows/Fonts/arial.ttf',
            'C:/Windows/Fonts/arialuni.ttf', 
            'C:/Windows/Fonts/tahoma.ttf',
            'C:/Windows/Fonts/calibri.ttf'
        ]
        
        registered_font = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    pdfmetrics.registerFont(TTFont('VietnameseFont', font_path))
                    registered_font = font_path
                    print(f"✅ Đã đăng ký font: {font_path}")
                    break
                except Exception as e:
                    print(f"❌ Không thể đăng ký font {font_path}: {e}")
                    continue
        
        if not registered_font:
            # Fallback: sử dụng font mặc định với encoding UTF-8
            print("⚠️ Không tìm thấy font Unicode, sử dụng font mặc định")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Lỗi đăng ký font: {e}")
        return False

if __name__ == "__main__":
    print("=== ĐĂNG KÝ FONT TIẾNG VIỆT CHO REPORTLAB ===")
    success = register_fonts()
    if success:
        print("✅ Hoàn thành đăng ký font!")
    else:
        print("❌ Không thể đăng ký font!")
