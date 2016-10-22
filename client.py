#!/usr/bin/python3
# coding=utf8

import argparse
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
DEFAULT_ENDPOINT = 'xu3g4ixx6c.execute-api.eu-central-1.amazonaws.com'


def _ajax_request(host, http_scheme, method, path, params=None, _headers={}):
    if http_scheme:
        handle = http.client.HTTPConnection(host)
    else:
        handle = http.client.HTTPSConnection(host)
    headers = {"Content-type": "application/json; charset=utf-8",
               "User-Agent": "Mozilla/5.0",
               "Accept": "application/json"}
    headers.update(_headers)

    handle.request(method, path, params, headers)
    res = handle.getresponse()
    if res.status != 200:
        response = {}
        response['codestring'] = 'Failed to auth'
        response['code'] = res.status
        return response
    return json.loads(res.read().decode('utf-8'))


def get_credentials(req):
    credentials = _ajax_request(req['endpoint'], req['http'],
                                'POST', '/starline/get_token', json.dumps(req))

    return credentials


def get_devices(credentials):
    devices = _ajax_request('dev.starline.ru', False, 'GET', '/json/user/' +
                            credentials['user_id'] + '/devices', None,
                            {"Cookie": credentials['cookie']})
    return devices


def get_state(credentials, device_id):
    state = _ajax_request('dev.starline.ru', False, 'GET', '/json/device/' +
                          device_id, None,
                          {"Cookie": credentials['cookie']})
    return state

def set_state(credentials, device_id, state={}):
    new_state = _ajax_request('dev.starline.ru', False, 'POST', '/json/device/' +
                              device_id + '/set_param', json.dumps(state),
                             {"Cookie": credentials['cookie']})
    return new_state


def main(_request = request):
    result = get_credentials(_request)
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

    if 'code' in result and int(result['code']) != 200:
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
    parser = argparse.ArgumentParser(description='Starline GSM client')
    parser.add_argument('-u', '--user', help='user name')
    parser.add_argument('-p', '--password', help='password')
    parser.add_argument('-http', '--http', help='force http scheme', action='store_true')
    parser.add_argument('-ep', '--endpoint', help='endpoint', default=DEFAULT_ENDPOINT)
    parser.add_argument('-cs', '--captchasid', help='captcha SID')
    parser.add_argument('-cc', '--captchacode', help='captcha code')
    args = parser.parse_args()
    _request = request
    _request['login'] = args.user
    _request['pass'] = args.password
    _request['endpoint'] = args.endpoint
    _request['http'] = args.http
    if args.captchasid:
        _request['captchaSid'] = args.captchasid
    if args.captchacode:
        _request['captchaCode'] = args.captchacode
    main(_request)
