import json
import logging
import os
import random
import socket
import time

import flask
from flask import jsonify
from flask import request

from core import messages

from clueless_db import Clueless_Database

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_ADDRESS = os.environ.get('DB_ADDRESS')

database_settings = {
    'database': DB_NAME,
    'user': DB_USER,
    'password': DB_PASSWORD,
    'host': DB_ADDRESS,
}

# Setup database
database = Clueless_Database(database_settings)

# Give database time to get up and running.
ATTEMPTS = 5
for attempt in range(ATTEMPTS):
    if database.connect():
        break
    print('Waiting for database to start: Attempt ' + str(attempt + 1) + '/' + str(ATTEMPTS))
    time.sleep(1)

APP = flask.Flask(__name__)

VALID = (
    'FALSE',
    'TRUE'
)

@APP.route('/')
def index():
    return f'This is the Server'

@APP.route('/api/test', methods=['GET'])
def handleGet():
    raw_data = dict(flask.request.args)
    accusation = messages.PlayerAccusation(**raw_data)
    logging.info('GET call, Received: %s', accusation)

    response = {'correct': random.choice(VALID)}

    return jsonify(response)

@APP.route('/api/db/create_database', methods=['GET'])
def setupDB():
    return str(database.create_database())

# Define all @APP.routes above this line.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.run(host='0.0.0.0')
    APP.secret_key == u'yolo'
