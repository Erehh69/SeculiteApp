from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget,QListWidgetItem, QTextEdit, QHBoxLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt

class ProgressWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        self.setWindowTitle("Intruder Attack Progress")

        self.responses = []  # Store the responses
        self.filtered_responses = []  # Store the filtered responses
        self.filter_min_length = 0  # Minimum length for filtering

        layout = QVBoxLayout()

        # Filter by length input
        self.filter_input = QLineEdit(self)
        self.filter_input.setPlaceholderText("Filter responses by length (e.g., >100000)")
        self.filter_input.setStyleSheet("background-color: #333; color: white;")
        self.filter_input.textChanged.connect(self.apply_filter)
        layout.addWidget(self.filter_input)

        # Response display list
        self.response_list = QListWidget(self)
        self.response_list.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout.addWidget(QLabel("Attack Responses:"))
        layout.addWidget(self.response_list)

        self.setLayout(layout)

        self.payloads = []  # This will store the payloads
        self.responses = []  # This will store the responses

    def add_response(self, payload, response, length):
        """
        Add the response from a payload and display it.
        """
        response_data = f"Payload: {payload}\nResponse Length: {length}\n{response}"
        self.responses.append((payload, response, length))  # Store full data
        self.update_response_list()

    def update_response_list(self):
        """
        Update the response list according to the filter settings.
        """
        self.response_list.clear()
        for payload, response, length in self.filtered_responses:
            item_text = f"Payload: {payload}\nResponse Length: {length}\n{response[:200]}..."  # Show first 200 chars
            item = QListWidgetItem(item_text)
            self.response_list.addItem(item)

    def set_payloads(self, payloads):
        """Set payloads that will be used for the attack."""
        self.payloads = payloads

    def add_response(self, payload, response, response_length):
        """Update the window with the response data."""
        display_text = f"Payload: {payload}, Length: {response_length}\nResponse:\n{response[:100]}\n{'-'*80}"
        self.responses.append(display_text)
        self.response_display.append(display_text)

    def apply_filter(self):
        """
        Apply a filter to only show responses with length greater than or less than the specified value.
        """
        filter_text = self.filter_input.text()
        try:
            if filter_text.startswith(">"):
                self.filter_min_length = int(filter_text[1:])
            elif filter_text.startswith("<"):
                self.filter_min_length = int(filter_text[1:])
            else:
                self.filter_min_length = int(filter_text)
        except ValueError:
            self.filter_min_length = 0  # Reset if invalid filter

        # Filter the responses
        self.filtered_responses = [
            (payload, response, length)
            for payload, response, length in self.responses
            if length >= self.filter_min_length
        ]

        self.update_response_list()

