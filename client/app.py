"""Example Client that generates a random accusation and sends it to the server."""
import json
import logging
import os
import random
import socket
import time
import flask

import requests

APP = flask.Flask(__name__)

SERVER_IP = os.environ.get('SERVER_IP')
SERVER_PORT = os.environ.get('SERVER_PORT')

NAMES = (
    'Prof. Plum',
    'Mrs. White',
    'Col. Mustard',
    'Miss Scarlet',
    'Mrs. Peacock',
    'Mr. Green',
)

WEAPONS = (
    'Revolver',
    'Dagger',
    'Lead Pipe',
    'Rope',
    'Candlestick',
    'Wrench',
)

ROOMS = (
    'Study',
    'Hall',
    'Lounge',
    'Library',
    'Billiard Room',
    'Dining Room',
    'Ballroom',
    'Kitchen',
    'Conservatory',
)

@APP.route('/', methods=['GET'])
def handleGet():
    logging.info('GET call, serving GUESS template')
    return flask.render_template('clue.html.jinja')


@APP.route('/', methods=['POST'])
def handlePost():
    url = 'http://' + SERVER_IP + ':' + SERVER_PORT + '/api/test'
    logging.info(url)

    accusation = {
        'username': flask.request.form['username'],
        'name': random.choice(NAMES),
        'room': random.choice(ROOMS),
        'weapon': random.choice(WEAPONS),
    }

    response = requests.get(url, params=accusation).json()

    return flask.render_template(
        'result.html.jinja',
        **accusation,
        valid=response['correct'],
    )


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.run(host='0.0.0.0')
    APP.secret_key == u'yolo'