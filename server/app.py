import json
import logging
import os
import random
import socket
import time
import uuid

import flask
from flask import jsonify
from flask import request

from core import messages
from core import game_rules

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
game_id = database.generate_uuid()

# Give database time to get up and running.
ATTEMPTS = 5
for attempt in range(ATTEMPTS):
    if database.connect():
        break
    print('Waiting for database to start: Attempt ' + str(attempt + 1) + '/' + str(ATTEMPTS))
    time.sleep(1)

APP = flask.Flask(__name__)


@APP.route('/')
def index():
    return f'This is the Server'

@APP.route('/api/test', methods=['GET'])
def handleGet():
    raw_data = dict(flask.request.args)
    accusation = messages.PlayerAccusation(**raw_data)
    logging.info('GET call, Received: %s', accusation)

    result = database.validate_accusation(
        game_id=game_id,
        suspect_card=accusation.suspect,
        weapon_card=accusation.weapon,
        room_card=accusation.room)

    response = {'correct': result}

    return jsonify(response)

@APP.route('/api/db/create_database', methods=['GET'])
def setupDB():
    create_result = database.create_database()
    logging.info(create_result)
    return 'Database Created!'

@APP.route('/api/setup_game', methods=['GET'])
def setupGame():
    user_id = database.generate_uuid()
    setup_result = database.start_game(game_id=game_id,
                                       user_id=user_id,
                                       user_name='admin',
                                       country_code=1,
                                       status='OK')
    logging.info(setup_result)
    murder_deck_result = database.set_murder_deck(
        game_id=game_id,
        suspect_card=random.choice(game_rules.NAMES),
        weapon_card=random.choice(game_rules.WEAPONS),
        room_card=random.choice(game_rules.ROOMS)
    )
    logging.info(murder_deck_result)
    return 'Game Setup Complete!'


# Define all @APP.routes above this line.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.run(host='0.0.0.0')
    APP.secret_key == u'yolo'
