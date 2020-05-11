from enum import Enum
import json
import logging
import os
import random
import time
from typing import List, Dict

from flask import Flask, request, render_template, jsonify, redirect, url_for

from core.messages import PlayerMoveRequest, PlayerMoveResponse
from core.server_boundary import Server
from core.messages import GameStateRequest, ClientGameStateRequest

from core.game import GameEncoder
from core import game_const
from core import messages
from time import sleep

SERVER_IP = os.environ.get('SERVER_IP')
SERVER_PORT = os.environ.get('SERVER_PORT')

DEBUG = False


class Actions(Enum):
    WAIT = 0  # Client should display default game interface
    MOVE = 1  # Client should display Move Selection page
    SUGGEST = 2  # Client should display Suggestion page
    ACCUSE = 3  # Client should display Accusation Page


class AppData(object):
    server = Server(SERVER_IP, SERVER_PORT)
    next_action: Actions = Actions.WAIT
    game_state: messages.GameStateRequest = GameStateRequest(
        None, None, None, None, None)
    move_request: messages.PlayerMoveRequest = None
    move_response: messages.PlayerMoveResponse = None
    suggest_request: messages.PlayerSuggestionRequest
    suggest_response: messages.PlayerSuggestionResponse = None
    suggest_results: messages.PlayerSuggestionResult
    accuse_request: messages.PlayerAccusationRequest
    accuse_response: messages.PlayerAccusationResponse = None
    accuse_results: messages.PlayerAccusationResult
    game_id: str = ''
    client_id: str = ''
    seen_cards: List[str] = []
    player_deck: List[str] = []
    character: str = ''
    whereabouts: Dict[str,str] = []
    current_turn: str = ''
    suggestion: bool = True
    continue_game: bool = False


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
    join_response = APP.app_data.server.send_join_request(
        APP.app_data.character)
    logging.info("Client ID: %s", join_response.client_id)
    APP.app_data.client_id = join_response.client_id

    # Player get game id
    game_response = APP.app_data.server.send_start_game_request()
    logging.info("Game ID: %s", game_response.client_id)
    APP.app_data.game_id = game_response.game_id

    if not APP.app_data.game_id:
        sleep(15)

    # Player request game state
    game_state_response = APP.app_data.server.get_game_state()
    logging.info("Game State: %s", game_state_response.game_id)

    return redirect(url_for('game', game_id=game_state_response.game_id))


@APP.route('/game/<game_id>', methods=['GET', 'POST'])
def game(game_id):
    APP.app_data.game_state = APP.app_data.server.get_game_state()
    APP.app_data.current_turn = APP.app_data.game_state.current_turn
    # App.app_data.game_state.whereabouts = {
    #     game_const.PLUM : (game_const.STUDY, game_const.LIBRARY),
    #     game_const.WHITE : (game_const.STUDY, game_const.LIBRARY),
    #     game_const.MUSTARD : game_const.BILLIARD,
    #     game_const.SCARLET : (game_const.LOUNGE, game_const.DINING),
    #     game_const.PEACOCK : game_const.KITCHEN,
    #     game_const.GREEN : game_const.BILLIARD
    # }

    # App.app_data.game_state.player_cards = {
    #     game_const.GREEN, game_const.BILLIARD, game_const.CANDLESTICK
    # }

    return render_template('game.html',
                           game_const=game_const,
                           characters=list(game_const.CHARACTERS),
                           weapons=list(game_const.WEAPONS),
                           rooms=list(game_const.ROOMS),
                           room_layout=list(game_const.ROOMS_LAYOUT),
                           suggestion=APP.app_data.suggestion,
                           character=APP.app_data.character,
                           game_state=APP.app_data.game_state,
                           turn=APP.app_data.current_turn,
                           continue_game=APP.app_data.continue_game)


@APP.route('/submit', methods=['POST'])
def accuse():

    # Player suggests character/weapon/room
    suspect = request.form.get('character')
    weapon = request.form.get('weapon')
    room = request.form.get('room')

    if request.form['submit'] == "Make a Suggestion":
        APP.app_data.suggest_request = messages.PlayerSuggestionRequest(
            APP.app_data.game_id,
            APP.app_data.client_id,
            suspect,
            weapon,
            room
        )

        # Once player made a suggestion, continue_game becomes True to display their next move
        # They can either make an accusation or make a move
        APP.app_data.suggestion = False
        APP.app_data.continue_game = True

    elif request.form['submit'] == "Make an Accusation":

        APP.app_data.suggest_request = messages.PlayerAccusationRequest(
            APP.app_data.game_id,
            APP.app_data.client_id,
            suspect,
            weapon,
            room
        )

        APP.app_data.continue_game = False
        APP.app_data.suggestion = True

    elif request.form['submit'] == "Make a Move":

        # TODO: Graeme to add move logic here

        APP.app_data.continue_game = False
        APP.app_data.suggestion = True

    return redirect(url_for('game', game_id=APP.app_data.game_id))


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


