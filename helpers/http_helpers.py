import json
from logger import Logger
import requests


class HttpHelpers:

    def __init__(self):
        self.logger = Logger()

    def send_request(self, request_data):
        method = request_data["method"]
        if method == "post":
            self.post_request(request_data)
        if method == "get":
            self.get_request_content(request_data)

    def get_request_content(self, request_data):
        try:
            url = request_data["url"]
            self.logger.set_log("Http Request: " + url, True)
            resp = requests.get(url, params=request_data["params"], headers=request_data["headers"])
            self.logger.set_log("Http Response: " + str(resp), True)
            return resp
        except Exception as e:
            self.logger.set_log('send_request(): ' + str(e), True)

    def post_request(self, request_data):
        try:
            url = request_data["url"]
            self.logger.set_log("Http Request: " + url, True)
            resp = requests.post(url, data=json.dumps(request_data["body"]), headers=request_data["headers"])
            self.logger.set_log("Http Response: " + str(resp.json()), True)
        except Exception as e:
            self.logger.set_log('send_request(): ' + str(e), True)


