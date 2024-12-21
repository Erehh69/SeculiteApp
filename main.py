from PyQt5 import QtWidgets, uic, QtCore
import sys
from proxy import Proxy
from intruder import Intruder
from repeater import Repeater

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        uic.loadUi('ui/main_window.ui', self)

        # Initialize Proxy
        self.proxy = Proxy()

        # Connect buttons to their functions
        self.proxy_button.clicked.connect(self.open_proxy_window)
        self.intruder_button.clicked.connect(self.open_intruder_window)
        self.repeater_button.clicked.connect(self.open_repeater_window)

    def open_proxy_window(self):
        self.proxy_window = ProxyWindow(self.proxy)
        self.proxy_window.show()

    def open_intruder_window(self):
        self.intruder_window = IntruderWindow()
        self.intruder_window.show()

    def open_repeater_window(self):
        self.repeater_window = RepeaterWindow()
        self.repeater_window.show()

class ProxyWindow(QtWidgets.QWidget):
    def __init__(self, proxy):
        super(ProxyWindow, self).__init__()
        uic.loadUi('ui/proxy_window.ui', self)
        self.proxy = proxy

        # Set up buttons
        self.test_button.clicked.connect(self.test_proxy)
        self.toggle_intercept_button.clicked.connect(self.toggle_intercept)
        self.forward_button.clicked.connect(self.forward_request)
        self.drop_button.clicked.connect(self.drop_request)

        # Timer to refresh intercepted requests
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_intercepted_requests)
        self.timer.start(1000)  # Refresh every second

    def test_proxy(self):
        host = self.host_input.text()
        port = self.port_input.text()
        self.proxy.set_proxy(host, port)
        self.proxy.start_proxy()  # Start proxy in a separate thread
        print(f"Testing proxy with host: {host}, port: {port}")

    def toggle_intercept(self):
        intercept_enabled = self.toggle_intercept_button.isChecked()
        self.proxy.toggle_intercept(intercept_enabled)

    def forward_request(self):
        selected_request = self.get_selected_request()
        if selected_request:
            self.proxy.forward_request(selected_request)
            print(f"Forwarding request: {selected_request}")

    def drop_request(self):
        selected_request = self.get_selected_request()
        if selected_request:
            self.proxy.drop_request(selected_request)
            print(f"Dropping request: {selected_request}")

    def update_intercepted_requests(self):
        """Update the list of intercepted requests in the UI."""
        self.intercepted_requests_list.clear()
        for request in self.proxy.intercepted_requests:
            self.intercepted_requests_list.addItem(request[:100])  # Show the first 100 chars of the request

    def get_selected_request(self):
        """Returns the selected intercepted request."""
        selected_row = self.intercepted_requests_list.currentRow()
        if selected_row >= 0:
            return self.proxy.intercepted_requests[selected_row]
        return None


# Main function to run the app
def main():
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