@APP.route('/api/suggest', methods=['GET'])
def api_suggest():
    logging.info('Received api_suggest Request: %s', request.args)
    suggest_request = messages.PlayerSuggestionRequest.from_dict(
        request.args.to_dict(flat=False))
    logging.info('Parsed Request: %s', suggest_request)
    APP.app_data.suggest_request = suggest_request
    APP.next_action = Actions.SUGGEST

    if DEBUG:
        time.sleep(2)
        weapons, suspects, rooms = APP.strategize_options(suggest_request.weapons,
                                                          suggest_request.suspects,
                                                          suggest_request.rooms)
        logging.info('Weapons: %s, Suspects: %s, Rooms: %s',
                     weapons, suspects, rooms)

        response = messages.PlayerSuggestionResponse(game_id=APP.app_data.game_id,
                                                     client_id=APP.app_data.client_id,
                                                     room=APP.app_data.suggest_request.rooms,
                                                     suspect=APP.app_data.suggest_request.suspects,
                                                     weapon=APP.app_data.suggest_request.weapons)
        logging.info('Sending Automated DEBUG Response: %s', response)
        return jsonify(response.to_dict())

    while not APP.app_data.suggest_response:
        time.sleep(1)
    response = APP.app_data.suggest_response
    APP.app_data.suggest_response = None
    logging.info('Sending Player Response: %s', response)
    return jsonify(response.to_dict())


@APP.route('/api/player_move', methods=['GET'])
def api_player_move():
    # logging.info('Received api_player_move Request: %s', request.args)
    move_request = messages.PlayerMoveRequest.from_dict(
        request.args.to_dict(flat=False))
    logging.info('Parsed Request: %s', move_request)
    # APP.move_request = move_request
    APP.next_action = Actions.MOVE

    if DEBUG:
        time.sleep(1)
        move_selection = random.choice(move_request.move_options)
        response = messages.PlayerMoveResponse(game_id=APP.app_data.game_id,
                                               client_id=APP.app_data.client_id,
                                               move=move_selection)

        logging.info('Sending Automated DEBUG Response: %s', response)
        return jsonify(response.to_dict())

    while not APP.app_data.move_response:
        time.sleep(1)
    response = APP.app_data.move_response
    APP.app_data.move_response = None
    logging.info('Sending Player Response: %s', response)
    return jsonify(response.to_dict())


@APP.route('/api/suggest_result', methods=['GET'])
def api_suggest_result():
    # logging.info('Received api_suggest_result Request: %s', request.args)
    suggest_results = messages.PlayerSuggestionResult.from_dict(
        request.args.to_dict(flat=False))
    logging.info('Parsing suggest results: %s', suggest_results)
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

    if DEBUG:
        time.sleep(2)
        weapons, suspects, rooms = APP.strategize_options(accuse_request.weapons,
                                                          accuse_request.suspects,
                                                          accuse_request.rooms)
        logging.info('Weapons: %s, Suspects: %s, Rooms: %s',
                     weapons, suspects, rooms)

        response = messages.PlayerAccusationResponse(game_id=APP.app_data.game_id,
                                                     client_id=APP.app_data.client_id,
                                                     room=APP.app_data.suggest_request.rooms,
                                                     suspect=APP.app_data.suggest_request.suspects,
                                                     weapon=APP.app_data.suggest_request.weapons)
        logging.info('Sending Automated DEBUG Response: %s', response)
        return jsonify(response.to_dict())

    while not APP.app_data.accuse_response:
        time.sleep(1)
    response = APP.app_data.accuse_response
    APP.app_data.accuse_response = None
    logging.info('Sending Player Response: %s', response)
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


@APP.template_filter('card_url')
def card_url(card_text):
    if card_text == game_const.DAGGER:
        return "https://i.imgur.com/GfXbfdU.jpg"
    elif card_text == game_const.WRENCH:
        return "https://i.imgur.com/1QPD85h.jpg"
    elif card_text == game_const.ROPE:
        return "https://i.imgur.com/C6leiZm.jpg"
    elif card_text == game_const.CANDLESTICK:
        return "https://i.imgur.com/FG7mF6M.jpg"
    elif card_text == game_const.PIPE:
        return "https://i.imgur.com/kS8LUEu.jpg"
    elif card_text == game_const.REVOLVER:
        return "https://i.imgur.com/bpcjdJc.jpg"
    elif card_text == game_const.PLUM:
        return "https://i.imgur.com/7lYwXpc.jpg?1"
    elif card_text == game_const.WHITE:
        return "https://i.imgur.com/arLVu0u.jpg?1"
    elif card_text == game_const.MUSTARD:
        return "https://i.imgur.com/j1FRYp4.jpg?1"
    elif card_text == game_const.SCARLET:
        return "https://i.imgur.com/SQFXJFk.jpg?1"
    elif card_text == game_const.PEACOCK:
        return "https://i.imgur.com/pN7b6nq.jpg?1"
    elif card_text == game_const.GREEN:
        return "https://i.imgur.com/tqtnJIn.jpg?1"
    elif card_text == game_const.STUDY:
        return "https://i.imgur.com/u8clJQw.jpg?1"
    elif card_text == game_const.HALL:
        return "https://i.imgur.com/gcJOSk4.jpg?1"
    elif card_text == game_const.LOUNGE:
        return "https://i.imgur.com/mNQrQAw.jpg?1"
    elif card_text == game_const.LIBRARY:
        return "https://i.imgur.com/dPgtAXN.jpg?1"
    elif card_text == game_const.BILLIARD:
        return "https://i.imgur.com/0RnL0uu.jpg?1"
    elif card_text == game_const.DINING:
        return "https://i.imgur.com/aPne9NX.jpg?1"
    elif card_text == game_const.BALLROOM:
        return "https://i.imgur.com/pRU9OYP.jpg?1"
    elif card_text == game_const.KITCHEN:
        return "https://i.imgur.com/6wclCaG.jpg?1"
    elif card_text == game_const.CONSERVATORY:
        return "https://i.imgur.com/Gbq9kuk.jpg?1"
    else:
        return ""


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.config.update(PROPAGATE_EXCEPTIONS=True)
    APP.run(debug=True, host='0.0.0.0')
    APP.secret_key == u'yolo'
