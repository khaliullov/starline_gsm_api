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


def _ajax_request(host, method, path, params=None, _headers={}):
    handle = http.client.HTTPSConnection(host)
    headers = {"Content-type": "application/json; charset=utf-8",
               "User-Agent": "Mozilla/5.0",
               "Accept": "application/json"}
    headers.update(_headers)

    handle.request(method, path, params, headers)
    res = handle.getresponse()
    if res.status != 200:
        response['codestring'] = 'Failed to auth'
        response['code'] = res.status
        return response
    return json.loads(res.read().decode('utf-8'))


def get_credentials(req):
    credentials = _ajax_request('xu3g4ixx6c.execute-api.eu-central-1.amazonaws.com',
                                'POST', '/starline/get_token', json.dumps(req))

    return credentials


def get_devices(credentials):
    devices = _ajax_request('dev.starline.ru', 'GET', '/json/user/' +
                            credentials['user_id'] + '/devices', None,
                            {"Cookie": credentials['cookie']})
    return devices


def get_state(credentials, device_id):
    state = _ajax_request('dev.starline.ru', 'GET', '/json/device/' +
                          device_id, None,
                          {"Cookie": credentials['cookie']})
    return state

def set_state(credentials, device_id, state={}):
    new_state = _ajax_request('dev.starline.ru', 'POST', '/json/device/' +
                              device_id + '/set_param', json.dumps(state),
                             {"Cookie": credentials['cookie']})
    return new_state


def main():
    result = get_credentials(request)
    pprint.pprint(result)
    if 'code' not in result or int(result['code']) != 200:
        pprint.pprint(result)
        return 1

    credentials = result

    result = get_devices(credentials)
    if int(result['code']) != 200:
        pprint.pprint(result)
        return 2

    devices = result['devices']

    result = get_state(credentials, devices[0]['device_id'])

    if int(result['code']) != 200:
        pprint.pprint(result)
        return 3

    state = result

    print("Devices:")
    pprint.pprint(devices)
    print("Device[0] state:")
    pprint.pprint(state['device']['state'])

    # disalarm
    # result = set_state(credentials, devices[0]['device_id'], {'arm': 0})
    # print("Disalarmed:")
    # pprint.pprint(result)

    # alarm
    # result = set_state(credentials, devices[0]['device_id'], {'arm': 1})
    # print("Alarmed:")
    # pprint.pprint(result)


if __name__== '__main__':
    main()
