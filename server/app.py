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

from core.client_boundary import Client

from core.messages import JoinGameRequest, JoinGameResponse
from core.messages import StartGameRequest, StartGameResponse
from core.messages import PlayerCountRequest, PlayerCountResponse
from core.game import Game

DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_ADDRESS = os.environ.get('DB_ADDRESS')

CLIENT_PORT = os.environ.get('CLIENT_PORT')

MIN_PLAYERS = 3
MAX_PLAYERS = 6

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

# @APP.route('/api/test', methods=['GET'])
# def handleGet():
#     raw_data = dict(flask.request.args)
#     accusation = messages.PlayerAccusation(**raw_data)
#     logging.info('GET call, Received: %s', accusation)

#     result = database.validate_accusation(
#         game_id=game_id,
#         suspect_card=accusation.suspect,
#         weapon_card=accusation.weapon,
#         room_card=accusation.room)

#     response = {'correct': result}

#     return jsonify(response)

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

clients = {}
hostID = None
game = None

@APP.route('/api/join_game', methods=['GET'])
def join():
    global hostID
    global game
    
    join_request = JoinGameRequest.from_dict(request.args)

    player_count = len(clients)
    if player_count >= MAX_PLAYERS:
        return JoinGameResponse(accepted = False, gameID = -1)

    client_id = database.generate_uuid()

    if len(clients) == 0:
        hostID = client_id

    newClient = Client(join_request.name, request.remote_addr, CLIENT_PORT)
    clients[client_id] = newClient

    return JoinGameResponse(client_id = client_id, accepted = True, gameID = 1)

@APP.route('/api/start_game', methods=['GET'])
def start_game():
    global hostID
    global game

    start_request = StartGameRequest.from_dict(request.args)

    player_count = len(clients)
    if player_count < MIN_PLAYERS or player_count > MAX_PLAYERS:
        return StartGameResponse(accepted = False)

    if hostID == start_request.client_id:
        game = Game(list(clients.values()))

    return StartGameResponse(accepted = True)

@APP.route('/api/number_of_players', methods=['GET'])
def player_count():
    start_request = PlayerCountRequest.from_dict(request.args)
    return PlayerCountResponse(count = len(clients))

@APP.route('/api/step_game', methods=['GET'])
def step_game():
    global game
    step_request = PlayerCountRequest.from_dict(request.args)
    game.take_turn()

# Define all @APP.routes above this line.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.run(host='0.0.0.0')
    APP.secret_key == u'yolo'
