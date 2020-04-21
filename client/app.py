"""Example Client that generates a random accusation and sends it to the server."""
import json
import logging
import os
import random
import socket
import time

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
    return flask.render_template('clue.html.jinja',
                                 names=game_rules.NAMES,
                                 rooms=game_rules.ROOMS,
                                 weapons=game_rules.WEAPONS)


# @APP.route('/', methods=['POST'])
# def handlePost():
#     url = 'http://' + SERVER_IP + ':' + SERVER_PORT + '/api/test'
#     logging.info(url)
#     form_results = flask.request.form
#     logging.info('Form Results: %s', form_results)

#     accusation = messages.PlayerAccusation(
#         message_id=messages.generate_message_id(),
#         player=form_results.get('player'),
#         suspect=form_results.get('suspect'),
#         weapon=form_results.get('weapon'),
#         room=form_results.get('room'),
#     )

#     response = requests.get(url, params=accusation.to_dict()).json()

#     return flask.render_template(
#         'result.html.jinja',
#         **accusation.to_dict(),
#         valid=response['correct'],
#     )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.run(host='0.0.0.0')
    APP.secret_key == u'yolo'