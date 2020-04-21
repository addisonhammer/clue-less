"""Example Client that generates a random accusation and sends it to the server."""
import json
import logging
import os
import random
import socket
import time

import flask
import requests
from flask import request, redirect, url_for

APP = flask.Flask(__name__)

SERVER_IP = os.environ.get('SERVER_IP')
SERVER_PORT = os.environ.get('SERVER_PORT')

@APP.route('/game/<int:game_id>/<int:client_id>', methods=['GET', 'POST'])
def game(game_id, client_id):
    """User is redirected to a game given a game_id and a client_id."""
    return flask.render_template('success.html.jinja')

@APP.route('/', methods=['GET', 'POST'])
def join_game():
    """User joins a game."""

    if request.method == 'POST':
        url = 'http://' + SERVER_IP + ':' + SERVER_PORT + '/api/join_game'
        player_name = request.form.get('name')     
        logging.info('Name: %s', player_name)

        # response = requests.get(url, param=player_name)
        # logging.info('URL Response: %s', response)
        # get client_id and game_id from response
        return redirect(url_for('game', game_id=1, client_id=3))

    return flask.render_template('home.html.jinja')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.run(debug=True, host='0.0.0.0')
    APP.secret_key == u'yolo'