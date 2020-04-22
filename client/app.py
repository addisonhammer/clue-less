from enum import Enum
import json
import logging
import os
import time

from flask import Flask, request, render_template, jsonify, redirect, url_for

from core.messages import PlayerMoveRequest, PlayerMoveResponse
from core.server_boundary import Server

from core import game_const
from core import messages

SERVER_IP = os.environ.get('SERVER_IP')
SERVER_PORT = os.environ.get('SERVER_PORT')


class Actions(Enum):
    WAIT = 0  # Client should display default game interface
    MOVE = 1  # Client should display Move Selection page
    SUGGEST = 2  # Client should display Suggestion page
    ACCUSE = 3  # Client should display Accusation Page


class App(Flask):
    server = Server(SERVER_IP, SERVER_PORT)
    # client = Client()
    player_name: str = ''
    character: str = ''
    client_ids = []
    game_ids = []
    characters = []
    suspect_suggest = ''
    weapon_suggest = ''
    room_suggest = ''

    next_action: Actions = Actions.WAIT
    game_state: messages.GameStateRequest = None
    move_request: messages.PlayerMoveRequest = None
    suggest_request: messages.PlayerSuggestionRequest
    suggest_results: messages.PlayerSuggestionResult
    accuse_request: messages.PlayerAccusationRequest
    accuse_results: messages.PlayerAccusationResult
    game_id: str = ''
    client_id: str = ''
    #  Add more attributes you need to access globally


APP = App(__name__)


@APP.route('/debug/app', methods=(['GET']))
def debug_app():
    app_dict = {key: str(value) for key, value in APP.__dict__.items()}
    return jsonify(app_dict)


@APP.route('/join', methods=['GET', 'POST'])
def join_game():
    if request.method == 'POST':
        character_selection = request.form.get('character')
        logging.info('Selected character: %s', character_selection)
        if character_selection:
            join_response = APP.server.send_join_request(character_selection)
            logging.info("Client ID: %s", join_response.client_id)
            APP.characters.append(join_response.player)
            APP.client_ids.append(join_response.client_id)
            APP.client_id = join_response.client_id
        return redirect(url_for('queue', client_id=APP.client_id))

    return render_template('home.html.jinja',
                           characters=list(game_const.CHARACTERS))


@APP.route('/queue/<client_id>', methods=['GET', 'POST'])
def queue(client_id):
    global game_id
    if request.method == 'POST':
        if "start_game" in request.form:
            logging.info('Client %s request to start the game', client_id)
            game_id = APP.server.send_start_game_request()
            if not game_id:
                return 'Please wait while we find an available game server for you.'
            else:
                logging.info("Game ID: %s", game_id)
                APP.game_ids.append(game_id)
                return redirect(url_for('game', game_id=game_id, client_id=client_id))

    return render_template('queue.html.jinja',
                           pending=False)


@APP.route('/game/<game_id>/<client_id>/suggest', methods=['GET', 'POST'])
def game(game_id, client_id):
    logging.info('Game %s has started', game_id)
    global suspect_suggest
    global weapon_suggest
    global room_suggest
    # POST request for suggestion
    if request.method == 'POST':
        form_results = request.form
        logging.info("Sending suggestion request data: %s", form_results)
        suspect_suggest = form_results.get("suspect")
        weapon_suggest = form_results.get("weapon")
        room_suggest = form_results.get("room")
        # i am unable to send form_results to new page because flask so have to make them global
        return redirect(url_for('result', game_id=game_id, client_id=client_id))

    return render_template('suggestion.html.jinja',
                           client_ids=App.client_ids,
                           game_ids=App.game_ids,
                           characters=App.characters,
                           names=list(game_const.CHARACTERS),
                           weapons=list(game_const.WEAPONS),
                           rooms=list(game_const.ROOMS))


@APP.route('/result/<game_id>/<client_id>', methods=['GET', 'POST'])
def result(game_id, client_id):
    logging.info("Suggestion result: %s", "Incorrect")
    # POST request for accusation
    if request.method == 'POST':
        if request.form['button'] == 'Make an Accusation':
            return redirect(url_for('accuse', game_id=game_id, client_id=client_id))
        else:
            return redirect(url_for('move', game_id=game_id, client_id=client_id))

    return render_template('result.html.jinja',
                           suspect=suspect_suggest,
                           weapon=weapon_suggest,
                           room=room_suggest,
                           result=False)


