from typing import List, Tuple, Dict, Optional
from enum import Enum
import random
import logging
import uuid

import networkx as nx

from core.client_boundary import Client
from core import game_const
from core.game_pieces import CardType, Card, RoomType, Room, Board, Player

# Module-level helper functions


def format_hallway_name(hallway: Tuple[str, str]) -> str:
    return f'{hallway[0]} - {hallway[1]} Hallway'


class Game(object):
    """Class representing the game instance."""

    def __init__(self, clients: List[Client]):
        """Initialize the Game, given a list of clients"""
        self.game_id = str(uuid.uuid4())
        self.clients = clients
        # Attaches the clients to the Game (for upstream client management)
        for client in self.clients:
            client.game_id = self.game_id

        # First initialize the board, and the contained Room instances
        self.board = self._init_board()

        # Next initialize the list of players, and their start_room
        self.players = self._init_players(
            [client.player_name for client in clients])

        # Now deal the cards to the murder_deck, and to each player
        self.murder_deck = []
        self.cards = []
        self._deal_cards()

        self.turn = 0
        self.result = ''

    @property
    def active_player(self) -> Player:
        # Modulo the turn index so the active player auto-loops
        return self.players[self.turn % len(self.players)]

    def get_player(self, player_name: str) -> Player:
        return next((player for player in self.players
                     if player.name == player_name), None)

    @property
    def active_client(self) -> Client:
        return self.get_client(self.active_player.name)

    def get_client(self, player_name: str) -> Client:
        return next((client for client in self.clients
                     if client.player_name == player_name), None)

    def get_card(self, card_name: str) -> Card:
        return next((card for card in self.cards
                     if card.name == card_name), None)

    def take_turn(self) -> str:
        if self.active_player.playing:
            # First send out a game update to all players
            self._broadcast_game_status()
            # Next start the MOVE phase of the turn
            self._player_move()
            # Next start the SUGGEST phased of the turn
            self._player_suggest()
            # Finally offer an opportunity to ACCUSE
            self._player_accuse()
        # Finally, increment turn
        self.turn += 1

    def _broadcast_game_status(self) -> None:
        for client in self.clients:
            logging.info('Sending Game Status update to %s',
                         client.player_name)
            client.send_game_state(self.players, self.active_player)

    def _broadcast_suggestion_results(self, suggestion: List[Card] = [],
                                      disproved_by: Optional[Player] = None,
                                      disproved_card: Optional[Card] = None
                                      ) -> None:
        for client in self.clients:
            client.send_suggestion_result(suggestion,
                                          disproved_by, disproved_card)

    def _broadcast_accusation_results(self, accusation: List[Card],
                                      correct: bool, ) -> None:
        for client in self.clients:
            client.send_accusation_result(accusation, correct)

    def _player_move(self) -> None:
        current_room = self.active_player.room
        adjacent_rooms = self.board.get_adj_rooms(current_room)
        valid_rooms = [
            room for room in adjacent_rooms
            if self._is_valid_move(room)] + [current_room]

        new_room = self.active_client.send_move_request(valid_rooms)
        if new_room:
            self.active_player.room = new_room
        # TODO(ahammer): Should probably handle 'null room' as an error

    def _is_valid_move(self, room: Room) -> bool:
        if room.type == RoomType.HALLWAY and self._is_room_occupied(room):
            return False
        return True

    def _is_room_occupied(self, room: Room) -> bool:
        return any(player.room.name == room.name
                   for player in self.players)

    def _player_suggest(self) -> None:
        # You can only suggest based on the room you are in
        room_card = self.get_card(self.active_player.room.name)
        if not room_card:
            self._broadcast_suggestion_results()
            return

        # Request a suggestion, given valid options
        valid_cards = [card for card in self.cards
                       if card.type != CardType.ROOM] + [room_card]
        suggestion = self.active_client.send_suggestion_request(valid_cards)

        # If they didn't want to make a suggestion, exit
        if not suggestion:
            self._broadcast_suggestion_results()
            return

        # Move the suspect (if they're playing) to the accuser's room
        suspect_card = next((card for card in suggestion
                             if card.type == CardType.CHARACTER))
        suspect_player = self.get_player(suspect_card.name)
        if suspect_player:
            suspect_player.room = self.active_player.room

        # Loop through the players **IN ORDER** to see who can disprove the suggestion
        for turn in range(self.turn + 1, self.turn + len(self.players)):
            player_to_ask = self.players[turn % len(self.players)]
            for card in suggestion:
                if card.name in player_to_ask.cards:
                    self._broadcast_suggestion_results(
                        suggestion, player_to_ask, card)
                    return

        # If no one was able to disprove the suggestion, broadcast that
        self._broadcast_suggestion_results(suggestion, None, None)

    def _player_accuse(self):
        # TODO(ahammer): Remove the player's hand from the list of cards to accuse with
        accusation = self.active_client.send_accusation_request(self.cards)
        if all(card in self.murder_deck for card in accusation):
            self._broadcast_accusation_results(True, accusation)
            self.results = self.active_player.name
            return
        self._broadcast_accusation_results(False, accusation)
        self.active_player.playing = False

    def _deal_cards(self):
        """Deals out the cards in the deck to start the game.

        Side-Effects:
          - Assigns a List[Card] to the Game.murder_deck attribute
          - Loops through Game.players and appends Card instances to the Player.card attribute
        """

        # First Initialize the cards from constants)
        weapons = [Card(name, CardType.WEAPON) for name in game_const.WEAPONS]
        characters = [Card(name, CardType.CHARACTER)
                      for name in game_const.CHARACTERS]
        rooms = [Card(name, CardType.ROOM) for name in game_const.ROOMS]

        # Shuffle each deck, and pop a random card for the murder deck
        random.shuffle(weapons)
        random.shuffle(characters)
        random.shuffle(rooms)
        self.cards = weapons + characters + rooms
        self.murder_deck = [weapons.pop(), characters.pop(), rooms.pop()]

        # Put the remaining cards in a deck, shuffle, and deal to players
        remaining_cards = weapons + characters + rooms
        random.shuffle(remaining_cards)
        while len(remaining_cards) > 0:
            for player in self.players:
                player.cards.append(remaining_cards.pop())

    def _init_board(self):
        """Initializes the Rooms and the Game Board."""
        # First build up a list of Room instances based on constants
        rooms = []
        rooms.extend([Room(name=room, type=RoomType.REGULAR)
                      for room in game_const.ROOMS])
        rooms.extend(
            [Room(name=format_hallway_name(hallway), type=RoomType.HALLWAY)
             for hallway in game_const.HALLWAYS])

        # Then use the static adjacency graph to generate a Board and return it
        board = Board(rooms=rooms)
        for room in game_const.ROOMS:
            board.add_node(room)
        for hallway in game_const.HALLWAYS:
            board.add_node(format_hallway_name(hallway))
            for adjacent_room in hallway:
                board.add_edge(adjacent_room, format_hallway_name(hallway))
        for secret_passage in game_const.SECRET_PASSAGES:
            board.add_edge(*secret_passage)
        return board

    def _init_players(self, player_names: List[str]):
        """Initializes the players in the Game."""
        players = []
        # TODO(ahammer): Do literally ANY error handling here
        for name in player_names:
            start_room = self.board.get_room(
                format_hallway_name(game_const.START_HALLWAY[name]))
            players.append(Player(name=name, room=start_room))
        return players
