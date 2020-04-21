from typing import Dict, List, Any, Tuple, Optional
import logging

import requests

from core.game_pieces import Player, Card, CardType, Room, Board
from core.messages import GameStateRequest, GameStateResponse
from core.messages import PlayerMoveRequest, PlayerMoveResponse
from core.messages import PlayerSuggestionRequest, PlayerSuggestionResponse, PlayerSuggestionResult
from core.messages import PlayerAccusationRequest, PlayerAccusationResponse, PlayerAccusationResult

ACK = 'ack'

GAME_STATE_ROUTE = 'api/game_state'
PLAYER_MOVE_ROUTE = 'api/player_move'
SUGGESTION_ROUTE = 'api/suggest'
SUGGESTION_RESULT_ROUTE = 'api/suggest/result'
ACCUSATION_ROUTE = 'api/accuse'
ACCUSATION_ROUTE = 'api/accuse_result'

DEBUG = False  # Using mocky.io endpoints for testing
DEBUG_ACK_ROUTE = '5e9e680f34000099b46eec98'
DEBUG_PLAYER_MOVE_ROUTE = '5e9e684334000037b56eec9a'
DEBUG_SUGGESTION_ROUTE = '5e9e686e34000083b56eec9b'


def _set_up_debug():
    global GAME_STATE_ROUTE
    GAME_STATE_ROUTE = DEBUG_ACK_ROUTE
    global PLAYER_MOVE_ROUTE
    PLAYER_MOVE_ROUTE = DEBUG_PLAYER_MOVE_ROUTE
    global SUGGESTION_ROUTE
    SUGGESTION_ROUTE = DEBUG_SUGGESTION_ROUTE
    global SUGGESTION_RESULT_ROUTE
    SUGGESTION_RESULT_ROUTE = DEBUG_ACK_ROUTE
    global ACCUSATION_ROUTE
    ACCUSATION_ROUTE = DEBUG_SUGGESTION_ROUTE
    global ACCUSATION_RESULT_ROUTE
    ACCUSATION_RESULT_ROUTE = DEBUG_ACK_ROUTE


def _sort_cards(cards: List[Card]) -> Tuple[List[str], List[str], List[str]]:
    # Sort the cards by type, so that we can abstract that for the client
    if not cards:
        return '', '', ''
    suspect_cards = [
        card.name for card in cards if card.type == CardType.CHARACTER]
    weapon_cards = [
        card.name for card in cards if card.type == CardType.WEAPON]
    room_cards = [card.name for card in cards if card.type == CardType.ROOM]
    return suspect_cards, weapon_cards, room_cards


class Client(object):
    """A boundary object that represents the Client connection."""

    def __init__(self, player_name: str,
                 address: str, port: Optional[int] = None,
                 game_id: str = ''):
        self.player_name = player_name
        self.game_id = game_id
        self._address = address
        self._port = port
        self.client_id = ""

    def send_game_state(self, players: List[Player],
                        active_player: Player) -> bool:
        whereabouts = {player.name: player.room.name for player in players}
        current_turn = active_player.name
        request = GameStateRequest(game_id=self.game_id,
                                   player=self.player_name,
                                   whereabouts=whereabouts,
                                   current_turn=current_turn)
        response = self._post_request(
            route=GAME_STATE_ROUTE, request=request)
        return response[ACK]

    def send_move_request(self, valid_moves: List[Room]) -> Optional[Room]:
        request = PlayerMoveRequest(
            game_id=self.game_id,
            player=self.player_name,
            move_options=[room.name for room in valid_moves]
        )
        response = self._post_request(route=PLAYER_MOVE_ROUTE, request=request)
        player_move = PlayerMoveResponse.from_dict(response)
        move_room = next((room for room in valid_moves
                          if room.name == player_move.move), None)
        return move_room

    def send_suggestion_request(self, cards: List[Card]) -> List[Card]:
        suspect_cards, weapon_cards, room_cards = _sort_cards(cards)
        request = PlayerSuggestionRequest(game_id=self.game_id,
                                          player=self.player_name,
                                          suspects=suspect_cards,
                                          weapons=weapon_cards,
                                          rooms=room_cards)
        response = self._post_request(route=SUGGESTION_ROUTE, request=request)
        player_suggestion = PlayerSuggestionResponse.from_dict(response)
        suggestion_cards = [card for card in cards
                            if card.name == player_suggestion.weapon
                            or card.name == player_suggestion.room
                            or card.name == player_suggestion.suspect]
        return suggestion_cards

    def send_suggestion_result(self, suggestion: List[Card],
                               disproved_by: Optional[Player],
                               disproved_card: Optional[Card]):
        suspect_cards, weapon_cards, room_cards = _sort_cards(suggestion)
        request = PlayerSuggestionResult(
            game_id=self.game_id,
            player=self.player_name,
            suspect=next(iter(suspect_cards), ''),
            weapon=next(iter(weapon_cards), ''),
            room=next(iter(room_cards), ''))
        # Suggestion was not disproved
        if not disproved_by or not disproved_card:
            response = self._post_request(
                route=SUGGESTION_RESULT_ROUTE, request=request)
            return response[ACK]

        request = PlayerSuggestionResult(game_id=self.game_id,
                                         player=self.player_name,
                                         disproved_by=disproved_by.name,
                                         disproved_card=disproved_card.name)
        response = self._post_request(route=SUGGESTION_RESULT_ROUTE,
                                      request=request)
        return response[ACK]

    def send_accusation_request(self, cards: List[Card]) -> List[Card]:
        suspect_cards, weapon_cards, room_cards = _sort_cards(cards)
        request = PlayerAccusationRequest(
            game_id=self.game_id,
            player=self.player_name,
            suspects=next(iter(suspect_cards), ''),
            weapons=next(iter(weapon_cards), ''),
            rooms=next(iter(room_cards), ''))
        response = self._post_request(route=ACCUSATION_ROUTE, request=request)
        player_accusation = PlayerAccusationResponse.from_dict(response)
        if not player_accusation:
            return []
        accusation_cards = [card for card in cards
                            if card.name == player_accusation.weapon
                            or card.name == player_accusation.room
                            or card.name == player_accusation.suspect]
        return accusation_cards

    def send_accusation_result(self, correct: bool,
                               murder_deck: List[Card]) -> bool:
        suspect_cards, weapon_cards, room_cards = _sort_cards(murder_deck)
        request = PlayerAccusationResult(game_id=self.game_id,
                                         player=self.player_name,
                                         correct=correct,
                                         suspect=next(iter(suspect_cards)),
                                         weapon=next(iter(weapon_cards)),
                                         room=next(iter(room_cards)))
        response = self._post_request(route=ACCUSATION_RESULT_ROUTE,
                                      request=request)
        return response[ACK]

    def _post_request(self, route, request) -> Dict[str, Any]:
        port = f':{self._port}' if self._port else ''
        url = f'http://{self._address}{port}/{route}'
        # This sends the request to the client and blocks till we get a response
        # TODO(ahammer): Add a timeout here and declare the client disconnected
        # TODO(ahammer): Do literally ANY error handling here
        logging.info('Sending request to %s', url)
        logging.info('Contents: %s', request.to_dict)
        response = requests.get(url, params=request.to_dict())
        logging.info('Response: %s', response.headers)
        return response.json()

