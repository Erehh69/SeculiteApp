from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QListWidget, QSplitter
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import requests
import json

class RepeaterPage(QWidget):
    def __init__(self):
        super().__init__()

        # Main Layout
        layout = QVBoxLayout()

        # Request Section
        request_label = QLabel("Request:")
        request_label.setStyleSheet("color: #1ABC9C; font-weight: bold;")
        request_label.setFont(QFont("Arial", 14))
        
        self.request_input = QTextEdit()
        self.request_input.setStyleSheet("background-color: #34495E; color: #ECF0F1;")
        self.request_input.setFont(QFont("Courier New", 12))
        self.request_input.setPlaceholderText("Enter your HTTP request here...")

        send_button = QPushButton("Send")
        send_button.setStyleSheet("""
            background-color: #1ABC9C;
            color: #2C3E50;
            font-weight: bold;
            padding: 10px;
            border-radius: 4px;
        """)
        send_button.clicked.connect(self.send_request)

        clear_button = QPushButton("Clear")
        clear_button.setStyleSheet("""
            background-color: #E74C3C;
            color: #ECF0F1;
            padding: 10px;
            border-radius: 4px;
        """)
        clear_button.clicked.connect(self.clear_request)

        button_layout = QHBoxLayout()
        button_layout.addWidget(send_button)
        button_layout.addWidget(clear_button)

        # Response Section
        response_label = QLabel("Response:")
        response_label.setStyleSheet("color: #1ABC9C; font-weight: bold;")
        response_label.setFont(QFont("Arial", 14))

        self.response_output = QTextEdit()
        self.response_output.setStyleSheet("background-color: #34495E; color: #ECF0F1;")
        self.response_output.setFont(QFont("Courier New", 12))
        self.response_output.setReadOnly(True)

        # Request History Section
        history_label = QLabel("History:")
        history_label.setStyleSheet("color: #1ABC9C; font-weight: bold;")
        history_label.setFont(QFont("Arial", 14))

        self.history_list = QListWidget()
        self.history_list.setStyleSheet("background-color: #2C3E50; color: #ECF0F1;")
        self.history_list.itemClicked.connect(self.load_history)

        # Splitter to Resize Request/Response
        splitter = QSplitter(Qt.Vertical)
        request_section = QWidget()
        request_layout = QVBoxLayout()
        request_layout.addWidget(request_label)
        request_layout.addWidget(self.request_input)
        request_layout.addLayout(button_layout)
        request_section.setLayout(request_layout)

        response_section = QWidget()
        response_layout = QVBoxLayout()
        response_layout.addWidget(response_label)
        response_layout.addWidget(self.response_output)
        response_section.setLayout(response_layout)

        splitter.addWidget(request_section)
        splitter.addWidget(response_section)
        splitter.setSizes([300, 400])

        # Layout Management
        layout.addWidget(history_label)
        layout.addWidget(self.history_list)
        layout.addWidget(splitter)
        self.setLayout(layout)

    def send_request(self):
        # Get request from input
        raw_request = self.request_input.toPlainText()
        
        # Basic Request Parser
        lines = raw_request.splitlines()
        if len(lines) < 1:
            self.response_output.setText("Invalid Request Format.")
            return
        
        first_line = lines[0].split()
        if len(first_line) < 2:
            self.response_output.setText("Invalid Request Line.")
            return

        method = first_line[0]
        url = first_line[1]
        
        headers = {}
        body = None
        is_body = False
        
        for line in lines[1:]:
            if line == "":
                is_body = True
                continue
            if is_body:
                body = line
            else:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()
        
        try:
            # Send Request
            if method.upper() == "GET":
                response = requests.get(url, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, headers=headers, data=body)
            elif method.upper() == "PUT":
                response = requests.put(url, headers=headers, data=body)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                self.response_output.setText("HTTP Method Not Supported.")
                return

            # Display Response
            response_text = f"Status Code: {response.status_code}\n"
            response_text += "Headers:\n"
            for k, v in response.headers.items():
                response_text += f"{k}: {v}\n"
            response_text += "\nBody:\n"
            try:
                response_text += json.dumps(response.json(), indent=4)
            except ValueError:
                response_text += response.text

            self.response_output.setText(response_text)

            # Add to History
            self.history_list.addItem(f"{method} {url}")
        
        except Exception as e:
            self.response_output.setText(str(e))

    def clear_request(self):
        self.request_input.clear()
        self.response_output.clear()

    def load_history(self, item):
        self.request_input.setText(item.text())
