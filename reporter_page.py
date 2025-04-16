from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QComboBox, QLineEdit, QListWidget, QListWidgetItem
)
from PyQt5.QtCore import Qt, QDateTime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

import os

class ReporterPage(QWidget):
    def __init__(self, scanner_reference=None):
        super().__init__()
        self.findings = []
        self.scanner_reference = scanner_reference  # reference to ScannerPage if needed

        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        layout = QVBoxLayout()

        # Header
        layout.addWidget(QLabel("📄 Vulnerability Report"))

        # Vulnerability List
        self.vuln_list = QListWidget()
        self.vuln_list.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(QLabel("Findings:"))
        layout.addWidget(self.vuln_list)

        # Manual Entry
        self.manual_entry_input = QLineEdit()
        self.manual_entry_input.setPlaceholderText("Enter manual finding...")
        self.manual_entry_input.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(self.manual_entry_input)

        self.severity_dropdown = QComboBox()
        self.severity_dropdown.addItems(["Low", "Medium", "High"])
        self.severity_dropdown.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(self.severity_dropdown)

        self.add_finding_btn = QPushButton("➕ Add Finding")
        self.add_finding_btn.setStyleSheet("background-color: #444; color: white;")
        self.add_finding_btn.clicked.connect(self.log_finding)
        layout.addWidget(self.add_finding_btn)

        # Notes section
        self.notes_input = QTextEdit()
        self.notes_input.setPlaceholderText("Write analysis notes here...")
        self.notes_input.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(QLabel("Analyst Notes:"))
        layout.addWidget(self.notes_input)

        # Export PDF button
        self.export_pdf_btn = QPushButton("📤 Export to PDF")
        self.export_pdf_btn.setStyleSheet("background-color: #555; color: white;")
        self.export_pdf_btn.clicked.connect(self.export_to_pdf)
        layout.addWidget(self.export_pdf_btn)

        self.setLayout(layout)

    def log_finding(self, finding):
        # Add the finding to the QListWidget
        text = f"[{finding['status']}] {finding['vulnerability']} - {finding['url']}"
        item = QListWidgetItem(text)
        item.setData(Qt.UserRole, finding['status'])  # Store status in user data if needed for further use
        self.vuln_list.addItem(item)


    def export_to_pdf(self):
        # Create the REPORT directory if it doesn't exist
        report_dir = os.path.join(os.getcwd(), "REPORT")
        if not os.path.exists(report_dir):
            os.makedirs(report_dir)

        # Generate a unique filename
        filename = f"SecuLite_Report_{QDateTime.currentDateTime().toString('yyyyMMdd_hhmmss')}.pdf"
        path = os.path.join(report_dir, filename)

        # Set up PDF canvas
        c = canvas.Canvas(path, pagesize=A4)
        width, height = A4
        y = height - 40

        c.setFont("Helvetica-Bold", 16)
        c.drawString(40, y, "SecuLite Vulnerability Report")
        y -= 40

        c.setFont("Helvetica", 10)
        c.drawString(40, y, f"Date: {QDateTime.currentDateTime().toString()}")
        y -= 30

        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Findings:")
        y -= 20

        c.setFont("Helvetica", 10)
        for index in range(self.vuln_list.count()):
            item_text = self.vuln_list.item(index).text()
            if y < 100:
                c.showPage()
                y = height - 40
            c.drawString(60, y, f"- {item_text}")
            y -= 20

        y -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Analyst Notes:")
        y -= 20

        c.setFont("Helvetica", 10)
        notes_lines = self.notes_input.toPlainText().split("\n")
        for line in notes_lines:
            if y < 100:
                c.showPage()
                y = height - 40
            c.drawString(60, y, line)
            y -= 15

        c.save()
        print(f"[+] Report exported to {path}")

