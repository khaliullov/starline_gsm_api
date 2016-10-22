#!/usr/bin/python2.7

from json import dumps
import pprint

from flask import Flask
from flask import request

from server import lambda_handler


app = Flask(__name__)


@app.route('/starline/get_token', methods = ['GET', 'POST'])
def get_token():
    res = lambda_handler(request.json, {})
    return dumps(res)
