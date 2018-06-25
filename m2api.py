import requests
import json


class m2api(object):

    def __init__(self, url, username, password):
        super(m2api, self).__init__()
        self.url = url
        self.token = self.getToken(username, password)

    def getToken(self, username, password):
        payload = {
            "username": username,
            "password": password
        }
        data = json.dumps(payload)
        headers = {
            "Content-Type": 'application/json',
            "Content-Length" str(len(data))
        }
        token_url = self.url + "rest/V1/integration/admin/token"
        return self.m2req(token_url, headers=json.dumps(headers), data=data)

    def m2req(self, url, headers, data):
        try:
            res = requests.post(url, headers=headers, data=data)
            if res.status_code = 200:
                return res.content
            else:
                return False
        except Exception as e:
            print(e)
            return False
