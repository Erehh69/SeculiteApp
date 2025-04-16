# repeater_page.py

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QTextEdit, QPushButton, QLabel, QListWidgetItem
)
from PyQt5.QtCore import pyqtSlot

class RepeaterPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Repeater")
        self.setStyleSheet("background-color: #1e1e1e; color: white;")

        self.sessions = []  # Stores (request_text, response_text)

        layout = QHBoxLayout()
        self.setLayout(layout)

        # Left: Session list
        self.session_list = QListWidget()
        self.session_list.setStyleSheet("background-color: #2d2d2d; color: white;")
        self.session_list.itemClicked.connect(self.load_selected_session)
        layout.addWidget(self.session_list, 1)

        # Right: Request/Response Editor
        right_layout = QVBoxLayout()

        right_layout.addWidget(QLabel("Request:"))
        self.request_editor = QTextEdit()
        self.request_editor.setStyleSheet("background-color: #2d2d2d; color: white;")
        right_layout.addWidget(self.request_editor)

        send_btn = QPushButton("Send")
        send_btn.setStyleSheet("background-color: #444; color: white;")
        send_btn.clicked.connect(self.send_request)
        right_layout.addWidget(send_btn)

        right_layout.addWidget(QLabel("Response:"))
        self.response_view = QTextEdit()
        self.response_view.setReadOnly(True)
        self.response_view.setStyleSheet("background-color: #2d2d2d; color: white;")
        right_layout.addWidget(self.response_view)

        layout.addLayout(right_layout, 3)

    def add_session(self, request_text):
        """Add a new repeater session with the request text."""
        self.sessions.append((request_text, ""))  # Empty response initially
        display_title = self._generate_session_title(request_text)
        item = QListWidgetItem(display_title)
        self.session_list.addItem(item)
        self.session_list.setCurrentItem(item)
        self.request_editor.setPlainText(request_text)
        self.response_view.clear()

    def _generate_session_title(self, request_text):
        """Extract method and path for display title."""
        try:
            first_line = request_text.splitlines()[0]
            parts = first_line.split()
            if len(parts) >= 2:
                return f"{parts[0]} {parts[1]}"
            return first_line
        except:
            return "New Session"

    def load_selected_session(self, item):
        index = self.session_list.row(item)
        if 0 <= index < len(self.sessions):
            req, res = self.sessions[index]
            self.request_editor.setPlainText(req)
            self.response_view.setPlainText(res)

    @pyqtSlot()
    def send_request(self):
        current_index = self.session_list.currentRow()
        if current_index < 0:
            return

        raw_request = self.request_editor.toPlainText()
        # TODO: Implement actual HTTP sending logic here.
        dummy_response = "[Response placeholder for now...]"

        # Update session data
        self.sessions[current_index] = (raw_request, dummy_response)
        self.response_view.setPlainText(dummy_response)
