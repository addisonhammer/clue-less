from typing import List, Tuple, Dict
from enum import Enum
import random

import networkx as nx

# Declare constants for Game
PLUM ='Prof. Plum'
WHITE = 'Mrs. White'
MUSTARD = 'Col. Mustard'
SCARLET = 'Miss Scarlet'
PEACOCK = 'Mrs. Peacock'
GREEN = 'Mr. Green'
CHARACTERS = (PLUM, WHITE, MUSTARD, SCARLET, PEACOCK, GREEN)

REVOLVER = 'Revolver'
DAGGER = 'Dagger'
PIPE = 'Lead Pipe'
ROPE = 'Rope'
CANDLESTICK = 'Candlestick'
WRENCH = 'Wrench'
WEAPONS = (REVOLVER, DAGGER, PIPE, ROPE, CANDLESTICK, WRENCH)

STUDY = 'Study'
HALL = 'Hall'
LOUNGE = 'Lounge'
LIBRARY = 'Library'
BILLIARD = 'Billiard Room'
DINING = 'Dining Room'
BALLROOM = 'Ballroom'
KITCHEN = 'Kitchen'
CONSERVATORY = 'Conservatory'
ROOMS = (STUDY, HALL, LOUNGE, LIBRARY, BILLIARD, DINING, BALLROOM, KITCHEN, CONSERVATORY)

HALLWAYS = (
    (STUDY, HALL),
    (STUDY, LIBRARY),
    (HALL, BILLIARD),
    (HALL, LOUNGE),
    (LOUNGE, DINING),
    (DINING, BILLIARD),
    (DINING, KITCHEN),
    (KITCHEN, BALLROOM),
    (BALLROOM, CONSERVATORY),
    (BALLROOM, BILLIARD),
    (CONSERVATORY, LIBRARY),
    (LIBRARY, BILLIARD),
)

SECRET_PASSAGES = (
    (STUDY, KITCHEN),
    (CONSERVATORY, LOUNGE)
)

START_HALLWAY = {
    PLUM: (STUDY, LIBRARY),
    WHITE: (KITCHEN, BALLROOM),
    MUSTARD: (LOUNGE, DINING),
    SCARLET: (HALL, LOUNGE),
    PEACOCK: (CONSERVATORY, LIBRARY),
    GREEN: (BALLROOM, CONSERVATORY),
}

# Module-level helper functions
def format_hallway_name(hallway: Tuple[str, str]):
    return f'{hallway[0]} - {hallway[1]} Hallway'

class CardType(Enum):
    ROOM = 1
    WEAPON = 2
    PLAYER = 3

class Card(object):
    """Class representing a single card."""

    def __init__(self, name: str, card_type: CardType):
        self.name = name
        self.type = card_type

    def __str__(self):
        return str(self.__dict__)

class RoomType(Enum):
    REGULAR = 1
    HALLWAY = 2

class Room(object):
    """Class representing a room on the Game Board."""

    def __init__(self, name:str, room_type: RoomType):
        self.type = room_type
        self.name = name

    def __str__(self):
        return str(self.__dict__)

class Board(nx.Graph):
    """Subclass of a NetworkX Graph that adds Room Instance lookup."""

    def __init__(self, *args, rooms: List[Room], **kwargs):
        """Overloaded __init__ method adds _rooms_dict as a kwarg and stores it."""
        super().__init__(*args, **kwargs)
        self._rooms_dict = {room.name: room for room in rooms}

    def get_adj_rooms(self, room: Room):
        """Returns the list of adj Room instances"""
        return [self._rooms_dict[adj_room] for adj_room in self.neighbors(room.name)]

    def get_room(self, room_name: str):
        """Return a room instance by name."""
        return self._rooms_dict[room_name]

class Player(object):
    """Class representing a player in the Game."""

    def __init__(self, name: str, start_room: Room):
        self.name = name
        self.room = start_room
        self.cards = []

    def __str__(self):
        return str(self.__dict__)

class Game(object):
    """Class representing the game instance."""

    def __init__(self, player_names: List[str]):
        """Initialize the Game, given a list of player names."""

        # First initialize the board, and the contained Room instances
        self.board = self._init_board()

        # Next initialize the list of players, and their start_room
        self.players = self._init_players(player_names)

        # Now deal the cards to the murder_deck, and to each player
        self._deal_cards()

        self.turn = 0
        self.result = ''

    def take_turn(self):
        pass

    def _deal_cards(self):
        """Deals out the cards in the deck to start the game.

        Side-Effects:
          - Assigns a List[Card] to the Game.murder_deck attribute
          - Loops through Game.players and appends Card instances to the Player.card attribute
        """

        # First Initialize the cards from constants)
        weapons = [Card(name, CardType.WEAPON) for name in WEAPONS]
        characters = [Card(name, CardType.PLAYER) for name in CHARACTERS]
        rooms = [Card(name, CardType.ROOM) for name in ROOMS]

        # Remove characters from the deck that are not playing
        player_names = [player.name for player in self.players]
        characters = [card for card in characters if card.name in player_names]

        # Shuffle each deck, and pop a random card for the murder deck
        random.shuffle(weapons)
        random.shuffle(characters)
        random.shuffle(rooms)
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
        rooms.extend([Room(name=room, room_type=RoomType.REGULAR) for room in ROOMS])
        rooms.extend([Room(name=format_hallway_name(hallway), room_type=RoomType.HALLWAY) for hallway in HALLWAYS])

        # Then use the static adjacency graph to generate a Board and return it
        board = Board(rooms=rooms)
        for room in ROOMS:
            board.add_node(room)
        for hallway in HALLWAYS:
            board.add_node(format_hallway_name(hallway))
            for adjacent_room in hallway:
                board.add_edge(adjacent_room, format_hallway_name(hallway))
        for secret_passage in SECRET_PASSAGES:
            board.add_edge(*secret_passage)
        return board

    def _init_players(self, player_names: List[str]):
        """Initializes the players in the Game."""
        players = []
        for name in player_names:
            start_room = self.board.get_room(format_hallway_name(START_HALLWAY[name]))
            players.append(Player(name=name, start_room=start_room))
        return players