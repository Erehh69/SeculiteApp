import logging
import urllib.parse
import requests
from http.server import BaseHTTPRequestHandler
import ssl

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class ProxyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        logging.debug("Handling GET request")
        self.handle_request('GET')

    def do_POST(self):
        logging.debug("Handling POST request")
        self.handle_request('POST')

    def do_PUT(self):
        logging.debug("Handling PUT request")
        self.handle_request('PUT')

    def do_DELETE(self):
        logging.debug("Handling DELETE request")
        self.handle_request('DELETE')

    def handle_request(self, method):
        try:
            # Log the request details
            logging.debug(f"Received request for path: {self.path} with method: {method}")

            # Read the body of the request (if any)
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b''

            # Prepare headers (exclude 'Host' header as it's already part of the target URL)
            headers = {key: value for key, value in self.headers.items() if key.lower() != 'host'}

            # Log request information
            logging.debug(f"Original path: {self.path}")
            base_url = "http://127.0.0.1:8000"  # Target server URL

            # Construct the target URL correctly
            target_url = urllib.parse.urljoin(base_url, self.path)  # Safely join the base URL and path
            logging.debug(f"Forwarding to target URL: {target_url}")

            # Forward the request to the target server
            response = requests.request(
                method,
                target_url,
                headers=headers,
                data=body,
                allow_redirects=False
            )

            # Log the response status and body for debugging
            logging.debug(f"Received response with status code: {response.status_code}")
            logging.debug(f"Response body (first 100 chars): {response.text[:100]}")

            # Send the response back to the client
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                # Ensure we keep the connection alive if possible
                if key.lower() == "connection" and value.lower() == "close":
                    self.send_header("Connection", "close")
                else:
                    self.send_header(key, value)
            self.end_headers()
            self.wfile.write(response.content)

        except Exception as e:
            # Log the error and send a 500 server error response
            logging.error(f"Error handling request: {str(e)}")
            self.send_error(500, f"Proxy error: {e}")
            print(f"Error: {e}")  # Print the error to the terminal for debugging
