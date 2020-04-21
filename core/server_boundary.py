from typing import Dict, List, Any, Tuple, Optional
import logging

import requests

from core.game_pieces import Player, Card, CardType, Room, Board
from core.messages import JoinGameRequest, JoinGameResponse
from core.messages import StartGameRequest, StartGameResponse
from core.messages import PlayerCountRequest, PlayerCountResponse
from core.messages import PlayerCountUpdateRequest, PlayerCountUpdateResponse

JOIN_GAME_ROUTE = 'api/join_game'
START_GAME_ROUTE = 'api/start_game'
PLAYER_COUNT_REQUEST_ROUTE = 'api/player_count'
PLAYER_COUNT_UPDATE_ROUTE = 'join'


class Server(object):
    """A boundary object that represents the Server connection."""

    def __init__(self, address: str, port: Optional[int] = None):
        self._address = address
        self._port = port
        self.client_id = ''

    def send_join_request(self, player_name):
        request = JoinGameRequest(player=player_name)
        response = self._post_request(route=JOIN_GAME_ROUTE, request=request)
        join_response = JoinGameResponse.from_dict(response)
        self.client_id = join_response.client_id
        return join_response.accepted

    def send_start_game_request(self, game_id: str):
        request = StartGameRequest(
            client_id=self.client_id, game_id=game_id)
        response = self._post_request(route=START_GAME_ROUTE, request=request)
        start_response = StartGameResponse.from_dict(response)
        return start_response.accepted

    def send_player_count_request(self):
        request = PlayerCountRequest(self.client_id)
        response = self._post_request(
            route=PLAYER_COUNT_REQUEST_ROUTE, request=request)
        count_response = PlayerCountResponse.from_dict(response)
        return count_response.count

    def send_player_count_update(self, count):
        # this is for sending a player count update to the client
        request = PlayerCountUpdateRequest(self.client_id, count=count)
        response = self._post_request(
            route=PLAYER_COUNT_UPDATE_ROUTE, request=request)
        count_response = PlayerCountUpdateResponse.from_dict(response)
        return count_response.accepted

    def _post_request(self, route, request) -> Dict[str, Any]:
        port = f':{self._port}' if self._port else ''
        url = f'http://{self._address}{port}/{route}'
        # This sends the request to the client and blocks till we get a response
        # TODO(ahammer): Add a timeout here and declare the client disconnected
        # TODO(ahammer): Do literally ANY error handling here
        logging.info('Sending request to %s', url)
        logging.info('Contents: %s', request.to_dict())
        response = requests.get(url, params=request.to_dict())
        logging.info('Response: %s', response.headers)
        return response.json()
