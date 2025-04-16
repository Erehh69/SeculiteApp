#development

#'''
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QListWidget, QStackedWidget, QWidget
from proxy_page import ProxyPage
from scanner_page import ScannerPage
from settings_page import SettingsPage
from repeater_page import RepeaterPage

class SecuLiteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecuLite - Advanced Security Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItem("Proxy Server")
        self.sidebar.addItem("Scanner")
        self.sidebar.addItem("Settings")
        self.sidebar.addItem("Repeater")
        self.sidebar.currentRowChanged.connect(self.display_page)

        # Pages
        self.pages = QStackedWidget()
        self.proxy_server_page = ProxyPage(parent=self)
        self.repeater_page = RepeaterPage()
        self.scanner_page = ScannerPage()
        self.settings_page = SettingsPage()

        self.pages.addWidget(self.proxy_server_page)
        self.pages.addWidget(self.scanner_page)
        self.pages.addWidget(self.settings_page)
        self.pages.addWidget(self.repeater_page)

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.sidebar, 1)
        layout.addWidget(self.pages, 4)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def log_message(self, message):
        # Log the message (could be passed to a log area or console)
        print("[Main Log]:", message)

    def display_page(self, index):
        self.pages.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SecuLiteApp()
    window.show()
    sys.exit(app.exec_())





#'''

#prototype
'''
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
    QPushButton, QStackedWidget, QLabel, QFrame
)
from PyQt5.QtCore import Qt
from prototype.proxypage import ProxyPage
from prototype.repeaterpage import RepeaterPage
from prototype.intruderpage import IntruderPage
from prototype.scannerpage import ScannerPage
from prototype.reporterpage import ReporterPage
from prototype.settingspage import SettingsPage

class SecuLite(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("SecuLite - Modern Web Security Suite")
        self.setGeometry(100, 100, 1200, 800)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #2C3E50;
            }
            QPushButton {
                background-color: #34495E;
                color: #ECF0F1;
                border: none;
                padding: 10px;
                text-align: left;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1ABC9C;
                color: #2C3E50;
            }
            QPushButton:checked {
                background-color: #1ABC9C;
                color: #2C3E50;
                font-weight: bold;
            }
            QLabel {
                color: #ECF0F1;
                font-size: 18px;
                font-weight: bold;
                padding: 5px;
            }
            QFrame {
                background-color: #000000;
            }
        """)

        # Main Layout
        main_layout = QHBoxLayout()

        # Sidebar Menu
        sidebar = QVBoxLayout()
        
        # Logo and Title (Reduced Size)
        logo = QLabel("SecuLite")
        logo.setStyleSheet("font-size: 28px; font-weight: bold; color: #1ABC9C;")
        logo.setAlignment(Qt.AlignCenter)
        sidebar.addWidget(logo)
        
        title = QLabel("Web Security Suite")
        title.setStyleSheet("font-size: 14px; color: #ECF0F1;")
        title.setAlignment(Qt.AlignCenter)
        sidebar.addWidget(title)

        # Add Divider Line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        sidebar.addWidget(line)

        # Navigation Buttons
        self.proxy_button = QPushButton("Proxy")
        self.proxy_button.setCheckable(True)
        self.proxy_button.setChecked(True)
        self.proxy_button.clicked.connect(lambda: self.display_page(0))
        sidebar.addWidget(self.proxy_button)

        self.repeater_button = QPushButton("Repeater")
        self.repeater_button.setCheckable(True)
        self.repeater_button.clicked.connect(lambda: self.display_page(1))
        sidebar.addWidget(self.repeater_button)

        self.intruder_button = QPushButton("Intruder")
        self.intruder_button.setCheckable(True)
        self.intruder_button.clicked.connect(lambda: self.display_page(2))
        sidebar.addWidget(self.intruder_button)

        self.scanner_button = QPushButton("Scanner")
        self.scanner_button.setCheckable(True)
        self.scanner_button.clicked.connect(lambda: self.display_page(3))
        sidebar.addWidget(self.scanner_button)

        self.reporter_button = QPushButton("Reporter")
        self.reporter_button.setCheckable(True)
        self.reporter_button.clicked.connect(lambda: self.display_page(4))
        sidebar.addWidget(self.reporter_button)

        # Add Settings Button
        self.settings_button = QPushButton("Settings")
        self.settings_button.setCheckable(True)
        self.settings_button.clicked.connect(lambda: self.display_page(5))
        sidebar.addWidget(self.settings_button)

        # Add Divider Line between Buttons and Content
        line_between = QFrame()
        line_between.setFrameShape(QFrame.VLine)
        line_between.setFrameShadow(QFrame.Sunken)
        line_between.setStyleSheet("background-color: #000000;")
        main_layout.addLayout(sidebar)
        main_layout.addWidget(line_between)

        # Content Area with Stacked Pages
        self.pages = QStackedWidget()
        self.pages.addWidget(ProxyPage())
        self.pages.addWidget(RepeaterPage())
        self.pages.addWidget(IntruderPage())
        self.pages.addWidget(ScannerPage())
        self.pages.addWidget(ReporterPage())
        self.pages.addWidget(SettingsPage())  # Settings Page Added

        main_layout.addWidget(self.pages)

        # Central Widget
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def display_page(self, index):
        self.pages.setCurrentIndex(index)
        self.proxy_button.setChecked(index == 0)
        self.repeater_button.setChecked(index == 1)
        self.intruder_button.setChecked(index == 2)
        self.scanner_button.setChecked(index == 3)
        self.reporter_button.setChecked(index == 4)
        self.settings_button.setChecked(index == 5)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = SecuLite()
    window.show()
    sys.exit(app.exec_())




'''