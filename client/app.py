from enum import Enum
import json
import logging
import os
import random
import time
from typing import List

from flask import Flask, request, render_template, jsonify, redirect, url_for

from core.messages import PlayerMoveRequest, PlayerMoveResponse
from core.server_boundary import Server
from core.client_boundary import Client

from core.game import GameEncoder
from core import game_const
from core import messages

SERVER_IP = os.environ.get('SERVER_IP')
SERVER_PORT = os.environ.get('SERVER_PORT')


class Actions(Enum):
    WAIT = 0  # Client should display default game interface
    MOVE = 1  # Client should display Move Selection page
    SUGGEST = 2  # Client should display Suggestion page
    ACCUSE = 3  # Client should display Accusation Page


class AppData(object):
    server = Server(SERVER_IP, SERVER_PORT)
    next_action: Actions = Actions.WAIT
    game_state: messages.GameStateRequest = None
    move_request: messages.PlayerMoveRequest = None
    suggest_request: messages.PlayerSuggestionRequest
    suggest_results: messages.PlayerSuggestionResult
    accuse_request: messages.PlayerAccusationRequest
    accuse_results: messages.PlayerAccusationResult
    game_id: str = ''
    client_id: str = ''
    seen_cards: List[str] = []
    player_deck: List[str] = []
    character: str = ''
    client_id: str = ''
    ready: bool = False



class App(Flask):
    app_data: AppData = AppData()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_encoder = GameEncoder

    def strategize_options(self, all_weapons: List[str], all_suspects: List[str],
                           all_rooms: List[str]):
        """Automatically reduce options based on our hand and cards we've seen."""
        # logging.info('Player Deck: %s', self.player_deck)
        # logging.info('Seen Cards: %s', self.seen_cards)

        weapons = [weapon for weapon in all_weapons
                   if weapon not in (self.app_data.player_deck + self.app_data.seen_cards)]
        suspects = [suspect for suspect in all_suspects
                    if suspect not in (self.app_data.player_deck + self.app_data.seen_cards)]
        rooms = [room for room in all_rooms
                 if room not in (self.app_data.player_deck + self.app_data.seen_cards)]

        if not weapons:
            weapons = all_weapons
        if not suspects:
            suspects = all_suspects
        if not rooms:
            rooms = all_rooms
        return weapons, suspects, rooms


APP = App(__name__)


@APP.route('/debug/app', methods=(['GET']))
def debug_app():
    app_dict = APP.app_data.__dict__.copy()
    if APP.app_data.seen_cards:
        app_dict.update(seen_cards=APP.app_data.seen_cards)
    return jsonify(app_dict)

@APP.route('/')
def main():
    return render_template('home.html', 
                            characters=list(game_const.CHARACTERS))

@APP.route('/join_game', methods=['POST'])
def join_game():
    # Player selects a character
    APP.app_data.character = request.form.get('character')
    logging.info('Selected character: %s', APP.app_data.character)

    # Player get client id  
    join_response = APP.app_data.server.send_join_request(APP.app_data.character)
    logging.info("Client ID: %s", join_response.client_id)
    APP.app_data.client_id = join_response.client_id

    # Player get game id
    game_response = APP.app_data.server.send_start_game_request()
    logging.info("Game ID: %s", join_response.client_id)
    APP.app_data.game_id = game_response.game_id

    client = Client(APP.app_data.character, SERVER_IP, SERVER_PORT, APP.app_data.game_id)
    game_state = client.send_game_state(list(game_const.CHARACTERS), APP.app_data.character)

    logging.info('Game state: %s', game_state)

    return render_template('home.html',
                           character=APP.app_data.character,
                           ready=APP.app_data.ready)

@APP.route('/game', methods=['POST'])
def start_game():

    # Add logic here to determien true/false for suggestion/accusation
    return render_template('game.html',
                            characters=list(game_const.CHARACTERS),
                            weapons=list(game_const.WEAPONS),
                            rooms=list(game_const.ROOMS_LAYOUT),
                            suggestion=True,
                            accusation=False,
                            move=False)

@APP.route('/api/game_state', methods=['GET'])
def api_game_state():
    logging.info('Received api_game_state Request: %s',
                 request.args)
    game_state = messages.GameStateRequest.from_dict(
        request.args.to_dict(flat=False))
    logging.info('Parsed Request: %s', game_state)
    APP.app_data.game_state = game_state
    APP.app_data.player_deck = game_state.player_cards
    APP.app_data.game_id = game_state.game_id[0]
    APP.next_action = Actions.WAIT
    response = {'ack': True}
    # logging.info('Sending Response: %s', response)
    return jsonify(response)


