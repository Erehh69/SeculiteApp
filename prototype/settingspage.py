from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTabWidget, QScrollArea, 
    QFormLayout, QLineEdit, QCheckBox, QComboBox
)

class SettingsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        title = QLabel("Settings")
        title.setStyleSheet("font-size: 24px; color: #1ABC9C;")
        layout.addWidget(title)

        tabs = QTabWidget()
        
        # General Settings
        general_tab = QWidget()
        general_layout = QFormLayout()
        general_layout.addRow("Theme:", QComboBox())
        general_layout.addRow("Language:", QComboBox())
        general_tab.setLayout(general_layout)
        tabs.addTab(general_tab, "General")

        # Network Settings
        network_tab = QWidget()
        network_layout = QFormLayout()
        network_layout.addRow("Proxy Host:", QLineEdit())
        network_layout.addRow("Proxy Port:", QLineEdit())
        network_layout.addRow("Use SSL Proxy:", QCheckBox())
        network_tab.setLayout(network_layout)
        tabs.addTab(network_tab, "Network")

        # Certificate Management
        cert_tab = QWidget()
        cert_layout = QVBoxLayout()
        cert_layout.addWidget(QLabel("Installed Certificates:"))
        cert_tab.setLayout(cert_layout)
        tabs.addTab(cert_tab, "Certificates")

        layout.addWidget(tabs)
        self.setLayout(layout)
