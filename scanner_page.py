import requests
import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QCheckBox
)
from PyQt5.QtCore import Qt

# Set up logging
logging.basicConfig(filename='scanner_log.txt', level=logging.DEBUG, format='%(asctime)s - %(message)s')

class ScannerPage(QWidget):
    def __init__(self):
        super().__init__()

        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        
        layout = QVBoxLayout()

        # URL input section
        layout.addWidget(QLabel("Target URL:"))
        self.url_input = QLineEdit()
        self.url_input.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(self.url_input)

        # Vulnerability selection
        self.sql_injection_checkbox = QCheckBox("SQL Injection")
        self.xss_checkbox = QCheckBox("XSS")
        self.command_injection_checkbox = QCheckBox("Command Injection")
        layout.addWidget(self.sql_injection_checkbox)
        layout.addWidget(self.xss_checkbox)
        layout.addWidget(self.command_injection_checkbox)

        # Scan button
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.clicked.connect(self.start_scan)
        self.scan_button.setStyleSheet("background-color: #444; color: white;")
        layout.addWidget(self.scan_button)

        # Results output
        self.results_output = QTextEdit()
        self.results_output.setReadOnly(True)
        self.results_output.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(QLabel("Scan Results:"))
        layout.addWidget(self.results_output)

        self.setLayout(layout)

    def start_scan(self):
        url = self.url_input.text()
        self.results_output.clear()

        if not url:
            self.results_output.append("[!] Please provide a URL.")
            logging.error("No URL provided.")
            return

        results = []
        
        # Fetch the initial page to retrieve cookies
        try:
            response = requests.get(url, timeout=5)
            cookies = response.cookies  # Store the cookies for future requests
            headers = {
                'User-Agent': 'SecuLiteScanner/1.0',
                'Cookie': self.format_cookies(cookies)
            }
            logging.info(f"Initial request to {url} successful. Cookies retrieved.")
        except requests.RequestException as e:
            self.results_output.append(f"[!] Failed to connect: {e}")
            logging.error(f"Failed to connect to {url}: {e}")
            return

        # Check for SQL Injection
        if self.sql_injection_checkbox.isChecked():
            sql_injection_result = self.check_sql_injection(url, headers)
            if sql_injection_result:
                results.append("[+] Potential SQL Injection vulnerability detected!")
                self.results_output.append(f"SQL Injection Test: {sql_injection_result['payload']}")
                self.results_output.append(f"Response Code: {sql_injection_result['status_code']}")
                self.results_output.append(f"Response Body: {sql_injection_result['body']}")
                logging.info(f"SQL Injection vulnerability detected at {url}.")
            else:
                logging.info(f"SQL Injection check for {url} did not find any vulnerability.")

        # Check for XSS
        if self.xss_checkbox.isChecked():
            xss_result = self.check_xss(url, headers)
            if xss_result:
                results.append("[+] Potential XSS vulnerability detected!")
                self.results_output.append(f"XSS Test: {xss_result['payload']}")
                self.results_output.append(f"Response Code: {xss_result['status_code']}")
                self.results_output.append(f"Response Body: {xss_result['body']}")
                logging.info(f"XSS vulnerability detected at {url}.")
            else:
                logging.info(f"XSS check for {url} did not find any vulnerability.")

        # Check for Command Injection
        if self.command_injection_checkbox.isChecked():
            command_injection_result = self.check_command_injection(url, headers)
            if command_injection_result:
                results.append("[+] Potential Command Injection vulnerability detected!")
                self.results_output.append(f"Command Injection Test: {command_injection_result['payload']}")
                self.results_output.append(f"Response Code: {command_injection_result['status_code']}")
                self.results_output.append(f"Response Body: {command_injection_result['body']}")
                logging.info(f"Command Injection vulnerability detected at {url}.")
            else:
                logging.info(f"Command Injection check for {url} did not find any vulnerability.")

        if not results:
            self.results_output.append("[+] No vulnerabilities found.")
            logging.info(f"No vulnerabilities detected at {url}.")
        else:
            for result in results:
                self.results_output.append(result)
        
        # Also log results to the file
        logging.info("Scan finished.\n")

    def format_cookies(self, cookies):
        """
        Format the cookies into a string suitable for the Cookie header.
        """
        cookie_str = ""
        for cookie in cookies:
            cookie_str += f"{cookie.name}={cookie.value}; "
        return cookie_str.strip()

    def check_sql_injection(self, url, headers):
        # Simple SQL Injection test (check for ' OR 1=1 --' payload)
        test_url = f"{url}?id=1' OR 1=1 --"
        try:
            response = requests.get(test_url, headers=headers, timeout=5)
            logging.info(f"Testing SQL Injection with payload: {test_url}")
            if "error" in response.text.lower():  # Basic check for SQL errors in response
                return {
                    "payload": test_url,
                    "status_code": response.status_code,
                    "body": response.text
                }
        except requests.RequestException as e:
            logging.error(f"Error testing SQL Injection: {e}")
        return None

    def check_xss(self, url, headers):
        # Simple XSS test (check for <script>alert(1)</script>)
        test_url = f"{url}?name=<script>alert(1)</script>"
        try:
            response = requests.get(test_url, headers=headers, timeout=5)
            logging.info(f"Testing XSS with payload: {test_url}")
            if "<script>alert(1)</script>" in response.text:  # Check if script is reflected in response
                return {
                    "payload": test_url,
                    "status_code": response.status_code,
                    "body": response.text
                }
        except requests.RequestException as e:
            logging.error(f"Error testing XSS: {e}")
        return None

    def check_command_injection(self, url, headers):
        # Simple Command Injection test (check for ;ls or similar)
        test_url = f"{url}?cmd=;ls"
        try:
            response = requests.get(test_url, headers=headers, timeout=5)
            logging.info(f"Testing Command Injection with payload: {test_url}")
            if "bin" in response.text:  # Checking for output that might indicate command execution
                return {
                    "payload": test_url,
                    "status_code": response.status_code,
                    "body": response.text
                }
        except requests.RequestException as e:
            logging.error(f"Error testing Command Injection: {e}")
        return None
