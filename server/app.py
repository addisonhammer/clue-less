import json
import logging
import os
import random
import socket
import time

import flask

APP = flask.Flask(__name__)

SERVER_PORT = int(os.environ.get('SERVER_PORT'))

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', SERVER_PORT))
s.listen(5)

@APP.route('/')
def index():
    clue_url = flask.url_for('clue_server')
    return f'This is the index, try <a href="{clue_url}">Clue</a> instead'

# This page loads indefinitely until a message is received from a client with an accusation
@APP.route('/clue_server')
def clue_server():
    address = ''
    while not address: 
        c, address = s.accept()
        time.sleep(0.1)
    accusation = json.loads(c.recv(1024).decode('utf-8'))
    accusation['username'] = accusation['username'] + f'@{address[0]}' 
    c.close()
    return flask.render_template('clue.html.jinja', whodoneit=True, **accusation)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.run(host='0.0.0.0')
    APP.secret_key == u'yolo'