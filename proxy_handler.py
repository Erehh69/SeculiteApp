import socket
import ssl
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import socketserver
import os
from OpenSSL import crypto

# Set up logging for better debugging
logging.basicConfig(level=logging.DEBUG)

# Paths for Intermediate CA
INTERMEDIATE_CA_CERT = "certs/intermediateCA.pem"
INTERMEDIATE_CA_KEY = "certs/intermediateCA.key"
CERTS_DIR = "certs"

# Ensure CERTS_DIR exists
os.makedirs(CERTS_DIR, exist_ok=True)

class ProxyHandler(BaseHTTPRequestHandler):
    def do_CONNECT(self):
        try:
            self.send_response(200, "Connection Established")
            self.end_headers()
            logging.debug(f"Establishing SSL tunnel for {self.path}")
            client_socket = self.connection

            # Extract domain
            domain = self.path.split(":")[0]

            # Generate certificate for the domain
            cert_path, key_path = generate_cert(domain)

            # Secure connection between client and proxy
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=cert_path, keyfile=key_path)
            ssl_socket = context.wrap_socket(client_socket, server_side=True)

            logging.debug("SSL connection successfully established with client.")

            # Forward HTTPS data
            self.forward_https_traffic(ssl_socket)
        except ssl.SSLError as e:
            logging.error(f"SSL Error in CONNECT: {e}")
            self.send_error(502, f"SSL Error: {str(e)}")
        except Exception as e:
            logging.error(f"General Error in CONNECT: {e}")
            self.send_error(500, str(e))

    def forward_https_traffic(self, ssl_socket):
        """Forward HTTPS traffic correctly"""
        try:
            remote_host, remote_port = self.path.split(':')
            remote_port = int(remote_port) if remote_port.isdigit() else 443

            # Connect to the remote server with SSL
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
        except ssl.SSLError as e:
            logging.error(f"SSL forwarding error: {e}")
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


def generate_cert(domain):
    """Generate a certificate signed by the Intermediate CA for a given domain with SAN support."""
    cert_path = os.path.join(CERTS_DIR, f"{domain}.crt")
    key_path = os.path.join(CERTS_DIR, f"{domain}.key")

    # Skip if certificate already exists
    if os.path.exists(cert_path) and os.path.exists(key_path):
        return cert_path, key_path

    # Load Intermediate CA
    with open(INTERMEDIATE_CA_CERT, "r") as f:
        ca_cert = crypto.load_certificate(crypto.FILETYPE_PEM, f.read())

    with open(INTERMEDIATE_CA_KEY, "r") as f:
        ca_key = crypto.load_privatekey(crypto.FILETYPE_PEM, f.read())

    # Create a new key pair
    key = crypto.PKey()
    key.generate_key(crypto.TYPE_RSA, 2048)

    # Create a certificate request
    req = crypto.X509Req()
    req.get_subject().CN = domain
    req.set_pubkey(key)
    req.sign(key, "sha256")

    # Create the new certificate
    cert = crypto.X509()
    cert.set_subject(req.get_subject())
    cert.set_serial_number(int.from_bytes(os.urandom(16), "big"))
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(31536000)  # Valid for 1 year
    cert.set_issuer(ca_cert.get_subject())
    cert.set_pubkey(req.get_pubkey())

    # Add Subject Alternative Name (SAN)
    san = f"DNS:{domain}".encode()
    cert.add_extensions([
        crypto.X509Extension(b"subjectAltName", False, san)
    ])

    cert.sign(ca_key, "sha256")

    # Save the certificate and key
    with open(cert_path, "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))

    with open(key_path, "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, key))

    logging.debug(f"Generated certificate for {domain} with SAN support")

    return cert_path, key_path
