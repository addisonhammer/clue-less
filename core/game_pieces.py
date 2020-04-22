from enum import Enum
from typing import List

import networkx as nx
import attr


class CardType(Enum):
    ROOM = 1
    WEAPON = 2
    CHARACTER = 3


@attr.s(auto_attribs=True, slots=True)
class Card(object):
    """Class representing a single card."""
    name: str
    type: CardType


class RoomType(Enum):
    REGULAR = 1
    HALLWAY = 2


@attr.s(auto_attribs=True, slots=True)
class Room(object):
    """Class representing a room on the Game Board."""
    name: str
    type: RoomType

    def __str__(self):
        return str(self.__dict__)


class Board(nx.Graph):
    """Subclass of a NetworkX Graph that adds Room Instance lookup."""

    def __init__(self, *args, rooms: List[Room], **kwargs):
        """Overloaded __init__ method adds _rooms_dict as a kwarg and stores it."""
        super().__init__(*args, **kwargs)
        self._rooms_dict = {room.name: room for room in rooms}

    def get_adj_rooms(self, room: Room) -> List[Room]:
        """Returns the list of adj Room instances"""
        return [self._rooms_dict[adj_room] for adj_room in self.neighbors(room.name)]

    def get_room(self, room_name: str) -> Room:
        """Return a room instance by name."""
        return self._rooms_dict[room_name]


@attr.s(auto_attribs=True, slots=True)
class Player(object):
    """Class representing a player in the Game."""
    name: str
    room: Room
    playing: bool
    cards: List[Card]
