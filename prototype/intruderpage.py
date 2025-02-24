from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox, QPushButton, QListWidget, 
    QTabWidget, QTableWidget, QTableWidgetItem, QHBoxLayout, QSplitter, QHeaderView
)
from PyQt5.QtCore import Qt

class IntruderPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("""
            QWidget {
                background-color: #3B4F64;
                color: #ECF0F1;
            }
            QListWidget {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #1ABC9C;
            }
            QTextEdit {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
                font-family: Consolas;
                padding: 4px;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:checked {
                background-color: #E74C3C;
            }
            QLabel {
                color: #ECF0F1;
                font-weight: bold;
            }
            QTabWidget::pane {
                border-top: 2px solid #1ABC9C;
            }
            QTabBar::tab {
                background: #34495E;
                color: #ECF0F1;
                padding: 8px;
            }
            QTabBar::tab:selected {
                background: #1ABC9C;
                color: #2C3E50;
            }
            QTableWidget {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
            }
            QHeaderView::section {
                background-color: #34495E;
                color: #ECF0F1;
                padding: 4px;
            }
        """)

        layout = QVBoxLayout()

        # Title
        title = QLabel("Intruder - Attack Module")
        title.setStyleSheet("color: #1ABC9C; font-weight: bold; font-size: 18px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Payload Input
        payload_label = QLabel("Payloads:")
        payload_label.setStyleSheet("color: #ECF0F1;")
        layout.addWidget(payload_label)

        self.payload_input = QTextEdit()
        self.payload_input.setStyleSheet("background-color: #34495E; color: #ECF0F1;")
        self.payload_input.setPlaceholderText("Enter payloads, one per line...")
        layout.addWidget(self.payload_input)

        # Attack Type
        attack_label = QLabel("Attack Type:")
        attack_label.setStyleSheet("color: #ECF0F1;")
        layout.addWidget(attack_label)

        self.attack_type = QComboBox()
        self.attack_type.addItems(["Sniper", "Battering Ram", "Pitchfork", "Cluster Bomb"])
        self.attack_type.setStyleSheet("background-color: #34495E; color: #ECF0F1;")
        layout.addWidget(self.attack_type)

        # Start Attack Button
        start_button = QPushButton("Start Attack")
        start_button.setStyleSheet("background-color: #1ABC9C; color: #2C3E50; padding: 10px; border-radius: 4px;")
        layout.addWidget(start_button)

        # Results Display
        self.results_list = QListWidget()
        self.results_list.setStyleSheet("background-color: #2C3E50; color: #ECF0F1;")
        layout.addWidget(self.results_list)

        # Example Result (Updated with More Payload Examples)
        self.show_example_results()

        # Raw / Body Toggle
        self.raw_button = QPushButton("Raw")
        self.body_button = QPushButton("Body")
        self.raw_button.setStyleSheet("background-color: #1ABC9C; color: white;")
        self.body_button.setStyleSheet("background-color: #1ABC9C; color: white;")
        self.raw_button.setCheckable(True)
        self.body_button.setCheckable(True)
        self.raw_button.clicked.connect(self.toggle_raw)
        self.body_button.clicked.connect(self.toggle_body)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.raw_button)
        buttons_layout.addWidget(self.body_button)
        layout.addLayout(buttons_layout)

        # Result Tabs (Raw or Body)
        self.response_tab = self.create_response_view()
        layout.addWidget(self.response_tab)

        self.setLayout(layout)

    def show_example_results(self):
        # More realistic example results (with multiple payloads)
        results = [
            {"status": "200 OK", "payload": "' OR 1=1 --", "time": "0.03s", "url": "/login"},
            {"status": "200 OK", "payload": "'; DROP TABLE users; --", "time": "0.07s", "url": "/admin"},
            {"status": "404 Not Found", "payload": "<script>alert('XSS')</script>", "time": "0.10s", "url": "/home"},
            {"status": "200 OK", "payload": "' AND email IS NULL --", "time": "0.02s", "url": "/profile"},
            {"status": "200 OK", "payload": "<img src='x' onerror='alert(1)'>", "time": "0.15s", "url": "/settings"},
            {"status": "403 Forbidden", "payload": "admin' --", "time": "0.12s", "url": "/admin-dashboard"},
            {"status": "500 Internal Server Error", "payload": "'; SELECT * FROM users --", "time": "0.05s", "url": "/user-list"},
            {"status": "302 Found", "payload": "'; EXEC xp_cmdshell('net user hacker /add') --", "time": "0.20s", "url": "/command"}
        ]
        for result in results:
            self.results_list.addItem(f"Status: {result['status']} | Payload: {result['payload']} | Time: {result['time']} | URL: {result['url']}")

    def toggle_raw(self):
        if self.raw_button.isChecked():
            self.raw_button.setStyleSheet("background-color: #E74C3C; color: white;")
            self.body_button.setChecked(False)
            self.body_button.setStyleSheet("background-color: #1ABC9C; color: white;")
            self.response_tab.setCurrentIndex(0)  # Show Raw Tab
        else:
            self.raw_button.setStyleSheet("background-color: #1ABC9C; color: white;")
            self.response_tab.setCurrentIndex(2)  # Show Body Tab

    def toggle_body(self):
        if self.body_button.isChecked():
            self.body_button.setStyleSheet("background-color: #E74C3C; color: white;")
            self.raw_button.setChecked(False)
            self.raw_button.setStyleSheet("background-color: #1ABC9C; color: white;")
            self.response_tab.setCurrentIndex(1)  # Show Body Tab
        else:
            self.body_button.setStyleSheet("background-color: #1ABC9C; color: white;")
            self.response_tab.setCurrentIndex(0)  # Show Raw Tab

    def create_response_view(self):
        response_tab = QTabWidget()

        # Raw Tab (Simulated Raw Data)
        raw_edit = QTextEdit()
        raw_edit.setText("HTTP/1.1 200 OK\nContent-Type: application/json\n\n{\"status\":\"success\"}")
        raw_edit.setReadOnly(True)
        raw_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
                font-family: Consolas;
                padding: 4px;
            }
        """)
        response_tab.addTab(raw_edit, "Raw")

        # Body Tab (Simulated Body Data)
        body_edit = QTextEdit()
        body_edit.setText("{\n    \"status\": \"success\",\n    \"data\": [1, 2, 3, 4, 5]\n}")
        body_edit.setReadOnly(True)
        body_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2C3E50;
                color: #ECF0F1;
                border: 1px solid #1ABC9C;
                font-family: Consolas;
                padding: 4px;
            }
        """)
        response_tab.addTab(body_edit, "Body")

        return response_tab
