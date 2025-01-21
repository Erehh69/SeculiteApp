import requests
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTextEdit, QLabel, QLineEdit

class ScannerPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Scanner Module"))
        layout.addWidget(QLabel("Enter Target URL:"))
        self.url_input = QLineEdit()
        layout.addWidget(self.url_input)

        self.scan_button = QPushButton("Start Scan")
        self.scan_button.clicked.connect(self.start_scan)
        layout.addWidget(self.scan_button)

        self.scan_results = QTextEdit()
        self.scan_results.setReadOnly(True)
        layout.addWidget(self.scan_results)

        self.setLayout(layout)

    def start_scan(self):
        target_url = self.url_input.text()
        if not target_url:
            self.scan_results.setText("Please enter a target URL.")
            return

        results = self.run_scanner(target_url)
        self.scan_results.setText("\n".join(results))

    def run_scanner(self, target_url):
        results = []
        try:
            response = requests.get(target_url)
            if "<!DOCTYPE" in response.text:
                results.append("XML vulnerability detected.")
            else:
                results.append("No XML vulnerabilities detected.")
        except Exception as e:
            results.append(f"Error scanning URL: {e}")
        return results
