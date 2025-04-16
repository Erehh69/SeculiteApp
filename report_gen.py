from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton, QCheckBox, QFileDialog

class ReportGenerationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Report")
        layout = QVBoxLayout()

        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["HTML", "PDF", "JSON"])
        layout.addWidget(QLabel("Report Format:"))
        layout.addWidget(self.report_type_combo)

        self.include_payloads_check = QCheckBox("Include Payload Details")
        layout.addWidget(self.include_payloads_check)

        self.include_vulnerabilities_check = QCheckBox("Include Vulnerabilities")
        layout.addWidget(self.include_vulnerabilities_check)

        self.generate_button = QPushButton("Generate Report")
        self.generate_button.clicked.connect(self.generate_report)
        layout.addWidget(self.generate_button)

        self.setLayout(layout)

    def generate_report(self):
        report_format = self.report_type_combo.currentText()
        include_payloads = self.include_payloads_check.isChecked()
        include_vulnerabilities = self.include_vulnerabilities_check.isChecked()

        # Here we call a method to actually generate the report in the selected format
        report_data = {
            "format": report_format,
            "include_payloads": include_payloads,
            "include_vulnerabilities": include_vulnerabilities
        }
        self.parent().create_report(report_data)
        self.accept()  # Close the dialog after generating the report
