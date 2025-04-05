import threading
import time

class ProxyServer:
    """Handles the proxy server operations"""

    def __init__(self):
        self.is_running = False

    def start(self):
        """Starts the proxy server"""
        self.is_running = True
        while self.is_running:
            time.sleep(1)  # Simulate server running

    def stop(self):
        """Stops the proxy server"""
        self.is_running = False
