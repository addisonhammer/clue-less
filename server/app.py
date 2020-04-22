from concurrent.futures import Future, ThreadPoolExecutor
import logging
import os
import time
from typing import List
import uuid

from flask import Flask, request, jsonify

from core.client_boundary import Client
from core.game import Game
from core.messages import JoinGameRequest, JoinGameResponse
from core.messages import StartGameRequest, StartGameResponse
from core.messages import PlayerCountRequest, PlayerCountResponse


CLIENT_PORT = os.environ.get('CLIENT_PORT')

MIN_PLAYERS = 3
MAX_PLAYERS = 6

DEBUG = False


class App(Flask):
    hostID: str = str(uuid.uuid4())
    clients: List[Client] = []
    games: List[Game] = []
    futures: List[Future] = []
    executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=5)

    @property
    def waiting_clients(self) -> List[Client]:
        return [client for client in self.clients
                if not client.game_id]

    def get_game(self, game_id: str) -> Game:
        return next((game for game in self.games
                     if game.game_id == game_id), None)

    def get_game_clients(self, game_id: str) -> List[Client]:
        return [client for client in self.clients
                if client.game_id == game_id]

    def start_game(self, game_id: str) -> bool:
        game = self.get_game(game_id)
        if not game:
            return False
        game_thread = self.executor.submit(self.run_game, game)
        game_thread.add_done_callback(end_game)
        self.futures.append(game_thread)
        return True

    def run_game(self, game: Game) -> str:
        game_result = ''
        # Wait a second for startup
        time.sleep(1)
        while not game_result:
            game.take_turn()
            game_result = game.result
            time.sleep(0.1)  # Give other threads a chance
        return self, game.game_id


def end_game(future: Future):
    app, game_id = future.result()
    winner = app.get_game(game_id).result
    clients = app.get_game_clients(game_id)
    for client in clients:
        client.end_game_request(winner)
        app.remove_client(client.client_id)
    app.remove_game(game_id)


APP = App(__name__)


@APP.route('/')
def index():
    return f'This is the Server, hostID={APP.hostID}'


@APP.route('/debug/clients')
def debug_clients():
    return jsonify([client.__dict__ for client in APP.clients])


@APP.route('/debug/games')
def debug_games():
    return jsonify([game.__dict__ for game in APP.games])


@APP.route('/debug/clear')
def debug_clear():
    return 'NotImplemented'


@APP.route('/api/join_game', methods=['GET'])
def join():
    # parse input params
    join_request = JoinGameRequest.from_dict(request.args)
    src_ip = request.remote_addr
    existing = [client for client in APP.clients
                if client.address == src_ip]

    if existing and not DEBUG:
        return jsonify(JoinGameResponse(existing[0].client_id, player='').to_dict())

    player = join_request.player
    new_client = Client(player,
                        src_ip,
                        CLIENT_PORT)
    APP.clients.append(new_client)

    # get player count without a running game
    player_count = len(APP.waiting_clients)
    return jsonify(
        JoinGameResponse(player=player,
                         client_id=new_client.client_id).to_dict())


@APP.route('/api/start_game', methods=['GET'])
def start_game():
    start_request = StartGameRequest.from_dict(request.args)

    player_count = len(APP.waiting_clients)
    if player_count < MIN_PLAYERS:
        response = StartGameResponse(game_id='')
        return jsonify(response.to_dict())

    if player_count > MAX_PLAYERS:
        game_clients = APP.waiting_clients[:MAX_PLAYERS-1]

    game_clients = APP.waiting_clients
    game = Game(game_clients)
    APP.games.append(game)
    result = APP.start_game(game.game_id)

    response = StartGameResponse(game_id=game.game_id)
    return jsonify(response.to_dict())


@APP.route('/api/player_count', methods=['GET'])
def player_count():
    player_count_request = PlayerCountRequest.from_dict(request.args)
    return PlayerCountResponse(count=len(APP.waiting_clients))


# Define all @APP.routes above this line.


def main():
    APP.config['PROPAGATE_EXCEPTIONS'] = True
    APP.secret_key == u'yolo'
    APP.run(host='0.0.0.0')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
