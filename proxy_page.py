import socket
import threading
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QListWidget, QListWidgetItem, 
    QPushButton, QSplitter
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
        """)

        layout = QVBoxLayout()

        self.intercept_button = QPushButton("Intercept: OFF")
        self.intercept_button.setCheckable(True)
        self.intercept_button.clicked.connect(self.toggle_intercept)
        layout.addWidget(self.intercept_button)

        self.request_list = QListWidget()
        self.request_list.itemClicked.connect(self.display_request_details)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.request_list)
        layout.addWidget(splitter)
        self.setLayout(layout)

        # Start Proxy Server
        self.proxy_thread = threading.Thread(target=self.start_proxy)
        self.proxy_thread.daemon = True
        self.proxy_thread.start()

    def toggle_intercept(self):
        if self.intercept_button.isChecked():
            self.intercept_button.setText("Intercept: ON")
            self.intercept_button.setStyleSheet("background-color: #E74C3C; color: white;")
        else:
            self.intercept_button.setText("Intercept: OFF")
            self.intercept_button.setStyleSheet("background-color: #3498DB; color: white;")

    def start_proxy(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('127.0.0.1', 8080))
        server_socket.listen(5)

        print("Proxy server running on port 8080...")

        while True:
            client_socket, addr = server_socket.accept()
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
            client_thread.daemon = True
            client_thread.start()

    def handle_client(self, client_socket):
        try:
            request = client_socket.recv(4096)

            # Check if it's a CONNECT request for HTTPS
            if request.startswith(b"CONNECT"):
                # Extract the host and port from the CONNECT request
                target_host = request.split(b' ')[1].split(b':')[0].decode()
                target_port = int(request.split(b' ')[1].split(b':')[1])

                # Establish connection to the target server
                target_socket = socket.create_connection((target_host, target_port))
                client_socket.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

                # Forward data between client and server
                self.forward_data(client_socket, target_socket)
            else:
                # Display HTTP request line (first line)
                request_line = request.split(b'\r\n')[0].decode(errors='ignore')
                self.request_list.addItem(QListWidgetItem(request_line))

                # Handle HTTP request
                host_line = [line for line in request.split(b'\r\n') if b"Host:" in line]
                if host_line:
                    target_host = host_line[0].split(b" ")[1].decode()
                    target_socket = socket.create_connection((target_host, 80))
                    target_socket.sendall(request)

                    response = target_socket.recv(4096)
                    client_socket.sendall(response)

                    target_socket.close()
            
            client_socket.close()

        except Exception as e:
            print("Error:", e)
        finally:
            client_socket.close()

    def forward_data(self, client_socket, target_socket):
        try:
            while True:
                client_socket.settimeout(1)
                target_socket.settimeout(1)

                try:
                    client_data = client_socket.recv(4096)
                    if client_data:
                        target_socket.sendall(client_data)
                except socket.timeout:
                    pass
                
                try:
                    target_data = target_socket.recv(4096)
                    if target_data:
                        client_socket.sendall(target_data)
                except socket.timeout:
                    pass

        except Exception as e:
            print("Forwarding Error:", e)
        finally:
            client_socket.close()
            target_socket.close()

    def display_request_details(self, item):
        print(f"Selected: {item.text()}")
