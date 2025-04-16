from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QTextEdit, QHBoxLayout, QPushButton, QComboBox, QFileDialog
)
from PyQt5.QtCore import Qt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import socket
import threading
from progress_window import ProgressWindow
from report_gen import ReportGenerationDialog  # Ensure you import the ProgressWindow

class IntruderPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.sessions = []
        self.payloads = []

        layout = QVBoxLayout()

        self.session_list = QListWidget()
        self.session_list.setStyleSheet("background-color: #2d2d2d; color: white;")
        self.session_list.itemClicked.connect(self.show_session)
        layout.addWidget(QLabel("Intruder Sessions:"))
        layout.addWidget(self.session_list)

        self.request_editor = QTextEdit()
        self.request_editor.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(QLabel("Intruder Request Editor:"))
        layout.addWidget(self.request_editor)

        # Payload section
        payload_layout = QHBoxLayout()

        self.insert_symbol_btn = QPushButton("Insert §")
        self.insert_symbol_btn.clicked.connect(self.insert_symbol)
        payload_layout.addWidget(self.insert_symbol_btn)

        self.payload_type_combo = QComboBox()
        self.payload_type_combo.addItems(["Simple List"])
        payload_layout.addWidget(QLabel("Payload Type:"))
        payload_layout.addWidget(self.payload_type_combo)

        self.load_payloads_btn = QPushButton("Load Payloads")
        self.load_payloads_btn.clicked.connect(self.load_payloads)
        payload_layout.addWidget(self.load_payloads_btn)

        layout.addLayout(payload_layout)

        # Run + Output
        self.run_button = QPushButton("Run Intruder Attack")
        self.run_button.setStyleSheet("background-color: #444; color: white;")
        self.run_button.clicked.connect(self.run_attack)
        layout.addWidget(self.run_button)

        self.response_output = QTextEdit()
        self.response_output.setReadOnly(True)
        self.response_output.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(QLabel("Intruder Responses:"))
        layout.addWidget(self.response_output)

        self.setLayout(layout)

    def insert_symbol(self):
        cursor = self.request_editor.textCursor()
        cursor.insertText("§")

    def load_payloads(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Load Payloads", "", "Text Files (*.txt)")
        if filename:
            try:
                with open(filename, 'r') as f:
                    self.payloads = [line.strip() for line in f.readlines() if line.strip()]
                self.response_output.append(f"[+] Loaded {len(self.payloads)} payloads.")
            except Exception as e:
                self.response_output.append(f"[!] Failed to load payloads: {e}")

    def add_intruder_session(self, title, request_data):
        session_item = QListWidgetItem(title)
        session_item.setData(Qt.UserRole, request_data)
        self.session_list.addItem(session_item)
        self.sessions.append(request_data)
        print(f"[+] New Intruder session added: {title}")

    def show_session(self, item):
        request_data = item.data(Qt.UserRole)
        self.request_editor.setPlainText(request_data)

    def run_attack(self):
        template = self.request_editor.toPlainText()

        if "§" not in template:
            self.response_output.append("[!] No § symbol found in request.")
            return

        if not self.payloads:
            self.response_output.append("[!] No payloads loaded.")
            return

        # Create a new progress window and start the attack in the background
        self.progress_window = ProgressWindow(self)  # Pass 'self' as the parent QWidget
        self.progress_window.show()  # Show the progress window

        # Start the attack in a separate thread
        threading.Thread(target=self.run_attack_in_background, args=(template,), daemon=True).start()

    def run_attack_in_background(self, template):
        """
        Run the attack in a separate thread.
        """
        for payload in self.payloads:
            # Modify the template with the current payload
            request_data = template.replace("§", payload)

            # Extract host and port from the request template
            try:
                host, port = self.extract_host_port(request_data)
            except Exception as e:
                self.response_output.append(f"[!] Error extracting host/port: {e}")
                continue

            # Send the request and get the response
            response = self.send_request(host, port, request_data)

            # Capture the response length and provide feedback
            response_length = len(response)
            self.progress_window.add_response(payload, response, response_length)  # Show in ProgressWindow

            self.response_output.append(f"Payload: {payload}, Response Length: {response_length}")

            # Detect vulnerabilities based on response (basic example)
            vulnerabilities = []
            if "SQL syntax" in response:
                vulnerabilities.append("Possible SQL Injection vulnerability detected.")

            self.progress_window.add_response(payload, response, response_length)
            self.response_output.append(f"Payload: {payload}, Response Length: {response_length}")

            # Add detected vulnerabilities to report
            if vulnerabilities:
                self.response_output.append(f"[!] Vulnerabilities: {', '.join(vulnerabilities)}")

    def extract_host_port(self, request_data):
        lines = request_data.splitlines()
        for line in lines:
            if line.lower().startswith("host:"):
                host_part = line.split(":", 1)[1].strip()
                if ":" in host_part:
                    host, port = host_part.split(":", 1)
                    return host.strip(), int(port.strip())
                return host_part.strip(), 80
        raise Exception("Missing or malformed Host header.")

    def send_request(self, host, port, request_data):
        if not request_data.endswith("\r\n\r\n"):
            request_data += "\r\n\r\n"

        with socket.create_connection((host, port), timeout=5) as sock:
            sock.sendall(request_data.encode('utf-8', errors='ignore'))
            response = b""
            sock.settimeout(2)
            try:
                while True:
                    chunk = sock.recv(4096)
                    if not chunk:
                        break
                    response += chunk
            except socket.timeout:
                pass
        return response.decode('utf-8', errors='replace')


    #report
    def open_report_dialog(self):
        dialog = ReportGenerationDialog(self)
        dialog.exec_()

    def create_report(self, report_data):
        """
        Based on the report_data dictionary, generate the selected report format.
        """
        report_format = report_data["format"]
        include_payloads = report_data["include_payloads"]
        include_vulnerabilities = report_data["include_vulnerabilities"]

        # Choose report generation method based on the selected format
        if report_format == "HTML":
            self.generate_html_report(include_payloads, include_vulnerabilities)
        elif report_format == "PDF":
            self.generate_pdf_report(include_payloads, include_vulnerabilities)
        elif report_format == "JSON":
            self.generate_json_report(include_payloads, include_vulnerabilities)

    def generate_html_report(self, include_payloads, include_vulnerabilities):
        """
        Generate an HTML report with the attack details.
        """
        # Construct HTML structure (headers, tables, etc.)
        report_html = "<html><head><title>SecuLite Report</title></head><body>"
        report_html += "<h1>SecuLite Intruder Attack Report</h1>"
        
        # Include the relevant data
        if include_payloads:
            report_html += "<h2>Payload Details</h2><ul>"
            for payload in self.payloads:
                report_html += f"<li>{payload}</li>"
            report_html += "</ul>"

        if include_vulnerabilities:
            report_html += "<h2>Vulnerabilities Detected</h2><ul>"
            # Add vulnerability data here (you might need to gather this during attack)
            report_html += "<li>SQL Injection Detected in POST /login</li>"
            report_html += "</ul>"

        report_html += "</body></html>"

        # Save report as HTML file
        filename, _ = QFileDialog.getSaveFileName(self, "Save Report", "", "HTML Files (*.html)")
        if filename:
            with open(filename, "w") as f:
                f.write(report_html)

    def generate_pdf_report(self, include_payloads, include_vulnerabilities):
        """
        Generate a PDF report (you can use libraries like ReportLab).
        """
        filename, _ = QFileDialog.getSaveFileName(self, "Save PDF Report", "", "PDF Files (*.pdf)")
        if filename:
            c = canvas.Canvas(filename, pagesize=letter)
            c.drawString(100, 750, "SecuLite Intruder Attack Report")

            # Add payload details and vulnerabilities if needed
            y_position = 730
            if include_payloads:
                c.drawString(100, y_position, "Payloads Tested:")
                y_position -= 20
                for payload in self.payloads:
                    c.drawString(100, y_position, payload)
                    y_position -= 20

            if include_vulnerabilities:
                c.drawString(100, y_position, "Vulnerabilities Detected:")
                y_position -= 20
                c.drawString(100, y_position, "SQL Injection Detected in POST /login")

            c.save()

    def generate_json_report(self, include_payloads, include_vulnerabilities):
        """
        Generate a JSON report.
        """
        import json

        report_data = {
            "format": "JSON",
            "payloads": self.payloads if include_payloads else [],
            "vulnerabilities": ["SQL Injection Detected in POST /login"] if include_vulnerabilities else []
        }

        filename, _ = QFileDialog.getSaveFileName(self, "Save JSON Report", "", "JSON Files (*.json)")
        if filename:
            with open(filename, "w") as f:
                json.dump(report_data, f, indent=4)