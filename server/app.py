from concurrent.futures import Future, ThreadPoolExecutor
import logging
import os
import time
from threading import Lock
from typing import List, Optional
import uuid

from flask import Flask, request, jsonify, render_template
import attr

from core.client_boundary import Client
from core.game import Game, GameEncoder
from core.messages import JoinGameRequest, JoinGameResponse
from core.messages import StartGameRequest, StartGameResponse
from core.messages import PlayerCountRequest, PlayerCountResponse

CLIENT_PORT = 5000

MIN_PLAYERS = 3
MAX_PLAYERS = 6


class App(Flask):
    hostID: str = str(uuid.uuid4())
    clients: List[Client] = []
    games: List[Game] = []
    futures: List[Future] = []
    executor: ThreadPoolExecutor = ThreadPoolExecutor(max_workers=5)
    lock: Lock = Lock()
    paused: bool = False
    kill: bool = False

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.json_encoder = GameEncoder

    @property
    def waiting_clients(self) -> List[Client]:
        return [client for client in self.clients
                if not client.game_id]

    def get_client(self, client_id: str) -> Optional[Client]:
        return next((client for client in self.clients
                     if client.client_id == client_id), None)

    def get_client_by_ip(self, ip: str) -> Optional[Client]:
        return next((client for client in self.clients
                     if client.address == ip), None)

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
            time.sleep(1)  # Give other threads a chance
            with self.lock:
                game.take_turn()
                game_result = game.result
            if self.kill == True:
                return self, game.game_id
        return self, game.game_id


def end_game(future: Future):
    app, game_id = future.result()
    logging.info('Game Over: %s Wins!', app.get_game(game_id).result)
    # for client in clients:
    #     app.remove_client(client.client_id)
    # app.remove_game(game_id)


APP = App(__name__)


@APP.route('/')
def index():
    return f'This is the Server, hostID={APP.hostID}'


@APP.route('/debug/clients')
def debug_clients():
    return jsonify(APP.clients)


@APP.route('/debug/games')
def debug_games():
    return jsonify(APP.games)


@APP.route('/debug/pause', methods=['POST', 'GET'])
def debug_pause():
    if request.method == 'POST':
        logging.info(request.form)
        if request.form.get('pause'):
            APP.paused = True
            APP.lock.acquire()
        if request.form.get('resume'):
            APP.paused = False
            APP.lock.release()
        if request.form.get('kill'):
            APP.kill = True
            if APP.lock.locked():
                APP.lock.release()
            APP.paused = False
            APP.kill = False
    return render_template('pause.html.jinja', paused=APP.paused)


@APP.route('/debug/clear')
def debug_clear():
    return 'NotImplemented'


@APP.route('/api/join_game', methods=['GET'])
def join():
    # parse input params
    # logging.info('Received join request: %s', request.args)
    join_request = JoinGameRequest.from_dict(dict(request.args))
    logging.info('Parsed Request: %s', join_request)
    src_ip = request.remote_addr
    existing = APP.get_client_by_ip(src_ip)

    if existing:
        logging.info('Client already exists for this IP. ')
        response = JoinGameResponse(client_id=existing.client_id,
                                    player=existing.player_name)
        return jsonify(response.to_dict())

    player = join_request.player
    # TODO(ahammer): Check this character against existing client's characters
    new_client = Client(player, src_ip, CLIENT_PORT)
    APP.clients.append(new_client)
    logging.info('Added a new client: %s', new_client.__dict__)

    response = JoinGameResponse(player=player,
                                client_id=new_client.client_id)
    logging.info('Response to client: %s', response)
    return jsonify(response.to_dict())


@APP.route('/api/request_game', methods=['GET'])
def request_game():
    start_request = StartGameRequest.from_dict(dict(request.args))

    player_count = len(APP.waiting_clients)
    if player_count < MIN_PLAYERS:
        response = StartGameResponse(client_id=start_request.client_id,
                                     game_id='')
        return jsonify(response.to_dict())

    if player_count > MAX_PLAYERS:
        game_clients = APP.waiting_clients[:MAX_PLAYERS - 2]
        game_clients.append(APP.get_client(start_request.client_id))
    else:
        game_clients = APP.waiting_clients
    game = Game(game_clients)
    APP.games.append(game)
    APP.start_game(game.game_id)

    response = StartGameResponse(client_id=start_request.client_id,
                                 game_id=game.game_id)
    return jsonify(response.to_dict())


@APP.route('/api/start_game', methods=['GET'])
def start_game():
    return 'NotImplemented'


@APP.route('/api/player_count', methods=['GET'])
def player_count():
    # logging.info('Received player_count request: %s', request.args)
    player_count_request = PlayerCountRequest.from_dict(dict(request.args))
    logging.info('Parsed request: %s', player_count_request)
    response = PlayerCountResponse(client_id=player_count_request.client_id,
                                   count=len(APP.waiting_clients))
    return jsonify(response.to_dict())


# Define all @APP.routes above this line.
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    APP.config['PROPAGATE_EXCEPTIONS'] = True
    APP.secret_key == u'yolo'
    APP.run(debug=True, host='0.0.0.0')
