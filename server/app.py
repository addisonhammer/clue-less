import json
import logging
import os
import random
import socket
import time

import flask
from flask import jsonify
from flask import request

APP = flask.Flask(__name__)

VALID = (
    'FALSE',
    'TRUE'
)

@APP.route('/')
def index():
    return f'This is the index'

@APP.route('/api/test', methods=['GET'])
def handleGet():
    logging.info('GET call, Received: ' + str(flask.request.args))

    response = {'correct': random.choice(VALID)}

    return jsonify(response)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.run(host='0.0.0.0')
    APP.secret_key == u'yolo'