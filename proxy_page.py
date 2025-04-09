from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit,
    QPushButton, QLabel, QListWidgetItem
)
from PyQt5.QtCore import QTimer
from proxy_engine import ProxyEngine
import threading

class ProxyPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecuLite Proxy")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.full_requests = []

        self.proxy_server = ProxyEngine(
            log_callback=self.log_message,
            intercept_enabled=lambda: self.toggle_intercept_btn.isChecked(),
            intercept_handler=self.capture_intercepted_request
        )

        self.setup_ui()
        self.start_proxy()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Intercept toggle button
        self.toggle_intercept_btn = QPushButton("Intercept: OFF")
        self.toggle_intercept_btn.setCheckable(True)
        self.toggle_intercept_btn.setStyleSheet("background-color: #444; color: white;")
        self.toggle_intercept_btn.clicked.connect(self.toggle_intercept)
        layout.addWidget(self.toggle_intercept_btn)

        # Horizontal split: Intercepted requests list and body view
        content_layout = QHBoxLayout()

        # Left: List of intercepted requests
        self.request_list = QListWidget()
        self.request_list.setStyleSheet("background-color: #2d2d2d; color: white;")
        self.request_list.itemClicked.connect(self.display_request_body)
        content_layout.addWidget(self.request_list, 2)

        # Right: Full body + headers of the selected request
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Full Request Data (Headers + Body):"))

        self.body_view = QTextEdit()
        self.body_view.setReadOnly(True)
        self.body_view.setStyleSheet("background-color: #2d2d2d; color: white;")
        right_layout.addWidget(self.body_view)

        content_layout.addLayout(right_layout, 3)
        layout.addLayout(content_layout)

        # Log output
        layout.addWidget(QLabel("Proxy Logs:"))
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def toggle_intercept(self):
        enabled = self.toggle_intercept_btn.isChecked()
        self.proxy_server.set_intercept(enabled)
        self.toggle_intercept_btn.setText("Intercept: ON" if enabled else "Intercept: OFF")

    def start_proxy(self):
        proxy_thread = threading.Thread(target=self.proxy_server.start, daemon=True)
        proxy_thread.start()
        self.log_message("[+] Proxy started and listening...")

    def capture_intercepted_request(self, request_line, full_request):
        def update_ui():
            item = QListWidgetItem(request_line)
            self.request_list.addItem(item)
            self.full_requests.append(full_request)
            self.log_message(f"[Intercepted] {request_line}")

        QTimer.singleShot(0, update_ui)

    def display_request_body(self, item):
        index = self.request_list.row(item)
        if 0 <= index < len(self.full_requests):
            self.body_view.setPlainText(self.full_requests[index])

    def log_message(self, message):
        self.log_output.append(message)
