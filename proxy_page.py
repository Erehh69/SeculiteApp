from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit,
    QPushButton, QLabel, QListWidgetItem
)
from PyQt5.QtCore import QTimer, Qt
from proxy_engine import ProxyEngine
import threading
from urllib.parse import urlparse
import socket

class ProxyPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecuLite Proxy")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.intercepted_requests = []  # store all (req_line, full_request)

        self.proxy_server = ProxyEngine(
            log_callback=self.log_message,
            intercept_enabled=lambda: self.toggle_intercept_btn.isChecked(),
            intercept_handler=self.capture_intercepted_request
        )

        self.setup_ui()
        self.start_proxy()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Intercept toggle
        self.toggle_intercept_btn = QPushButton("Intercept: OFF")
        self.toggle_intercept_btn.setCheckable(True)
        self.toggle_intercept_btn.setStyleSheet("background-color: #444; color: white;")
        self.toggle_intercept_btn.clicked.connect(self.toggle_intercept)
        layout.addWidget(self.toggle_intercept_btn)

        # Horizontal split layout
        main_layout = QHBoxLayout()

        # LEFT: List of intercepted requests
        self.request_list = QListWidget()
        self.request_list.setStyleSheet("background-color: #2d2d2d; color: white;")
        self.request_list.itemClicked.connect(self.on_request_selected)
        main_layout.addWidget(self.request_list, 2)

        # RIGHT: Request editor and buttons
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Request Details (edit before forwarding):"))

        self.request_editor = QTextEdit()
        self.request_editor.setStyleSheet("background-color: #2d2d2d; color: white;")
        right_layout.addWidget(self.request_editor)

        # Buttons: Forward / Drop / Send to Repeater / Intruder
        button_layout = QHBoxLayout()
        self.forward_btn = QPushButton("Forward")
        self.drop_btn = QPushButton("Drop")
        self.to_repeater_btn = QPushButton("Send to Repeater")
        self.to_intruder_btn = QPushButton("Send to Intruder")

        self.forward_btn.clicked.connect(self.forward_request)
        self.drop_btn.clicked.connect(self.drop_request)
        self.to_repeater_btn.clicked.connect(self.send_to_repeater)
        self.to_intruder_btn.clicked.connect(self.send_to_intruder)

        for btn in [self.forward_btn, self.drop_btn, self.to_repeater_btn, self.to_intruder_btn]:
            btn.setStyleSheet("background-color: #444; color: white;")
            button_layout.addWidget(btn)

        right_layout.addLayout(button_layout)
        main_layout.addLayout(right_layout, 3)

        layout.addLayout(main_layout)

        # Log output
        layout.addWidget(QLabel("Logs:"))
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
        threading.Thread(target=self.proxy_server.start, daemon=True).start()
        self.log_message("[+] Proxy started and listening...")

    def capture_intercepted_request(self, request_line, full_request):
        def update_ui():
            self.intercepted_requests.append((request_line, full_request))
            self.request_list.addItem(request_line)
            self.log_message(f"[Intercepted] {request_line}")

        QTimer.singleShot(0, update_ui)

    def on_request_selected(self, item):
        index = self.request_list.row(item)
        if 0 <= index < len(self.intercepted_requests):
            request_data = self.intercepted_requests[index][1]
            self.request_editor.setPlainText(request_data)

    def forward_request(self):
        current_row = self.request_list.currentRow()
        if current_row >= 0:
            edited = self.request_editor.toPlainText()
            req_line = self.intercepted_requests[current_row][0]
            self.log_message(f"[→] Forwarding:\n{req_line}")

            # Parse and send manually
            try:
                lines = edited.split("\r\n")
                request_line = lines[0]
                method, path, _ = request_line.split()
                host = ""
                for line in lines:
                    if line.lower().startswith("host:"):
                        host = line.split(":", 1)[1].strip()
                        break

                parsed = urlparse("http://" + host + path)
                target_host = parsed.hostname
                target_port = parsed.port or 80

                final_request = edited.encode()

                with socket.create_connection((target_host, target_port)) as sock:
                    sock.sendall(final_request)
                    self.log_message(f"[→] Sent to {target_host}:{target_port}")
                    response = sock.recv(4096)
                    snippet = response[:300].decode(errors='ignore')
                    self.log_message(f"[<] Response snippet:\n{snippet.strip()}")

            except Exception as e:
                self.log_message(f"[!] Error forwarding: {e}")

            self.remove_request(current_row)


    def drop_request(self):
        current_row = self.request_list.currentRow()
        if current_row >= 0:
            req_line = self.intercepted_requests[current_row][0]
            self.log_message(f"[✖] Dropped: {req_line}")
            self.remove_request(current_row)

    def send_to_repeater(self):
        current_row = self.request_list.currentRow()
        if current_row >= 0:
            req_line = self.intercepted_requests[current_row][0]
            self.log_message(f"[⇄] Sent to Repeater: {req_line}")
            # TODO: Hook with repeater window

    def send_to_intruder(self):
        current_row = self.request_list.currentRow()
        if current_row >= 0:
            req_line = self.intercepted_requests[current_row][0]
            self.log_message(f"[⚔] Sent to Intruder: {req_line}")
            # TODO: Hook with intruder window

    def remove_request(self, index):
        self.intercepted_requests.pop(index)
        self.request_list.takeItem(index)
        self.request_editor.clear()

    def log_message(self, message):
        self.log_output.append(message)
