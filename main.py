import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QListWidget, QStackedWidget, QWidget
from proxy_page import ProxyPage
from scanner_page import ScannerPage
from settings_page import SettingsPage

# Set environment variables for scaling
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
os.environ['QT_SCREEN_SCALE_FACTORS'] = '1.0'
os.environ['QT_SCALE_FACTOR'] = '1.0'

class SecuLiteApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SecuLite - Advanced Security Tool")
        self.setGeometry(100, 100, 1200, 800)

        # Sidebar
        self.sidebar = QListWidget()
        self.sidebar.addItem("Proxy")
        self.sidebar.addItem("Scanner")
        self.sidebar.addItem("Settings")
        self.sidebar.currentRowChanged.connect(self.display_page)

        # Pages
        self.pages = QStackedWidget()
        self.proxy_page = ProxyPage()
        self.pages.addWidget(self.proxy_page)
        self.pages.addWidget(ScannerPage())
        self.pages.addWidget(SettingsPage())

        # Layout
        layout = QHBoxLayout()
        layout.addWidget(self.sidebar, 1)
        layout.addWidget(self.pages, 4)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def display_page(self, index):
        self.pages.setCurrentIndex(index)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SecuLiteApp()
    window.show()
    sys.exit(app.exec_())
