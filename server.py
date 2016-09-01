from __future__ import print_function

import hashlib
import httplib
import urllib
import json


GET_TOKEN_URL = "/apiV3/application/getToken?appId=4&secret=82f4ec68b8769dcda04a76735b93ebc4"
LOGIN_URL = "/apiV3/user/login"
AUTH_URL = "/json/v2/auth.slid"


def lambda_handler(event, context):
    response = {}

    h = hashlib.sha1()
    h.update(event['pass'])
    response['pass'] = h.hexdigest()
    response['login'] = event['login']

    ids = httplib.HTTPSConnection("id.starline.ru")

    ids.request("GET", GET_TOKEN_URL)
    res = ids.getresponse()
    if res.status != 200:
        response['codestring'] = 'Failed to get token'
        response['code'] = res.status
        return response
    result = json.load(res)
    if result['state'] != 1:
        response['codestring'] = 'Invalid state while getting token'
        response['code'] = 403
        return response
    token = result['desc']['token']

    params = urllib.urlencode({'login': event['login'], 'pass': response['pass']})
    headers = {'token': token, "Content-type": "application/x-www-form-urlencoded",
               "User-Agent": "Mozilla/5.0", "Accept": "application/json"}
    ids.request("POST", LOGIN_URL, params, headers)
    res = ids.getresponse()
    if res.status != 200:
        response['codestring'] = 'Failed to login'
        response['code'] = res.status
        return response
    result = json.load(res)
    if result['state'] != 1:
        response['codestring'] = 'Invalid state while getting token'
        response['code'] = 403
    if 'user_token' in result['desc']:
        response['token'] = str(result['desc']['user_token'])
    else:
        response['codestring'] = str(result['desc']['message'])
        response['code'] = 403
        return response

    dev = httplib.HTTPSConnection("dev.starline.ru")

    headers = {"Content-type": "application/json; charset=utf-8",
               "User-Agent": "Mozilla/5.0",
               "Accept": "application/json"}
    params = json.dumps({"slid_token": response['token'],
                         "app.data": event['app.data']})
    dev.request("POST", AUTH_URL, params, headers)
    res = dev.getresponse()
    if res.status != 200:
        response['codestring'] = 'Failed to auth'
        response['code'] = res.status
        return response
    result = json.load(res)
    response['codestring'] = str(result['codestring'])
    response['code'] = str(result['code'])
    response['user_id'] = str(result['user_id'])
    response['cookie'] = res.getheader('Set-Cookie', None)
    response['realplexor_id'] = str(result['realplexor_id'])
    if response['cookie']:
        response['cookie'] = response['cookie'].split(';', 1)[0]
    return response
