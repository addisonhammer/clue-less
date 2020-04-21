import uuid
from typing import Dict, List

import attr


@attr.s(auto_attribs=True, slots=True)
class Message(object):
    """Generic message template with built-in classmethods, functions etc."""
    game_id: str
    player: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return attr.asdict(self)


@attr.s(auto_attribs=True, slots=True)
class PlayerSuggestionRequest(Message):
    """This is a Server request for a client to make a Suggestion"""
    suspects: List[str]
    weapons: List[str]
    rooms: List[str]


@attr.s(auto_attribs=True, slots=True)
class PlayerSuggestionResponse(Message):
    """This is a Client response containing the Suggestion."""
    suspect: str = ''
    weapon: str = ''
    room: str = ''


@attr.s(auto_attribs=True, slots=True)
class PlayerSuggestionResult(Message):
    """Contains the results of the Suggestion, for the Client"""
    suspect: str = ''
    weapon: str = ''
    room: str = ''
    disproved_by: str = ''
    disproved_card: str = ''


@attr.s(auto_attribs=True, slots=True)
class PlayerAccusationRequest(Message):
    """This is a game-ending accusation, identical to a suggestion."""
    suspects: List[str]
    weapons: List[str]
    rooms: List[str]


@attr.s(auto_attribs=True, slots=True)
class PlayerAccusationResponse(Message):
    """This is a game-ending accusation, identical to a suggestion."""
    suspect: str = ''
    weapon: str = ''
    room: str = ''


@attr.s(auto_attribs=True, slots=True)
class PlayerAccusationResult(Message):
    """Contains the results of the Accusation, for the Client"""
    correct: bool
    suspect: str
    weapon: str
    room: str


@attr.s(auto_attribs=True, slots=True)
class PlayerMoveRequest(Message):
    """This is a server's request to a client for a PlayerMove."""
    move_options: List[str]


@attr.s(auto_attribs=True, slots=True)
class PlayerMoveResponse(Message):
    """This is a client's response to a PlayerMoveRequest."""
    move: str = ''


@attr.s(auto_attribs=True, slots=True)
class GameStateRequest(Message):
    """This is the servers broadcast of game state to all clients."""
    whereabouts: Dict[str, str]  # The Room.name (location) of each Player.name
    current_turn: str  # The Player.name of the current turn


@attr.s(auto_attribs=True, slots=True)
class GameStateResponse(Message):
    """This is the client response indicating they are still connected."""
    connected: bool

@attr.s(auto_attribs=True, slots=True)
class JoinGameRequest(Message):
    """This is the client request asking to join a game"""
    name: str

@attr.s(auto_attribs=True, slots=True)
class JoinGameResponse(Message):
    """This is the response to the client asking to join the game"""
    client_id: str
    accepted: bool

@attr.s(auto_attribs=True, slots=True)
class StartGameRequest(Message):
    """This is the response to the client asking to join the game"""
    client_id: str

@attr.s(auto_attribs=True, slots=True)
class StartGameResponse(Message):
    """This is the response to the client asking to join the game"""
    accepted: bool

@attr.s(auto_attribs=True, slots=True)
class PlayerCountRequest(Message):
    """This is the response to the client asking to join the game"""

@attr.s(auto_attribs=True, slots=True)
class PlayerCountResponse(Message):
    """This is the response to the client asking to join the game"""
    count: int

@attr.s(auto_attribs=True, slots=True)
class GameStepRequest(Message):
    """This is the response to the client asking to join the game"""

@attr.s(auto_attribs=True, slots=True)
class GameStepResponse(Message):
    """This is the response to the client asking to join the game"""
    success: bool

def generate_message_id() -> int:
    return uuid.uuid4().fields[1]
