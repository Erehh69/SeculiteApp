import socket
import threading
import ssl
import os
from dynamic_cert import generate_cert  # assumes your generate_cert is in dynamic_cert.py

LISTEN_HOST = '127.0.0.1'
LISTEN_PORT = 8080

def handle_client(client_conn):
    try:
        request = client_conn.recv(65536).decode('utf-8', errors='ignore')
        if not request.startswith('CONNECT'):
            client_conn.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n\r\n")
            client_conn.close()
            return

        # Parse the target host and port from CONNECT request
        target_host, target_port = request.split(' ')[1].split(':')
        target_port = int(target_port)

        print(f"[+] Intercepting HTTPS for {target_host}:{target_port}")

        # Acknowledge HTTPS tunnel establishment
        client_conn.sendall(b"HTTP/1.1 200 Connection Established\r\n\r\n")

        # 🧠 Generate dynamic cert and wrap client conn
        crt_path, key_path = generate_cert(target_host)

        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=crt_path, keyfile=key_path)

        ssl_client = context.wrap_socket(client_conn, server_side=True)

        # 🧠 Connect to the actual remote server
        server_sock = socket.create_connection((target_host, target_port))
        ssl_server = ssl.create_default_context().wrap_socket(server_sock, server_hostname=target_host)

        # 🧠 Start bidirectional forwarding
        threading.Thread(target=forward, args=(ssl_client, ssl_server), daemon=True).start()
        threading.Thread(target=forward, args=(ssl_server, ssl_client), daemon=True).start()

    except Exception as e:
        print(f"[!] Connection error: {e}")
        client_conn.close()

def forward(source, destination):
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

def start_proxy():
    print(f"[+] SecuLite Proxy listening on https://{LISTEN_HOST}:{LISTEN_PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((LISTEN_HOST, LISTEN_PORT))
        server.listen(100)
        while True:
            client_sock, _ = server.accept()
            threading.Thread(target=handle_client, args=(client_sock,), daemon=True).start()

if __name__ == "__main__":
    start_proxy()
