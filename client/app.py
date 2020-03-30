"""Example Client that generates a random accusation and sends it to the server."""
import json
import logging
import os
import random
import socket
import time
import uuid

import flask
import requests

from core import game_rules
from core import messages

APP = flask.Flask(__name__)

SERVER_IP = os.environ.get('SERVER_IP')
SERVER_PORT = os.environ.get('SERVER_PORT')

@APP.route('/', methods=['GET'])
def handleGet():
    logging.info('GET call, serving GUESS template')
    return flask.render_template('clue.html.jinja')


@APP.route('/', methods=['POST'])
def handlePost():
    url = 'http://' + SERVER_IP + ':' + SERVER_PORT + '/api/test'
    logging.info(url)

    accusation = messages.PlayerAccusation(
        message_id=uuid.uuid4().fields[0],
        player=flask.request.form['player'],
        accused=random.choice(game_rules.NAMES),
        room=random.choice(game_rules.ROOMS),
        weapon=random.choice(game_rules.WEAPONS),
    )

    response = requests.get(url, params=accusation.to_dict()).json()

    return flask.render_template(
        'result.html.jinja',
        **accusation.to_dict(),
        valid=response['correct'],
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.run(host='0.0.0.0')
    APP.secret_key == u'yolo'