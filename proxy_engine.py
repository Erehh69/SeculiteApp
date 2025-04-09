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

    def set_intercept(self, enabled: bool):
        self.intercept_enabled = lambda: enabled


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

            self.log(f"[+] HTTPS Interception: {target_host}:{target_port}")
            client_conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            # Intercept with certificate
            cert, key = generate_cert(target_host)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=cert, keyfile=key)
            ssl_client = context.wrap_socket(client_conn, server_side=True)

            # Connect to target
            context_client = ssl._create_unverified_context()
            server_sock = socket.create_connection((target_host, target_port))
            ssl_server = context_client.wrap_socket(server_sock, server_hostname=target_host)

            # Forward both directions with intercept logic
            threading.Thread(target=self.forward, args=(ssl_client, ssl_server), daemon=True).start()
            threading.Thread(target=self.forward, args=(ssl_server, ssl_client), daemon=True).start()

        except Exception as e:
            self.log(f"[!] HTTPS error: {e}")
            client_conn.close()

    def handle_http(self, client_socket, data):
        try:
            request_text = data
            self.log(f"[RAW REQUEST]:\n{request_text[:300]}")
            header_part, _, body_part = request_text.partition("\r\n\r\n")
            header_lines = header_part.split("\r\n")

            if not header_lines or not header_lines[0]:
                self.log("[!] Malformed HTTP request")
                return

            method, url, version = header_lines[0].split()
            from urllib.parse import urlparse
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or 80
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query
            header_lines[0] = f"{method} {path} {version}"

            headers = []
            for line in header_lines[1:]:
                if line.lower().startswith("host:"):
                    headers.append(f"Host: {host}")
                elif line.lower().startswith("connection:"):
                    headers.append("Connection: close")
                else:
                    headers.append(line)
            headers.append("Connection: close")
            full_raw_request = "\r\n".join([header_lines[0]] + headers) + "\r\n\r\n" + body_part
            request_line = header_lines[0]

            if self.intercept_enabled() and self.intercept_handler:
                self.intercept_handler(request_line, full_raw_request)
                return  # stop here until GUI decides what to do

            # If not intercepted, proceed to send immediately
            final_request = full_raw_request.encode()
            with socket.create_connection((host, port)) as server_socket:
                server_socket.sendall(final_request)
                while True:
                    response = server_socket.recv(4096)
                    if not response:
                        break
                    client_socket.sendall(response)
                    if b"HTTP/" in response:
                        snippet = response[:300].decode(errors="ignore")
                        self.log(f"[<] Response:\n{snippet.strip()}")

        except Exception as e:
            self.log(f"[!] Exception in handle_http: {e}")



    def forward(self, source, destination):
        try:
            while True:
                data = source.recv(4096)
                if not data:
                    break

                # Debug: log a snippet of what’s being forwarded back to browser
                if b"HTTP/1.1" in data:
                    snippet = data[:300].decode("utf-8", errors="ignore")
                    self.log(f"[>] Forwarding response snippet:\n{snippet}")

                destination.sendall(data)
        except Exception as e:
            self.log(f"[!] Forward error: {e}")