from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QSyntaxHighlighter, QTextCharFormat, QFont, QColor


class SQLHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for SQL queries."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []

        # SQL Keywords format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor(86, 156, 214))  # Blue
        keyword_format.setFontWeight(QFont.Bold)

        # SQL keywords
        keywords = [
            "SELECT", "FROM", "WHERE", "JOIN", "INNER", "LEFT", "RIGHT", "OUTER",
            "ON", "GROUP", "BY", "ORDER", "HAVING", "LIMIT", "OFFSET",
            "INSERT", "INTO", "VALUES", "UPDATE", "SET", "DELETE",
            "CREATE", "TABLE", "VIEW", "INDEX", "DROP", "ALTER",
            "AS", "AND", "OR", "NOT", "IN", "LIKE", "BETWEEN", "IS", "NULL",
            "DISTINCT", "COUNT", "SUM", "AVG", "MIN", "MAX",
            "CASE", "WHEN", "THEN", "ELSE", "END",
            "UNION", "ALL", "EXISTS", "WITH", "RECURSIVE",
            "ASC", "DESC", "NULLS", "FIRST", "LAST",
            "CROSS", "NATURAL", "USING", "PRIMARY", "KEY", "FOREIGN",
            "REFERENCES", "UNIQUE", "CHECK", "DEFAULT", "CONSTRAINT",
            "VARCHAR", "INTEGER", "INT", "BIGINT", "DOUBLE", "FLOAT",
            "BOOLEAN", "DATE", "TIMESTAMP", "TIME", "INTERVAL"
        ]

        for word in keywords:
            pattern = QRegularExpression(f"\\b{word}\\b", QRegularExpression.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, keyword_format))

        # DuckDB specific functions
        function_format = QTextCharFormat()
        function_format.setForeground(QColor(220, 220, 170))  # Light yellow

        functions = [
            "read_csv", "read_csv_auto", "read_parquet", "read_json",
            "read_arrow", "COPY", "DESCRIBE", "SHOW", "PRAGMA"
        ]

        for func in functions:
            pattern = QRegularExpression(f"\\b{func}\\b", QRegularExpression.CaseInsensitiveOption)
            self.highlighting_rules.append((pattern, function_format))

        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor(181, 206, 168))  # Light green
        number_pattern = QRegularExpression(r"\b\d+\.?\d*\b")
        self.highlighting_rules.append((number_pattern, number_format))

        # String literals (single quotes)
        string_format = QTextCharFormat()
        string_format.setForeground(QColor(206, 145, 120))  # Orange/salmon
        single_quote_pattern = QRegularExpression(r"'[^']*'")
        self.highlighting_rules.append((single_quote_pattern, string_format))

        # String literals (double quotes - for identifiers)
        identifier_format = QTextCharFormat()
        identifier_format.setForeground(QColor(206, 145, 120))  # Same as strings
        double_quote_pattern = QRegularExpression(r'"[^"]*"')
        self.highlighting_rules.append((double_quote_pattern, identifier_format))

        # Single-line comments (-- style)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor(106, 153, 85))  # Green
        comment_format.setFontItalic(True)
        comment_pattern = QRegularExpression(r"--[^\n]*")
        self.highlighting_rules.append((comment_pattern, comment_format))

        # Multi-line comments (/* */ style)
        self.multi_line_comment_format = QTextCharFormat()
        self.multi_line_comment_format.setForeground(QColor(106, 153, 85))
        self.multi_line_comment_format.setFontItalic(True)

        self.comment_start_expression = QRegularExpression(r"/\*")
        self.comment_end_expression = QRegularExpression(r"\*/")

    def highlightBlock(self, text):
        """Apply syntax highlighting to a block of text."""
        # Apply all single-line rules
        for pattern, format in self.highlighting_rules:
            iterator = pattern.globalMatch(text)
            while iterator.hasNext():
                match = iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)

        # Handle multi-line comments
        self.setCurrentBlockState(0)

        start_index = 0
        if self.previousBlockState() != 1:
            match = self.comment_start_expression.match(text)
            start_index = match.capturedStart() if match.hasMatch() else -1

        while start_index >= 0:
            match = self.comment_end_expression.match(text, start_index)
            end_index = match.capturedStart() if match.hasMatch() else -1

            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + match.capturedLength()

            self.setFormat(start_index, comment_length, self.multi_line_comment_format)

            match = self.comment_start_expression.match(text, start_index + comment_length)
            start_index = match.capturedStart() if match.hasMatch() else -1
