from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
    QTextEdit, QPushButton, QSplitter, QLabel, QTabWidget, QTableWidget,
    QTableWidgetItem, QLineEdit, QCheckBox, QHeaderView
)
from PyQt5.QtCore import Qt

class ProxyPage(QWidget):
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

        # Intercept Button
        self.intercept_button = QPushButton("Intercept: OFF")
        self.intercept_button.setCheckable(True)
        self.intercept_button.clicked.connect(self.toggle_intercept)
        layout.addWidget(self.intercept_button)

        # Request List
        self.request_list = QListWidget()
        self.request_list.itemClicked.connect(self.display_request_details)

        # Dummy Data for Requests
        dummy_requests = [
            ("GET", "/home", "200 OK"),
            ("POST", "/login", "302 Redirect"),
            ("GET", "/api/data", "200 OK"),
            ("PUT", "/api/update", "401 Unauthorized"),
            ("DELETE", "/api/remove", "403 Forbidden"),
            ("GET", "/products", "200 OK"),
            ("POST", "/checkout", "500 Internal Server Error")
        ]
        
        for method, path, status in dummy_requests:
            item = QListWidgetItem(f"{method} {path} - {status}")
            self.request_list.addItem(item)

        # Request and Response Viewer
        request_view = self.create_request_view()
        response_view = self.create_response_view()

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.request_list)
        splitter.addWidget(request_view)
        splitter.addWidget(response_view)

        layout.addWidget(splitter)

        self.setLayout(layout)

    def toggle_intercept(self):
        if self.intercept_button.isChecked():
            self.intercept_button.setText("Intercept: ON")
            self.intercept_button.setStyleSheet("background-color: #E74C3C; color: white;")
        else:
            self.intercept_button.setText("Intercept: OFF")
            self.intercept_button.setStyleSheet("background-color: #3498DB; color: white;")

    def create_request_view(self):
        request_tab = QTabWidget()

        # Headers Tab
        headers_table = QTableWidget(4, 2)
        headers_table.setHorizontalHeaderLabels(["Header", "Value"])
        headers = [
            ("Host", "example.com"),
            ("User-Agent", "SecuLite/1.0"),
            ("Accept", "application/json"),
            ("Connection", "keep-alive")
        ]
        for row, (header, value) in enumerate(headers):
            headers_table.setItem(row, 0, QTableWidgetItem(header))
            headers_table.setItem(row, 1, QTableWidgetItem(value))
        headers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Body Tab
        body_edit = QTextEdit()
        body_edit.setText("{\n    \"username\": \"test_user\",\n    \"password\": \"pass123\"\n}")
        
        # Query Parameters Tab
        query_table = QTableWidget(2, 2)
        query_table.setHorizontalHeaderLabels(["Parameter", "Value"])
        queries = [
            ("search", "example"),
            ("page", "1")
        ]
        for row, (param, value) in enumerate(queries):
            query_table.setItem(row, 0, QTableWidgetItem(param))
            query_table.setItem(row, 1, QTableWidgetItem(value))
        query_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        request_tab.addTab(headers_table, "Headers")
        request_tab.addTab(body_edit, "Body")
        request_tab.addTab(query_table, "Query Params")

        return request_tab

    def create_response_view(self):
        response_tab = QTabWidget()

        # Status Tab
        status_label = QLabel("HTTP/1.1 200 OK")
        status_label.setStyleSheet("font-size: 16px;")
        status_layout = QVBoxLayout()
        status_layout.addWidget(status_label)
        status_widget = QWidget()
        status_widget.setLayout(status_layout)

        # Headers Tab
        headers_table = QTableWidget(3, 2)
        headers_table.setHorizontalHeaderLabels(["Header", "Value"])
        headers = [
            ("Content-Type", "application/json"),
            ("Server", "SecuLite-Server"),
            ("Content-Length", "512")
        ]
        for row, (header, value) in enumerate(headers):
            headers_table.setItem(row, 0, QTableWidgetItem(header))
            headers_table.setItem(row, 1, QTableWidgetItem(value))
        headers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Body Tab
        body_edit = QTextEdit()
        body_edit.setText("{\n    \"status\": \"success\",\n    \"data\": [1, 2, 3, 4, 5]\n}")
        body_edit.setReadOnly(True)

        response_tab.addTab(status_widget, "Status")
        response_tab.addTab(headers_table, "Headers")
        response_tab.addTab(body_edit, "Body")

        return response_tab

    def display_request_details(self, item):
        # Simulate loading the request and response details
        print(f"Selected: {item.text()}")
