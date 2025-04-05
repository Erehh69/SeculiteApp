import socket
import threading
import ssl
from dynamic_cert import generate_cert

LISTEN_HOST = '127.0.0.1'
LISTEN_PORT = 8080

class ProxyEngine:
    def __init__(self, log_callback=print):
        self.running = False
        self.log = log_callback
        self.server_thread = None

    def start(self):
        """Start the proxy server in a separate thread."""
        self.running = True
        self.server_thread = threading.Thread(target=self.run_server, daemon=True)
        self.server_thread.start()

    def stop(self):
        """Stop the proxy server."""
        self.running = False

    def run_server(self):
        """Runs the proxy server to intercept traffic."""
        self.log(f"[+] SecuLite Proxy listening on https://{LISTEN_HOST}:{LISTEN_PORT}")
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
        """Handle the connection from a client."""
        try:
            request = client_conn.recv(65536).decode('utf-8', errors='ignore')
            if not request.startswith('CONNECT'):
                client_conn.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
                client_conn.close()
                return

            target_host, target_port = request.split(' ')[1].split(':')
            target_port = int(target_port)
            self.log(f"[+] Intercepting HTTPS for {target_host}:{target_port}")

            client_conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

            crt_path, key_path = generate_cert(target_host)

            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile=crt_path, keyfile=key_path)

            ssl_client = context.wrap_socket(client_conn, server_side=True)

            server_sock = socket.create_connection((target_host, target_port))
            ssl_server = ssl.create_default_context().wrap_socket(server_sock, server_hostname=target_host)

            threading.Thread(target=self.forward, args=(ssl_client, ssl_server), daemon=True).start()
            threading.Thread(target=self.forward, args=(ssl_server, ssl_client), daemon=True).start()

        except Exception as e:
            self.log(f"[!] Connection error: {e}")
            client_conn.close()

    def forward(self, source, destination):
        """Forward data between source and destination."""
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