@APP.route('/api/player_move', methods=['GET'])
def api_player_move():
    # logging.info('Received api_player_move Request: %s', request.args)
    move_request = messages.PlayerMoveRequest.from_dict(
        request.args.to_dict(flat=False))
    logging.info('Parsed Request: %s', move_request)
    APP.move_request = move_request
    APP.next_action = Actions.MOVE
    time.sleep(2)
    move_selection = random.choice(move_request.move_options)
    response = messages.PlayerMoveResponse(game_id=APP.app_data.game_id,
                                           client_id=APP.app_data.client_id,
                                           move=move_selection)

    logging.info('Sending Response: %s', response)
    return jsonify(response.to_dict())


@APP.route('/api/suggest', methods=['GET'])
def api_suggest():
    # logging.info('Received api_suggest Request: %s', request.args)
    suggest_request = messages.PlayerSuggestionRequest.from_dict(
        request.args.to_dict(flat=False))
    logging.info('Parsed Request: %s', suggest_request)
    APP.app_data.suggest_request = suggest_request
    APP.next_action = Actions.SUGGEST
    time.sleep(2)
    weapons, suspects, rooms = APP.strategize_options(suggest_request.weapons,
                                                      suggest_request.suspects,
                                                      suggest_request.rooms)
    logging.info('Weapons: %s, Suspects: %s, Rooms: %s',
                 weapons, suspects, rooms)
    room = random.choice(rooms)
    weapon = random.choice(weapons)
    suspect = random.choice(suspects)
    response = messages.PlayerSuggestionResponse(game_id=APP.app_data.game_id,
                                                 client_id=APP.app_data.client_id,
                                                 room=room,
                                                 suspect=suspect,
                                                 weapon=weapon)
    logging.info('Sending Response: %s', response)
    return jsonify(response.to_dict())


@APP.route('/api/suggest_result', methods=['GET'])
def api_suggest_result():
    # logging.info('Received api_suggest_result Request: %s', request.args)
    suggest_results = messages.PlayerSuggestionResult.from_dict(
        request.args.to_dict(flat=False))
    logging.info('Parsed Request: %s', suggest_results)
    APP.app_data.suggest_results = suggest_results
    logging.info('test')
    if suggest_results.disproved_card[0]:
        APP.app_data.seen_cards.append(suggest_results.disproved_card[0])
    logging.info(APP.app_data.seen_cards)
    APP.next_action = Actions.WAIT
    response = {'ack': True}
    # logging.info('Sending Response: %s', response)
    return jsonify(response)


@APP.route('/api/accuse', methods=['GET'])
def api_accuse():
    # logging.info('Received api_accuse Request: %s', request.args)
    accuse_request = messages.PlayerAccusationRequest.from_dict(
        request.args.to_dict(flat=False))
    logging.info('Parsed Request: %s', accuse_request)
    APP.accuse_request = accuse_request
    APP.next_action = Actions.ACCUSE
    time.sleep(2)
    weapons, suspects, rooms = APP.strategize_options(accuse_request.weapons,
                                                      accuse_request.suspects,
                                                      accuse_request.rooms)
    logging.info('Weapons: %s, Suspects: %s, Rooms: %s',
                 weapons, suspects, rooms)
    # Only select an accusation if we're pretty sure!
    if (
            len(rooms) +
            len(weapons) +
            len(suspects)) <= 4:
        room = random.choice(rooms)
        weapon = random.choice(weapons)
        suspect = random.choice(suspects)
    else:
        room = ''
        weapon = ''
        suspect = ''

    response = messages.PlayerAccusationResponse(game_id=APP.app_data.game_id,
                                                 client_id=APP.app_data.client_id,
                                                 room=room,
                                                 weapon=weapon,
                                                 suspect=suspect)
    logging.info('Sending Response: %s', response)
    return jsonify(response.to_dict())


@APP.route('/api/accuse_result', methods=['GET'])
def api_accuse_result():
    # logging.info('Received api_accuse_result Request: %s', request.args)
    accuse_results = messages.PlayerAccusationResult.from_dict(
        request.args.to_dict(flat=False))
    logging.info('Parsed Request: %s', accuse_results)
    APP.accuse_results = accuse_results
    APP.next_action = Actions.WAIT
    response = {'ack': True}
    # logging.info('Sending Response: %s', response)
    return jsonify(response)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.config.update(PROPAGATE_EXCEPTIONS=True)
    APP.run(debug=True, host='0.0.0.0')
    APP.secret_key == u'yolo'
