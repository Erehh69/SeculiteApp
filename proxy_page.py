from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLabel
import logging
from proxy_handler import ProxyHandler
from http.server import HTTPServer
import ssl

class ProxyPage(QWidget):
    intercepted_request_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        control_layout = QHBoxLayout()

        # Status Label
        self.status_label = QLabel("Proxy Status: Stopped")
        control_layout.addWidget(self.status_label)

        # Intercept Button
        self.intercept_button = QPushButton("Intercept Off")
        self.intercept_button.setStyleSheet("background-color: red; color: white;")
        self.intercept_button.clicked.connect(self.toggle_intercept)
        control_layout.addWidget(self.intercept_button)

        # Start Proxy Button
        self.start_proxy_button = QPushButton("Start Proxy")
        self.start_proxy_button.clicked.connect(self.start_proxy)
        control_layout.addWidget(self.start_proxy_button)
        layout.addLayout(control_layout)

        # Log Output (Text Area)
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

    def toggle_intercept(self):
        if self.intercept_button.text() == "Intercept Off":
            self.intercept_button.setText("Intercept On")
            self.intercept_button.setStyleSheet("background-color: green; color: white;")
            self.status_label.setText("Intercepting Requests...")
        else:
            self.intercept_button.setText("Intercept Off")
            self.intercept_button.setStyleSheet("background-color: red; color: white;")
            self.status_label.setText("Proxy Status: Stopped")

    def start_proxy(self):
        """ Start Proxy Server in a background thread """
        self.log_output.append("Starting Proxy Server...")
        logging.basicConfig(level=logging.DEBUG)  # Enable logging for debugging

        # Start the background thread for proxy server
        self.proxy_thread = ProxyServerThread(self)
        self.proxy_thread.start()

    @pyqtSlot(str)
    def log_to_ui(self, log_message):
        """ Append log messages from the background thread to the UI """
        self.log_output.append(log_message)


class ProxyServerThread(QThread):
    def __init__(self, proxy_page):
        super().__init__()
        self.proxy_page = proxy_page

    def run(self):
        """ Run the proxy server in the background """
        try:
            # Set up the proxy server (with SSL)
            server_address = ('127.0.0.1', 8080)
            logging.debug(f"Starting proxy server on {server_address}")

            # Create the HTTP server
            httpd = HTTPServer(server_address, ProxyHandler)

            # Set up SSL for the server
            context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            context.options |= ssl.OP_NO_SSLv2 | ssl.OP_NO_SSLv3  # Disable old SSL versions
            context.set_ciphers('DEFAULT')  # Use system default ciphers instead of a specific one

            # Log certificate loading attempt
            logging.debug("Loading certificates from certs/proxy.crt and certs/proxy.key...")
            context.load_cert_chain(certfile="certs/proxy.crt", keyfile="certs/proxy.key")

            # Log confirmation if certificates were loaded successfully
            logging.debug("Certificates loaded successfully!")

            # Wrap the server socket to enable SSL
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)

            # Log the server start
            logging.debug("Proxy server started with SSL")

            # Run the HTTP server
            httpd.serve_forever()

        except Exception as e:
            self.proxy_page.log_to_ui(f"Error starting proxy: {str(e)}")
            logging.error(f"Error starting proxy: {str(e)}")

