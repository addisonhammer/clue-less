from typing import Dict, List, Any, Tuple
import requests

from core.game import Game, Player, Card, CardType, Room, Board
from core.messages import GameStateRequest, GameStateResponse
from core.messages import PlayerSuggestionRequest, PlayerSuggestionResponse, PlayerSuggestionResult
from core.messages import PlayerAccusationRequest, PlayerAccusationResponse, PlayerAccusationResult
from core.messages import PlayerMoveRequest, PlayerMoveResponse

ACK = 'ack'

GAME_STATE_ROUTE = 'api/game_state'
PLAYER_MOVE_ROUTE = 'api/player_move'
SUGGESTION_ROUTE = 'api/suggest'
ACCUSATION_ROUTE = 'api/accuse'


def sort_cards(cards: List[Card]) -> Tuple(str, str, str):
    # Sort the cards by type, so that we can abstract that for the client
    suspect_cards = [card.name for card in cards if card.type == CardType.PLAYER]
    weapon_cards = [card.name for card in cards if card.type == CardType.WEAPON]
    room_cards = [card.name for card in cards if card.type == CardType.ROOM]
    return suspect_cards, weapon_cards, room_cards

class Client(object):
    """A boundary object that represents the Client connection."""
    def __init__(self, player_name:str, ip_address: str, port: int):
        self.player_name = player_name
        self._ip_address = ip_address
        self._port = port

    def send_game_state(self, game: Game) -> bool:
        whereabouts = {player.name: player.room.name for player in game.players}
        current_turn = game.players[game.turn].name
        request = GameStateRequest(whereabouts=whereabouts, current_turn=current_turn)
        response = self._post_request(route=GAME_STATE_ROUTE, request=request)
        return response[ACK]

    def send_move_request(self, valid_moves: List[Room]) -> Room:
        request = PlayerMoveRequest(move_options=[room.name for room in valid_moves])
        response = self._post_request(route=PLAYER_MOVE_ROUTE, request=request)
        player_move = PlayerMoveResponse.from_dict(response)
        move_selected = [room for room in valid_moves if room.name == player_move.move]
        return move_selected

    def send_suggestion_request(self, cards: List[Card]) -> List[Card]:
        suspect_cards, weapon_cards, room_cards = sort_cards(cards)
        request = PlayerSuggestionRequest(suspects=suspect_cards,
                                          weapons=weapon_cards,
                                          rooms=room_cards)
        response = self._post_request(route=SUGGESTION_ROUTE, request=request)
        player_suggestion = PlayerSuggestionResponse.from_dict(response)
        suggestion = [card for card in cards
                      if card.name == player_suggestion.weapon
                      or card.name == player_suggestion.room
                      or card.name == player_suggestion.suspect]
        return suggestion

    def send_suggestion_result(self, disproved_by: Player, disproved_card: Card):
        request = PlayerSuggestionResult(disproved_by=disproved_by.name,
                                         disproved_card=disproved_card.name)
        response = self._post_request(route=SUGGESTION_ROUTE, request=request)
        return response[ACK]

    def send_accusation_request(self, cards: List[Card]) -> List[Card]:
        suspect_cards, weapon_cards, room_cards = sort_cards(cards)
        request = PlayerAccusationRequest(suspects=suspect_cards,
                                          weapons=weapon_cards,
                                          rooms=room_cards)
        response = self._post_request(route=SUGGESTION_ROUTE, request=request)
        player_accusation = PlayerAccusationResponse.from_dict(response)
        accusation = [card for card in cards
                      if card.name == player_accusation.weapon
                      or card.name == player_accusation.room
                      or card.name == player_accusation.suspect]
        return accusation

        
    def send_accusation_result(self, correct: bool, murder_deck: List[Card]):
        suspect_cards, weapon_cards, room_cards = sort_cards(murder_deck)
        request = PlayerAccusationResult(correct=correct,
                                         suspect=suspect_cards[0],
                                         weapon=weapon_cards[0],
                                         room=room_cards[0])
        response = self._post_request(route=SUGGESTION_ROUTE, request=request)
        return response[ACK]

    def _post_request(self, route, request) -> Dict[str, Any]:
        url = f'http://{self._ip_address}:{self._port}/{route}'
        # This sends the request to the client and blocks till we get a response
        # TODO(ahammer): Add a timeout here and declare the client disconnected
        return requests.get(url, params=request.to_dict()).json()