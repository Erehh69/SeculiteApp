from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit,
    QPushButton, QLabel, QListWidgetItem
)
from PyQt5.QtCore import QTimer, Qt
from proxy_engine import ProxyEngine
import threading
from urllib.parse import urlparse
import socket
from PyQt5.QtCore import QMetaObject, Qt
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QFileDialog


class ProxyPage(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.main_window = parent
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

        # LEFT: Intercept list and action buttons
        left_layout = QVBoxLayout()
        self.request_list = QListWidget()
        self.request_list.setStyleSheet("background-color: #2d2d2d; color: white;")
        self.request_list.itemClicked.connect(self.on_request_selected)
        left_layout.addWidget(self.request_list)

        # Buttons below list
        list_btn_layout = QHBoxLayout()
        self.clear_btn = QPushButton("Clear Intercepts")
        self.save_btn = QPushButton("Save Intercepts")
        for btn in [self.clear_btn, self.save_btn]:
            btn.setStyleSheet("background-color: #333; color: white;")
        self.clear_btn.clicked.connect(self.clear_intercepts)
        self.save_btn.clicked.connect(self.save_intercepts)
        list_btn_layout.addWidget(self.clear_btn)
        list_btn_layout.addWidget(self.save_btn)
        left_layout.addLayout(list_btn_layout)

        main_layout.addLayout(left_layout, 2)

        # RIGHT: Request editor and action buttons
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Request Details (edit before forwarding):"))

        self.request_editor = QTextEdit()
        self.request_editor.setStyleSheet("background-color: #2d2d2d; color: white;")
        right_layout.addWidget(self.request_editor)

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

    def capture_intercepted_request(self, request_line, full_request, continue_callback):
        print(f"[DEBUG] capture_intercepted_request() called with: {request_line}")
        self._pending_request_line = request_line
        self._pending_full_request = full_request
        self._pending_continue_callback = continue_callback  # Store the callback for later use
        QTimer.singleShot(0, self.update_ui)


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

            try:
                if hasattr(self, "_pending_continue_callback"):
                    self._pending_continue_callback(edited)
                    self.log_message("[✓] Request forwarded via proxy engine.")
                else:
                    self.log_message("[!] No pending request to forward.")
            except Exception as e:
                self.log_message(f"[!] Error forwarding: {e}")

            self.remove_request(current_row)

    def clear_intercepts(self):
        self.intercepted_requests.clear()
        self.request_list.clear()
        self.request_editor.clear()
        self.log_message("[✂] Intercept list cleared.")

    def save_intercepts(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save Intercepts", "", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, "w") as f:
                    for line, full_req in self.intercepted_requests:
                        f.write(f"### {line}\n{full_req}\n\n")
                self.log_message(f"[💾] Saved intercepted requests to: {filename}")
            except Exception as e:
                self.log_message(f"[!] Error saving intercepts: {e}")

    def update_ui(self):
        request_line = self._pending_request_line
        full_request = self._pending_full_request
        print(f"[DEBUG] update_ui() running. Request Line: {request_line}")

        method, path, _ = request_line.split()
        display_text = f"{method} {path}"

        self.intercepted_requests.append((request_line, full_request))
        item = QListWidgetItem(display_text)
        self.request_list.addItem(item)
        self.request_list.repaint()
        self.log_message(f"[Intercepted] {display_text}")

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
            full_req = self.intercepted_requests[current_row][1]
            self.log_message(f"[⇄] Sent to Repeater: {req_line}")
            if self.main_window and hasattr(self.main_window, "repeater_page"):
                self.main_window.repeater_page.add_session(full_req)
                self.main_window.sidebar.setCurrentRow(3)  # Switch to Repeater tab

    #INTRUDER

    def set_intruder_page(self, intruder_page):
        self.intruder_page = intruder_page

    def send_to_intruder(self):
        current_row = self.request_list.currentRow()
        if current_row >= 0:
            req_line, full_request = self.intercepted_requests[current_row]
            self.log_message(f"[⚔] Sent to Intruder: {req_line}")
            if hasattr(self, 'intruder_page'):
                self.intruder_page.add_intruder_session(req_line, full_request)
                self.main_window.sidebar.setCurrentRow(4)


    def remove_request(self, index):
        self.intercepted_requests.pop(index)
        self.request_list.takeItem(index)
        self.request_editor.clear()

    def log_message(self, message):
        self.log_output.append(message)