@APP.route('/accuse/<game_id>/<client_id>', methods=['GET', 'POST'])
def accuse(game_id, client_id):
    # POST request for accusation
    if request.method == 'POST':
        form_results = request.form
        logging.info("Sending accusation request data: %s", form_results)
        logging.info("Accusation result: %s", "Incorrect")
        return 'Your accusation was incorrect. Game over.'

    return render_template('accusation.html.jinja',
                           client_ids=App.client_ids,
                           game_ids=App.game_ids,
                           characters=App.characters,
                           names=list(game_const.CHARACTERS),
                           weapons=list(game_const.WEAPONS),
                           rooms=list(game_const.ROOMS))


@APP.route('/move/<game_id>/<client_id>', methods=['GET', 'POST'])
def move(game_id, client_id):
    if request.method == 'POST':
        form_results = request.form
        logging.info("Sending move request data: %s", form_results)
        logging.info("Move result: %s", "Succesful")
        return 'You have successfully moved.'

    return render_template('room.html.jinja',
                           rooms=['Billiard', 'Lounge'])


@APP.route('/api/game_state', methods=['GET'])
def api_game_state():
    logging.info('Received api_game_state Request: %s', request.args)
    game_state = messages.GameStateRequest.from_dict(dict(request.args))
    logging.info('Parsed Request: %s', game_state)
    APP.game_state = game_state
    APP.game_id = game_state.game_id
    APP.next_action = Actions.WAIT
    time.sleep(0.5)
    response = {'ack': True}
    logging.info('Sending Response: %s', response)
    return jsonify(response)


@APP.route('/api/player_move', methods=['GET'])
def api_player_move():
    logging.info('Received api_player_move Request: %s', request.args)
    move_request = messages.PlayerMoveRequest.from_dict(dict(request.args))
    logging.info('Parsed Request: %s', move_request)
    APP.move_request = move_request
    APP.next_action = Actions.MOVE
    time.sleep(0.5)
    response = messages.PlayerMoveResponse(game_id=APP.game_id,
                                           client_id=APP.client_id)

    logging.info('Sending Response: %s', response)
    return jsonify(response.to_dict())


@APP.route('/api/suggest', methods=['GET'])
def api_suggest():
    logging.info('Received api_suggest Request: %s', request.args)
    suggest_request = messages.PlayerSuggestionRequest.from_dict(
        dict(request.args))
    logging.info('Parsed Request: %s', suggest_request)
    APP.suggest_request = suggest_request
    APP.next_action = Actions.SUGGEST
    time.sleep(0.5)
    response = messages.PlayerSuggestionResponse(game_id=APP.game_id,
                                                 client_id=APP.client_id)
    logging.info('Sending Response: %s', response)
    return jsonify(response.to_dict())


@APP.route('/api/suggest_result', methods=['GET'])
def api_suggest_result():
    logging.info('Received api_suggest_result Request: %s', request.args)
    suggest_results = messages.PlayerSuggestionResult.from_dict(
        dict(request.args))
    logging.info('Parsed Request: %s', suggest_results)
    APP.suggest_results = suggest_results
    APP.next_action = Actions.WAIT
    time.sleep(0.5)
    response = {'ack': True}
    logging.info('Sending Response: %s', response)
    return jsonify(response)


@APP.route('/api/accuse', methods=['GET'])
def api_accuse():
    logging.info('Received api_accuse Request: %s', request.args)
    accuse_request = messages.PlayerAccusationRequest.from_dict(
        dict(request.args))
    logging.info('Parsed Request: %s', accuse_request)
    APP.accuse_request = accuse_request
    APP.next_action = Actions.ACCUSE
    time.sleep(0.5)
    response = messages.PlayerAccusationResponse(game_id=APP.game_id,
                                                 client_id=APP.client_id)
    logging.info('Sending Response: %s', response)
    return jsonify(response.to_dict())


@APP.route('/api/accuse_result', methods=['GET'])
def api_accuse_result():
    logging.info('Received api_accuse_result Request: %s', request.args)
    accuse_results = messages.PlayerAccusationResult.from_dict(
        dict(request.args))
    logging.info('Parsed Request: %s', accuse_results)
    APP.accuse_results = accuse_results
    APP.next_action = Actions.WAIT
    time.sleep(0.5)
    response = {'ack': True}
    logging.info('Sending Response: %s', response)
    return jsonify(response)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.config.update(PROPAGATE_EXCEPTIONS=True)
    APP.run(debug=True, host='0.0.0.0')
    APP.secret_key == u'yolo'
