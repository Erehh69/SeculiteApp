from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QTextEdit
from PyQt5.QtCore import Qt
from proxy_engine import ProxyEngine

class ProxyServer(QWidget):
    def __init__(self, log_callback=print):
        super().__init__()

        self.proxy = ProxyEngine(log_callback=self.log_message)  # Use log_message to update the log area

        layout = QVBoxLayout()

        # UI Elements for intercept control
        self.intercept_button = QPushButton("Intercept: OFF")
        self.intercept_button.setCheckable(True)
        self.intercept_button.clicked.connect(self.toggle_intercept)
        layout.addWidget(self.intercept_button)

        # Log area for displaying proxy activities
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        layout.addWidget(self.log_area)

        # Dummy request list for demonstration
        self.request_list = QListWidget()
        dummy_requests = [
            ("GET", "/home", "200 OK"),
            ("POST", "/login", "302 Redirect")
        ]
        for method, path, status in dummy_requests:
            self.request_list.addItem(f"{method} {path} - {status}")

        self.setLayout(layout)

    def toggle_intercept(self):
        """Toggle intercept button to start or stop the proxy server."""
        if self.intercept_button.isChecked():
            self.intercept_button.setText("Intercept: ON")
            self.intercept_button.setStyleSheet("background-color: #E74C3C; color: white;")  # Change color to indicate ON
            self.proxy.start()  # Start the proxy server
        else:
            self.intercept_button.setText("Intercept: OFF")
            self.intercept_button.setStyleSheet("background-color: #3498DB; color: white;")  # Change color to indicate OFF
            self.proxy.stop()  # Stop the proxy server

    def log_message(self, message):
        """Update the log area with incoming proxy messages."""
        self.log_area.append(message)
