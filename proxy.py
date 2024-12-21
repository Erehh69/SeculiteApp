import threading
import socket
import select

class Proxy:
    def __init__(self):
        self.host = '127.0.0.1'  # Default host
        self.port = 8080  # Default port
        self.intercept = False
        self.intercepted_requests = []

    def set_proxy(self, host, port):
        """Sets the proxy's host and port."""
        self.host = host
        self.port = int(port)
        print(f"Proxy set to {self.host}:{self.port}")

    def toggle_intercept(self, enable):
        """Toggles the intercept functionality."""
        self.intercept = enable
        status = "on" if enable else "off"
        print(f"Intercept is now {status}")

    def forward_request(self, request):
        """Forward the intercepted request."""
        print(f"Forwarding intercepted request: {request}")
        # Here you'd forward the request to the destination server

    def drop_request(self, request):
        """Drops the intercepted request."""
        print(f"Dropping intercepted request: {request}")

    def start_proxy(self):
        """Start proxy listener in a thread."""
        threading.Thread(target=self.proxy_listener).start()

    def proxy_listener(self):
        """Listen for HTTP requests and optionally intercept them."""
        print(f"Proxy listening on {self.host}:{self.port}")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen(5)
            print("Waiting for connections...")
            while True:
                client_socket, client_address = server_socket.accept()
                with client_socket:
                    print(f"Connection from {client_address}")
                    request = client_socket.recv(4096).decode('utf-8')
                    if request:
                        if self.intercept:
                            print("Intercepting request:")
                            print(request)
                            self.intercepted_requests.append(request)
                            # This is where you would modify the request before forwarding or dropping it
                        else:
                            self.forward_request(request)
                        # Simulate forwarding the response (for testing purposes)
                        client_socket.sendall(b"HTTP/1.1 200 OK\r\n\r\nProxy Response")
