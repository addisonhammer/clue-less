"""Example Client that generates a random accusation and sends it to the server."""
import json
import logging
import os
import random
import socket
import time

import flask
APP = flask.Flask(__name__)

SERVER_IP = os.environ.get('SERVER_IP')
SERVER_PORT = int(os.environ.get('SERVER_PORT'))

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

@APP.route('/')
def index():
    clue_url = flask.url_for('clue')
    return f'This is the index, try <a href="{clue_url}">Clue</a> instead'

# This one handles HTTP POST and GET methods, so we can capture the form submit
@APP.route('/clue', methods=['POST', 'GET'])
def clue():
    if flask.request.method == 'POST':
        logging.info('POST call, sending random accusation to server...')
        accusation = {
            'username': flask.request.form['username'],
            'name': random.choice(NAMES),
            'room': random.choice(ROOMS),
            'weapon': random.choice(WEAPONS),
        }
        logging.info('Sending accusation to %s:%s...\n%s', SERVER_IP, SERVER_PORT, accusation)
        s = socket.socket()
        s.connect((SERVER_IP, SERVER_PORT))
        s.send(json.dumps(accusation).encode('utf-8')) 
        s.close()       
        return flask.render_template(
            'clue.html.jinja',
            whodoneit=True,
            **accusation,
        )
    else:
        logging.info('GET call, serving GUESS template')
        return flask.render_template('clue.html.jinja', whodoneit=False)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.run(host='0.0.0.0')
    APP.secret_key == u'yolo'