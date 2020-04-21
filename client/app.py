import json
import logging
import os

from flask import Flask, request, render_template, jsonify, redirect, url_for

from core.messages import PlayerMoveRequest, PlayerMoveResponse
from core.server_boundary import Server

from core import game_const

SERVER_IP = os.environ.get('SERVER_IP')
SERVER_PORT = os.environ.get('SERVER_PORT')


class App(Flask):
    server = Server(SERVER_IP, SERVER_PORT)
    player_name: str = ''
    #  Add more attributes you need to access globally


APP = App(__name__)


@APP.route('/join', methods=['GET', 'POST'])
def join_game():
    if request.method == 'POST':
        character_selection = request.form.get('character')
        logging.info('Selected character: %s', character_selection)
        if character_selection:
            result = APP.server.send_join_request(character_selection)
            logging.info(result)
            # result does not return client_id
        return redirect(url_for('queue', client_id=3))

    return render_template('home.html.jinja',
                           characters=list(game_const.CHARACTERS))


@APP.route('/queue/<int:client_id>', methods=['GET', 'POST'])
def queue(client_id):
    if request.method == 'POST':
        if "start_game" in request.form:
            logging.info('Client %s request to start the game', client_id)
            # result = APP.server.send_start_game_request()
            # logging.info(result)
            # TypeError: send_start_game_request() missing 1 required positional argument: 'game_id'
        return redirect(url_for('game', client_id=3, game_id=3))

    return render_template('queue.html.jinja')


@APP.route('/game/<int:game_id>/<int:client_id>', methods=['GET', 'POST'])
def game(client_id, game_id):
    return render_template('clue.html.jinja')


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
    # APP.config.update(PROPAGATE_EXCEPTIONS=True)
    APP.run(debug=True, host='0.0.0.0')
    APP.secret_key == u'yolo'
