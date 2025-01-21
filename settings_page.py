from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Proxy Settings"))

        layout.addWidget(QLabel("Proxy Host:"))
        self.proxy_host = QLineEdit("127.0.0.1")
        layout.addWidget(self.proxy_host)

        layout.addWidget(QLabel("Proxy Port:"))
        self.proxy_port = QLineEdit("8080")
        layout.addWidget(self.proxy_port)

        self.save_button = QPushButton("Save Settings")
        self.save_button.clicked.connect(self.save_settings)
        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def save_settings(self):
        host = self.proxy_host.text()
        port = self.proxy_port.text()
        print(f"Settings saved: Host - {host}, Port - {port}")
