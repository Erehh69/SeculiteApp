import socket
import threading
import ssl
from dynamic_cert import generate_cert

LISTEN_HOST = '127.0.0.1'
LISTEN_PORT = 8080


class ProxyEngine:
    def __init__(self, log_callback=print, intercept_enabled=lambda: False, intercept_handler=None):
        self.running = False
        self.log = log_callback
        self.intercept_enabled = intercept_enabled
        self.intercept_handler = intercept_handler
        self.server_thread = None

    def start(self):
        self.running = True
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

    def stop(self):
        self.running = False

    def run_server(self):
        self.log(f"[+] Proxy running on {LISTEN_HOST}:{LISTEN_PORT}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((LISTEN_HOST, LISTEN_PORT))
            server.listen(100)
            while self.running:
                try:
                    client_sock, _ = server.accept()
                    threading.Thread(target=self.handle_client, args=(client_sock,), daemon=True).start()
                except Exception as e:
                    self.log(f"[!] Accept error: {e}")

    def handle_client(self, client_conn):
        try:
            request = client_conn.recv(65536).decode('utf-8', errors='ignore')

            if request.startswith('CONNECT'):
                self.handle_https(client_conn, request)
            else:
                self.handle_http(client_conn, request)

        except Exception as e:
            self.log(f"[!] Error handling client: {e}")
            client_conn.close()

    def handle_https(self, client_conn, request):
        try:
            host_port = request.split(' ')[1]
            target_host, target_port = host_port.split(':')
            target_port = int(target_port)

            self.log(f"[+] Handling HTTPS: {target_host}:{target_port}")
            client_conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            cert, key = generate_cert(target_host)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=cert, keyfile=key)
            ssl_client = context.wrap_socket(client_conn, server_side=True)

            # Connect to real server
            context_client = ssl._create_unverified_context()
            server_sock = socket.create_connection((target_host, target_port))
            ssl_server = context_client.wrap_socket(server_sock, server_hostname=target_host)

            # Intercept logic
            if self.intercept_enabled():
                self.log(f"[+] Intercepted HTTPS request to {target_host}")
                if self.intercept_handler:
                    self.intercept_handler(f"CONNECT {target_host}:{target_port}", "<SSL Intercepted>")

            threading.Thread(target=self.forward, args=(ssl_client, ssl_server), daemon=True).start()
            threading.Thread(target=self.forward, args=(ssl_server, ssl_client), daemon=True).start()

        except Exception as e:
            self.log(f"[!] HTTPS error: {e}")
            client_conn.close()

    def handle_http(self, client_conn, request):
        try:
            lines = request.split('\r\n')
            first_line = lines[0]
            method, full_url, _ = first_line.split()
            host = ""
            port = 80

            for line in lines:
                if line.lower().startswith("host:"):
                    host = line.split(":", 1)[1].strip()
                    break

            if ':' in host:
                host, port = host.split(':')
                port = int(port)

            self.log(f"[+] Handling HTTP: {host}:{port} -> {method} {full_url}")

            # Interception
            if self.intercept_enabled():
                if self.intercept_handler:
                    self.intercept_handler(first_line, request)

            remote = socket.create_connection((host, port))
            remote.sendall(request.encode())

            # Forwarding data
            threading.Thread(target=self.forward, args=(client_conn, remote), daemon=True).start()
            threading.Thread(target=self.forward, args=(remote, client_conn), daemon=True).start()

        except Exception as e:
            self.log(f"[!] HTTP error: {e}")
            client_conn.close()

    def forward(self, source, destination):
        try:
            while True:
                data = source.recv(4096)
                if not data:
                    break
                destination.sendall(data)
        except Exception:
            pass
        finally:
            source.close()
            destination.close()
