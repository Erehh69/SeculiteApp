from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QListWidget
)
from PyQt5.QtCore import Qt

class ScannerPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        # Title
        title = QLabel("Vulnerability Scanner")
        title.setStyleSheet("color: #1ABC9C; font-weight: bold; font-size: 18px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Target URL
        target_label = QLabel("Target URL:")
        target_label.setStyleSheet("color: #ECF0F1;")
        layout.addWidget(target_label)

        self.target_input = QLineEdit()
        self.target_input.setStyleSheet("background-color: #34495E; color: #ECF0F1;")
        self.target_input.setPlaceholderText("Enter the target URL...")
        layout.addWidget(self.target_input)

        # Scan Type
        scan_label = QLabel("Scan Type:")
        scan_label.setStyleSheet("color: #ECF0F1;")
        layout.addWidget(scan_label)

        self.scan_type = QComboBox()
        self.scan_type.addItems(["XSS", "SQL Injection", "CSRF", "Directory Traversal"])
        self.scan_type.setStyleSheet("background-color: #34495E; color: #ECF0F1;")
        layout.addWidget(self.scan_type)

        # Start Scan Button
        scan_button = QPushButton("Start Scan")
        scan_button.setStyleSheet("background-color: #1ABC9C; color: #2C3E50; padding: 10px; border-radius: 4px;")
        layout.addWidget(scan_button)

        # Scan Results
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("background-color: #2C3E50; color: #ECF0F1;")
        layout.addWidget(self.results_list)

        # Example Scan Results (Dummy Data)
        example_results = [
            "XSS: <script>alert('XSS Attack')</script> found at http://example.com/search",
            "SQL Injection: ' OR 1=1 -- vulnerability detected at http://example.com/login",
            "CSRF: Potential CSRF attack found on http://example.com/change-password",
            "Directory Traversal: ../../../../etc/passwd accessed at http://example.com/files/../admin",
            "SQL Injection: '; DROP TABLE users; -- on http://example.com/delete-account",
            "XSS: <img src='x' onerror='alert(1)'> on http://example.com/profile",
            "Directory Traversal: ../../../etc/shadow at http://example.com/download",
            "CSRF: Missing token in form at http://example.com/transfer-funds"
        ]

        for result in example_results:
            self.results_list.addItem(result)

        self.setLayout(layout)
