import json
from logger  import Logger
import requests


class HttpHelpers:

    def __init__(self):
        self.logger = Logger()

    def send_request(self, request_data):
        try:
            url = request_data["url"]
            self.logger.set_log("Http Request: " + url, True)
            resp = requests.post(url, data=json.dumps(request_data["body"]), headers=request_data["headers"])
            self.logger.set_log("Http Response: " + str(resp.json()), True)
        except Exception as e:
            self.logger.set_log('send_request(): ' + str(e), True)


