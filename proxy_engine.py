import base64
import socket
import threading
import ssl
import select
import json
from urllib.parse import urlparse
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
        self.intercepted_requests = []

    def start(self):
        self.running = True
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

    def stop(self):
        self.running = False

    def set_intercept(self, enabled: bool):
        self.intercept_enabled = lambda: enabled

    def clear_intercepted_requests(self):
        self.intercepted_requests.clear()
        self.log("[*] Intercepted requests list cleared.")

    def get_intercepted_requests(self):
        return self.intercepted_requests

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

            self.log(f"[+] HTTPS Interception: {target_host}:{target_port}")
            client_conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            cert, key = generate_cert(target_host)
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=cert, keyfile=key)
            ssl_client = context.wrap_socket(client_conn, server_side=True)

            context_client = ssl._create_unverified_context()
            server_sock = socket.create_connection((target_host, target_port))
            ssl_server = context_client.wrap_socket(server_sock, server_hostname=target_host)

            threading.Thread(target=self.forward, args=(ssl_client, ssl_server, "→"), daemon=True).start()
            threading.Thread(target=self.forward, args=(ssl_server, ssl_client, "←"), daemon=True).start()

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
            parsed = urlparse(url)
            host = parsed.hostname
            port = parsed.port or 80
            path = parsed.path or "/"
            if parsed.query:
                path += "?" + parsed.query

            self.log(f"[+] {method} request to {host}{path}")

            header_lines[0] = f"{method} {path} {version}"
            headers = []
            content_type = ""
            is_websocket = False

            for line in header_lines[1:]:
                lower = line.lower()
                if lower.startswith("host:"):
                    headers.append(f"Host: {host}")
                elif lower.startswith("connection:"):
                    if "upgrade" in lower:
                        headers.append(line)
                        is_websocket = True
                    else:
                        headers.append("Connection: close")
                elif lower.startswith("upgrade:"):
                    headers.append(line)
                    is_websocket = True
                elif lower.startswith("authorization:"):
                    try:
                        auth_header = line.split(" ")[1]
                        decoded = base64.b64decode(auth_header).decode('utf-8')
                        self.log(f"[+] Found Basic Auth: {decoded}")
                    except:
                        pass
                else:
                    headers.append(line)
                    if lower.startswith("content-type:"):
                        content_type = line.split(":", 1)[1].strip()

            headers.append("Connection: close")
            full_raw_request = "\r\n".join([header_lines[0]] + headers) + "\r\n\r\n" + body_part
            request_line = header_lines[0]

            with open("all_requests.log", "a", encoding='utf-8') as f:
                f.write(full_raw_request + "\n" + "-" * 80 + "\n")

            if method.upper() in ["POST", "PUT"] and "application/json" in content_type:
                try:
                    parsed_json = json.loads(body_part)
                    pretty_json = json.dumps(parsed_json, indent=2)
                    self.log(f"[+] Parsed JSON:\n{pretty_json}")
                except Exception as e:
                    self.log(f"[!] Failed to parse JSON: {e}")

            server_socket = socket.create_connection((host, port))

            if is_websocket:
                sec_websocket_key = None
                for line in header_lines[1:]:
                    if "Sec-WebSocket-Key:" in line:
                        sec_websocket_key = line.split(":", 1)[1].strip()
                        break

                if sec_websocket_key:
                    accept_key = self.generate_accept_key(sec_websocket_key)
                    websocket_response = f"HTTP/1.1 101 Switching Protocols\r\n" \
                                        f"Upgrade: websocket\r\n" \
                                        f"Connection: Upgrade\r\n" \
                                        f"Sec-WebSocket-Accept: {accept_key}\r\n\r\n"
                    client_socket.sendall(websocket_response.encode())
                    self.log(f"[WS] Handshake complete. Tunneling begins.")
                    threading.Thread(target=self.forward_websocket, args=(client_socket, server_socket, "→"), daemon=True).start()
                    threading.Thread(target=self.forward_websocket, args=(server_socket, client_socket, "←"), daemon=True).start()
                    return

            if self.intercept_enabled() and self.intercept_handler:
                def continue_callback(modified_data):
                    try:
                        if isinstance(modified_data, bytes):
                            modified_text = modified_data.decode(errors='ignore')
                        else:
                            modified_text = modified_data

                        headers_part, _, body = modified_text.partition("\r\n\r\n")
                        header_lines = headers_part.split("\r\n")

                        body_length = len(body.encode())
                        new_headers = []
                        has_length = False

                        for line in header_lines[1:]:
                            if line.lower().startswith("content-length:"):
                                new_headers.append(f"Content-Length: {body_length}")
                                has_length = True
                            else:
                                new_headers.append(line)

                        if not has_length:
                            new_headers.append(f"Content-Length: {body_length}")

                        final_data = f"{header_lines[0]}\r\n" + "\r\n".join(new_headers) + "\r\n\r\n" + body
                        self.log(f"[→] Forwarding:\n{header_lines[0]}")
                        server_socket.sendall(final_data.encode())

                        while True:
                            response = server_socket.recv(4096)
                            if not response:
                                break
                            client_socket.sendall(response)

                    except Exception as e:
                        self.log(f"[!] Callback error: {e}")
                    finally:
                        server_socket.close()
                        client_socket.close()

                self.intercept_handler(request_line, full_raw_request, continue_callback)
                return

            server_socket.sendall(full_raw_request.encode())
            threading.Thread(target=self.forward, args=(server_socket, client_socket, "←"), daemon=True).start()
            threading.Thread(target=self.forward, args=(client_socket, server_socket, "→"), daemon=True).start()

        except Exception as e:
            self.log(f"[!] Exception in handle_http: {e}")
            client_socket.close()
    
    def generate_accept_key(sec_websocket_key):
        import hashlib
        import base64
        GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        accept_key = base64.b64encode(hashlib.sha1((sec_websocket_key + GUID).encode('utf-8')).digest())
        return accept_key.decode('utf-8')


    def forward(self, source, destination, direction="→"):
        try:
            while True:
                data = source.recv(4096)
                if not data:
                    break
                destination.sendall(data)

                if direction == "←":
                    self.log(f"[{direction}] Response from server:\n{data[:300].decode(errors='ignore')}")
        except Exception as e:
            self.log(f"[!] Forwarding error: {e}")
        finally:
            # Keep the sockets open for further forwarding if necessary.
            if source:
                source.close()
            if destination:
                destination.close()

    def forward_websocket(self, client_sock, server_sock, direction):
        try:
            sockets = [client_sock, server_sock]
            while True:
                readable, _, _ = select.select(sockets, [], [], 1)
                for sock in readable:
                    try:
                        data = sock.recv(4096)
                        if not data:
                            return

                        target = server_sock if sock is client_sock else client_sock

                        # Intercept data if enabled
                        if self.intercept_enabled() and self.intercept_handler:
                            try:
                                modified_data = self.intercept_handler(data, direction)
                                if modified_data is not None:
                                    data = modified_data
                            except Exception as e:
                                self.log(f"[!] Intercept handler WS error: {e}")

                        target.sendall(data)

                        if direction == "→":
                            self.log(f"[→] WS Data Sent: {data[:100].decode(errors='replace')}")
                        else:
                            self.log(f"[←] WS Data Received: {data[:100].decode(errors='replace')}")

                    except (ConnectionResetError, ssl.SSLError) as e:
                        self.log(f"[!] WS recv/send error: {e}")
                        return
        except Exception as e:
            self.log(f"[!] WebSocket forwarding error: {e}")
