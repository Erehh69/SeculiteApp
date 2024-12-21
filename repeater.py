import requests

class Repeater:
    def __init__(self):
        pass

    def repeat_request(self, url, method='GET', data=None):
        if method.upper() == 'POST':
            response = requests.post(url, data=data)
        else:
            response = requests.get(url)
        return response
