"""Example Client that generates a random accusation and sends it to the server."""
import json
import logging
import os
import random
import socket
import time

from flask import Flask, request, render_template, jsonify
import requests

from core.messages import PlayerMoveRequest, PlayerMoveResponse
from core.server_boundary import Server

# from core import game_rules
# from core import messages

SERVER_IP = os.environ.get('SERVER_IP')
SERVER_PORT = os.environ.get('SERVER_PORT')


class App(Flask):
    server = Server(SERVER_IP, SERVER_PORT)
    player_name: str = ''
    #  Add more attributes you need to access globally


APP = App(__name__)


@APP.route('/join', methods=['GET'])
def join_game():
    if request.method == 'GET':
        logging.info('GET call, serving HOME template')
        return render_template('home.html.jinja')
    logging.info('Form Results: %s', request.form)
    player_selection = request.form.get('player')
    if player_selection:  # Add more error checking here
        result = APP.server.send_join_request(player_selection)
    return jsonify(result)


@APP.route('/api/player_move', methods=['GET'])
def player_move():
    # Parse PlayerMoveRequest
    _ = PlayerMoveRequest.from_dict(request.args)
    # Store move options in App, and present to user elsewhere
    # block until they choose where to move
    # Build PlayerMoveResponse
    return jsonify(PlayerMoveResponse().to_dict())


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.config.update(PROPAGATE_EXCEPTIONS=True)
    APP.run(debug=True, host='0.0.0.0')
    APP.secret_key == u'yolo'
