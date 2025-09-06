#!/usr/bin/env python3
"""
Module phân tích SQL để gợi ý tối ưu hóa
"""

import re
from typing import List, Dict, Optional

class SQLAnalyzer:
    """Phân tích câu lệnh SQL để đưa ra gợi ý tối ưu hóa"""
    
    def __init__(self):
        # Các từ khóa SQL phổ biến
        self.sql_keywords = {
            'SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN',
            'IS', 'NULL', 'EXISTS', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'OUTER',
            'ON', 'GROUP', 'BY', 'HAVING', 'ORDER', 'LIMIT', 'OFFSET', 'UNION',
            'INSERT', 'UPDATE', 'DELETE', 'CREATE', 'ALTER', 'DROP', 'INDEX'
        }
        
        # Các toán tử so sánh
        self.comparison_operators = ['=', '!=', '<>', '<', '>', '<=', '>=', 'LIKE', 'NOT LIKE', 'IN', 'NOT IN', 'BETWEEN', 'NOT BETWEEN']
        
        # Các hàm SQL phổ biến
        self.sql_functions = {
            'COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'UPPER', 'LOWER', 'SUBSTRING',
            'LENGTH', 'TRIM', 'CONCAT', 'COALESCE', 'CASE', 'WHEN', 'THEN', 'ELSE', 'END'
        }
    
    def analyze_sql(self, sql_query: str) -> Dict:
        """
        Phân tích câu lệnh SQL và đưa ra gợi ý tối ưu hóa
        
        Args:
            sql_query: Câu lệnh SQL cần phân tích
            
        Returns:
            Dict chứa thông tin phân tích và gợi ý
        """
        if not sql_query or not sql_query.strip():
            return {
                'status': 'error',
                'message': 'Câu lệnh SQL trống',
                'suggestions': ['Khuyến nghị xem xét thủ công']
            }
        
        try:
            # Chuẩn hóa SQL
            normalized_sql = self._normalize_sql(sql_query)
            
            # Phân tích các thành phần
            analysis = {
                'original_sql': sql_query,
                'normalized_sql': normalized_sql,
                'query_type': self._get_query_type(normalized_sql),
                'where_clause': self._extract_where_clause(normalized_sql),
                'where_fields': [],
                'suggestions': [],
                'status': 'success'
            }
            
            # Phân tích mệnh đề WHERE
            if analysis['where_clause']:
                analysis['where_fields'] = self._extract_where_fields(analysis['where_clause'])
                analysis['suggestions'] = self._generate_suggestions(analysis['where_fields'])
            
            # Nếu không có WHERE hoặc không phân tích được
            if not analysis['where_fields']:
                analysis['suggestions'] = ['Khuyến nghị xem xét thủ công']
            
            return analysis
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Lỗi phân tích SQL: {str(e)}',
                'suggestions': ['Khuyến nghị xem xét thủ công']
            }
    
    def _normalize_sql(self, sql: str) -> str:
        """Chuẩn hóa câu lệnh SQL"""
        # Loại bỏ comment
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        # Chuẩn hóa khoảng trắng
        sql = re.sub(r'\s+', ' ', sql.strip())
        
        # Chuyển thành chữ hoa các từ khóa SQL
        words = sql.split()
        normalized_words = []
        
        for word in words:
            if word.upper() in self.sql_keywords:
                normalized_words.append(word.upper())
            else:
                normalized_words.append(word)
        
        return ' '.join(normalized_words)
    
    def _get_query_type(self, sql: str) -> str:
        """Xác định loại câu lệnh SQL"""
        sql_upper = sql.upper().strip()
        
        if sql_upper.startswith('SELECT'):
            return 'SELECT'
        elif sql_upper.startswith('INSERT'):
            return 'INSERT'
        elif sql_upper.startswith('UPDATE'):
            return 'UPDATE'
        elif sql_upper.startswith('DELETE'):
            return 'DELETE'
        else:
            return 'UNKNOWN'
    
    def _extract_where_clause(self, sql: str) -> Optional[str]:
        """Trích xuất mệnh đề WHERE từ SQL"""
        # Tìm mệnh đề WHERE
        where_match = re.search(r'WHERE\s+(.+?)(?:\s+(?:GROUP|ORDER|HAVING|LIMIT|UNION)|$)', sql, re.IGNORECASE | re.DOTALL)
        
        if where_match:
            where_clause = where_match.group(1).strip()
            # Loại bỏ các từ khóa SQL ở cuối nếu có
            where_clause = re.sub(r'\s+(?:GROUP|ORDER|HAVING|LIMIT|UNION).*$', '', where_clause, flags=re.IGNORECASE)
            return where_clause.strip()
        
        return None
    
    def _extract_where_fields(self, where_clause: str) -> List[str]:
        """Trích xuất các trường trong mệnh đề WHERE"""
        fields = []
        
        # Chuẩn hóa WHERE clause
        where_clause = where_clause.strip()
        
        # Pattern để tìm các trường trong WHERE
        # Tìm pattern: field operator value
        # Ví dụ: id = 1, name LIKE '%john%', status IN (...)
        
        # Pattern 1: Trường với toán tử so sánh đơn giản
        # Ví dụ: id = 1, price > 100
        simple_pattern = r'(\w+)\s*(?:=|!=|<>|<|>|<=|>=)\s*[^\s]'
        matches = re.findall(simple_pattern, where_clause, re.IGNORECASE)
        for match in matches:
            field = match.strip()
            if self._is_valid_field_name(field):
                fields.append(field)
        
        # Pattern 2: Trường với LIKE
        # Ví dụ: name LIKE '%john%'
        like_pattern = r'(\w+)\s+(?:NOT\s+)?LIKE\s+'
        matches = re.findall(like_pattern, where_clause, re.IGNORECASE)
        for match in matches:
            field = match.strip()
            if self._is_valid_field_name(field):
                fields.append(field)
        
        # Pattern 3: Trường với IN
        # Ví dụ: status IN ('active', 'pending')
        in_pattern = r'(\w+)\s+(?:NOT\s+)?IN\s*\('
        matches = re.findall(in_pattern, where_clause, re.IGNORECASE)
        for match in matches:
            field = match.strip()
            if self._is_valid_field_name(field):
                fields.append(field)
        
        # Pattern 4: Trường với BETWEEN
        # Ví dụ: created_at BETWEEN '2023-01-01' AND '2023-12-31'
        between_pattern = r'(\w+)\s+(?:NOT\s+)?BETWEEN\s+'
        matches = re.findall(between_pattern, where_clause, re.IGNORECASE)
        for match in matches:
            field = match.strip()
            if self._is_valid_field_name(field):
                fields.append(field)
        
        # Pattern 5: Trường với IS NULL/IS NOT NULL
        # Ví dụ: email IS NULL, phone IS NOT NULL
        null_pattern = r'(\w+)\s+IS\s+(?:NOT\s+)?NULL'
        matches = re.findall(null_pattern, where_clause, re.IGNORECASE)
        for match in matches:
            field = match.strip()
            if self._is_valid_field_name(field):
                fields.append(field)
        
        # Loại bỏ trùng lặp và sắp xếp
        return sorted(list(set(fields)))
    
    def _is_valid_field_name(self, field: str) -> bool:
        """Kiểm tra xem có phải là tên trường hợp lệ không"""
        if not field or len(field) == 0:
            return False
        
        # Loại bỏ các từ khóa SQL
        if field.upper() in self.sql_keywords:
            return False
        
        # Loại bỏ các hàm SQL
        if field.upper() in self.sql_functions:
            return False
        
        # Loại bỏ các giá trị số
        if field.isdigit():
            return False
        
        # Loại bỏ các giá trị chuỗi (bắt đầu bằng dấu nháy)
        if field.startswith("'") or field.startswith('"'):
            return False
        
        return True
    
    def _generate_suggestions(self, fields: List[str]) -> List[str]:
        """Tạo gợi ý tối ưu hóa dựa trên các trường"""
        suggestions = []
        
        if not fields:
            return ['Khuyến nghị xem xét thủ công']
        
        # Gợi ý index cho từng trường
        for field in fields:
            suggestions.append(f"Thêm index trên [{field}]")
        
        # Gợi ý composite index nếu có nhiều trường
        if len(fields) > 1:
            suggestions.append(f"Xem xét composite index trên [{', '.join(fields)}]")
        
        # Gợi ý chung
        suggestions.extend([
            "Kiểm tra execution plan",
            "Xem xét phân vùng bảng nếu dữ liệu lớn",
            "Cập nhật thống kê bảng"
        ])
        
        return suggestions
    
    def get_optimization_summary(self, analysis: Dict) -> str:
        """Tạo tóm tắt gợi ý tối ưu hóa"""
        if analysis['status'] != 'success':
            return "Khuyến nghị xem xét thủ công"
        
        suggestions = analysis.get('suggestions', [])
        if not suggestions:
            return "Khuyến nghị xem xét thủ công"
        
        # Lấy gợi ý index đầu tiên làm tóm tắt chính
        index_suggestions = [s for s in suggestions if s.startswith("Thêm index")]
        if index_suggestions:
            return index_suggestions[0]
        
        return suggestions[0] if suggestions else "Khuyến nghị xem xét thủ công"


# Test function
def test_sql_analyzer():
    """Test SQL analyzer"""
    analyzer = SQLAnalyzer()
    
    test_queries = [
        "SELECT * FROM users WHERE id = 1",
        "SELECT * FROM orders WHERE customer_id = 123 AND status = 'pending'",
        "SELECT * FROM products WHERE price > 100 AND category IN ('electronics', 'books')",
        "SELECT * FROM logs WHERE created_at BETWEEN '2023-01-01' AND '2023-12-31'",
        "SELECT * FROM users WHERE name LIKE '%john%' AND email IS NOT NULL",
        "INVALID SQL QUERY",
        ""
    ]
    
    print("=== TEST SQL ANALYZER ===")
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        analysis = analyzer.analyze_sql(query)
        print(f"   Status: {analysis['status']}")
        print(f"   Fields: {analysis.get('where_fields', [])}")
        print(f"   Suggestions: {analysis.get('suggestions', [])}")
        print(f"   Summary: {analyzer.get_optimization_summary(analysis)}")


if __name__ == "__main__":
    test_sql_analyzer()
