import socket
import ssl
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import socketserver

CERT_FILE = "certs/proxy.crt"
KEY_FILE = "certs/proxy.key"

class ProxyHandler(BaseHTTPRequestHandler):
    def do_CONNECT(self):
        try:
            self.send_response(200, "Connection Established")
            self.end_headers()
            logging.debug(f"Establishing SSL tunnel for {self.path}")
            client_socket = self.connection

            # Secure connection between client and proxy
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)
            ssl_socket = context.wrap_socket(client_socket, server_side=True)
            logging.debug("SSL connection successfully established with client.")

            # Forward HTTPS data
            self.forward_https_traffic(ssl_socket)
        except Exception as e:
            logging.error(f"Error in CONNECT: {e}")
            self.send_error(500, str(e))

    def forward_https_traffic(self, ssl_socket):
        """Forward HTTPS traffic correctly"""
        try:
            remote_host, remote_port = self.path.split(':')
            remote_port = int(remote_port) if remote_port.isdigit() else 443

            remote_socket = ssl.create_default_context().wrap_socket(
                socket.socket(socket.AF_INET, socket.SOCK_STREAM),
                server_hostname=remote_host
            )
            remote_socket.connect((remote_host, remote_port))

            while True:
                data = ssl_socket.recv(4096)
                if not data:
                    break
                remote_socket.sendall(data)

                response_data = remote_socket.recv(4096)
                ssl_socket.sendall(response_data)

            remote_socket.close()
            ssl_socket.close()
        except Exception as e:
            logging.error(f"Error forwarding HTTPS traffic: {e}")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"This is a proxy server.")

class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""
    daemon_threads = True
    allow_reuse_address = True
