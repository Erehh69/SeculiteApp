from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
import logging
from proxy_handler import ThreadedHTTPServer, ProxyHandler
import socketserver

class ProxyPage(QWidget):
    def __init__(self):
        super().__init__()
        self.proxy_thread = None
        self.init_ui()
        self.start_proxy()  # Auto-start proxy on launch

    def init_ui(self):
        layout = QVBoxLayout()
        control_layout = QHBoxLayout()

        # Status label
        self.status_label = QLabel("Proxy Status: Running")
        control_layout.addWidget(self.status_label)

        # Start/Stop Proxy Button
        self.start_proxy_button = QPushButton("Stop Proxy")
        self.start_proxy_button.clicked.connect(self.toggle_proxy)
        control_layout.addWidget(self.start_proxy_button)
        layout.addLayout(control_layout)

        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def toggle_proxy(self):
        """Stops or starts the proxy based on current state"""
        if self.proxy_thread and self.proxy_thread.isRunning():
            self.stop_proxy()
        else:
            self.start_proxy()

    def start_proxy(self):
        """Starts the proxy server"""
        self.log_output.append("Starting Proxy Server...")
        logging.basicConfig(level=logging.DEBUG)

        self.proxy_thread = ProxyServerThread(self)
        self.proxy_thread.start()

        self.start_proxy_button.setText("Stop Proxy")
        self.status_label.setText("Proxy Status: Running")

    def stop_proxy(self):
        """Stops the proxy server"""
        if self.proxy_thread and self.proxy_thread.isRunning():
            self.proxy_thread.terminate()  # Terminate the thread
            self.proxy_thread.wait()
        
        self.log_output.append("Proxy Server Stopped.")
        self.start_proxy_button.setText("Start Proxy")
        self.status_label.setText("Proxy Status: Stopped")

    def log_to_ui(self, log_message):
        self.log_output.append(log_message)


class ProxyServerThread(QThread):
    def __init__(self, proxy_page):
        super().__init__()
        self.proxy_page = proxy_page

    def run(self):
        try:
            server_address = ('127.0.0.1', 8080)
            httpd = ThreadedHTTPServer(server_address, ProxyHandler)
            logging.debug("Proxy server started, awaiting connections...")
            httpd.serve_forever()
        except Exception as e:
            self.proxy_page.log_to_ui(f"Error: {str(e)}")
