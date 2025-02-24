from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QTextEdit, QFileDialog
)
from PyQt5.QtCore import Qt

class ReporterPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Title
        title = QLabel("Request Reports")
        title.setStyleSheet("color: #1ABC9C; font-weight: bold; font-size: 18px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Request History List
        self.history_list = QListWidget()
        self.history_list.setStyleSheet("background-color: #2C3E50; color: #ECF0F1;")
        layout.addWidget(self.history_list)

        # Report Details
        self.report_details = QTextEdit()
        self.report_details.setStyleSheet("background-color: #34495E; color: #ECF0F1;")
        self.report_details.setReadOnly(True)
        layout.addWidget(self.report_details)

        # Export Report Button
        export_button = QPushButton("Export Report")
        export_button.setStyleSheet("background-color: #1ABC9C; color: #2C3E50; padding: 10px; border-radius: 4px;")
        export_button.clicked.connect(self.export_report)
        layout.addWidget(export_button)

        self.setLayout(layout)

        # Add sample reports (dummy data for example)
        self.add_report(
            "Scan Date: 2025-02-17\n"
            "Scan Type: SQL Injection\n"
            "Target URL: http://example.com/login\n"
            "Payload Used: ' OR 1=1 --\n"
            "Vulnerability Detected: Unfiltered input allowing SQL injection\n"
            "Severity: High\n"
            "Description: The 'username' field is vulnerable to SQL injection. The payload"
            "'OR 1=1 --' returns all records in the database."
            "Remediation: Sanitize user input, use prepared statements and parameterized queries.\n"
            "-----------------------------------\n"
        )

        self.add_report(
            "Scan Date: 2025-02-17\n"
            "Scan Type: XSS\n"
            "Target URL: http://example.com/search\n"
            "Payload Used: <script>alert('XSS Attack')</script>\n"
            "Vulnerability Detected: Cross-site scripting vulnerability allowing script execution\n"
            "Severity: Medium\n"
            "Description: The search field is not sanitizing input, allowing attackers to inject arbitrary JavaScript.\n"
            "Remediation: Implement input sanitization and encoding of special characters like <, >, and '.\n"
            "-----------------------------------\n"
        )

        self.add_report(
            "Scan Date: 2025-02-17\n"
            "Scan Type: CSRF\n"
            "Target URL: http://example.com/transfer-funds\n"
            "Payload Used: Missing CSRF token\n"
            "Vulnerability Detected: Lack of CSRF token in form submissions\n"
            "Severity: High\n"
            "Description: The form on the transfer funds page does not include a CSRF token, allowing attackers to perform unauthorized actions.\n"
            "Remediation: Implement CSRF tokens in all state-changing requests.\n"
            "-----------------------------------\n"
        )

        self.add_report(
            "Scan Date: 2025-02-17\n"
            "Scan Type: Directory Traversal\n"
            "Target URL: http://example.com/files/../admin\n"
            "Payload Used: ../../../../etc/passwd\n"
            "Vulnerability Detected: Directory traversal vulnerability allows access to sensitive files\n"
            "Severity: High\n"
            "Description: The application does not sanitize input, allowing an attacker to access restricted files.\n"
            "Remediation: Validate and sanitize user input, ensure path traversal is prevented.\n"
            "-----------------------------------\n"
        )

    def add_report(self, report_text):
        self.history_list.addItem(report_text)
        self.report_details.setPlainText(report_text)

    def export_report(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Report", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.report_details.toPlainText())
