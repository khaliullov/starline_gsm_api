#!/usr/bin/python3

import http.client
import json
import pprint


request = {
    "login": "_USER_EMAIL_",
    "pass": "_USER_PASSWORD_",
    "app.data": {
        "os_type": "Nucleus RTOS",
        "os_version": "1.3.1:3.50",
        "app_version": "0.0.1",
        "phone_model": "GARMIN-FENIX-3-HR",
        "network_type": "BLE",
        "theme": "black",
        "language": "ru",
        "locale": "USSR"
    }
}


def main(event):
    aws = http.client.HTTPSConnection("xu3g4ixx6c.execute-api.eu-central-1.amazonaws.com")

    headers = {"Content-type": "application/json; charset=utf-8",
               "User-Agent": "Mozilla/5.0",
               "Accept": "application/json"}
    params = json.dumps(event)
    aws.request("POST", "/starline/get_token", params, headers)
    res = aws.getresponse()
    if res.status != 200:
        response['codestring'] = 'Failed to auth'
        response['code'] = res.status
        return response
    return res.read()


res = main(request)

pprint.pprint(res)
