import uuid
from typing import Dict, List

import attr


@attr.s(auto_attribs=True, slots=True)
class Message(object):
    """Generic message template with built-in classmethods, functions etc."""

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return attr.asdict(self)


@attr.s(auto_attribs=True, slots=True)
class PlayerSuggestionRequest(Message):
    """This is a Server request for a client to make a Suggestion"""
    game_id: str
    client_id: str
    suspects: str
    weapons: str
    rooms: str


@attr.s(auto_attribs=True, slots=True)
class PlayerSuggestionResponse(Message):
    """This is a Client response containing the Suggestion."""
    game_id: str
    client_id: str
    suspect: str = ''
    weapon: str = ''
    room: str = ''


@attr.s(auto_attribs=True, slots=True)
class PlayerSuggestionResult(Message):
    """Contains the results of the Suggestion, for the Client"""
    game_id: str
    client_id: str
    suspect: str = ''
    weapon: str = ''
    room: str = ''
    disproved_by: str = ''
    disproved_card: str = ''
    suggested_by: str = ''


@attr.s(auto_attribs=True, slots=True)
class PlayerAccusationRequest(Message):
    """This is a game-ending accusation, identical to a suggestion."""
    game_id: str
    client_id: str
    suspects: List[str]
    weapons: List[str]
    rooms: List[str]


@attr.s(auto_attribs=True, slots=True)
class PlayerAccusationResponse(Message):
    """This is a game-ending accusation, identical to a suggestion."""
    game_id: str
    client_id: str
    suspect: str = ''
    weapon: str = ''
    room: str = ''


@attr.s(auto_attribs=True, slots=True)
class PlayerAccusationResult(Message):
    """Contains the results of the Accusation, for the Client"""
    game_id: str
    client_id: str
    correct: bool
    suspect: str
    weapon: str
    room: str


@attr.s(auto_attribs=True, slots=True)
class PlayerMoveRequest(Message):
    """This is a server's request to a client for a PlayerMove."""
    game_id: str
    client_id: str
    move_options: List[str]


@attr.s(auto_attribs=True, slots=True)
class PlayerMoveResponse(Message):
    """This is a client's response to a PlayerMoveRequest."""
    game_id: str
    client_id: str
    move: str = ''


@attr.s(auto_attribs=True, slots=True)
class GameStateRequest(Message):
    """This is the servers broadcast of game state to all clients."""
    game_id: str
    client_id: str
    whereabouts: Dict[str, str]  # The Room.name (location) of each Player.name
    current_turn: str  # The Player.name of the current turn
    player_cards: List[str]  # The cards in the player's hand


@attr.s(auto_attribs=True, slots=True)
class ClientGameStateRequest(Message):
    """This is the client requesting the game state."""
    client_id: str


@attr.s(auto_attribs=True, slots=True)
class JoinGameRequest(Message):
    """This is the client request asking to join a game"""
    player: str


@attr.s(auto_attribs=True, slots=True)
class JoinGameResponse(Message):
    """This is the response to the client asking to join the game"""
    client_id: str
    player: str


@attr.s(auto_attribs=True, slots=True)
class StartGameRequest(Message):
    """This is the client request to the server to start the game"""
    client_id: str


@attr.s(auto_attribs=True, slots=True)
class StartGameResponse(Message):
    """This is the response to the client asking to start the game"""
    client_id: str
    game_id: str


@attr.s(auto_attribs=True, slots=True)
class PlayerCountRequest(Message):
    """This is the request to the server for the current player count in a particular game"""
    client_id: str


@attr.s(auto_attribs=True, slots=True)
class PlayerCountResponse(Message):
    """This is the reponse from the server for the player count"""
    client_id: str
    count: int


@attr.s(auto_attribs=True, slots=True)
class GameStepRequest(Message):
    """This is the request to the server to step the game forward"""


@attr.s(auto_attribs=True, slots=True)
class GameStepResponse(Message):
    """This is the response to the client asking to step the game forward"""
    success: bool


@attr.s(auto_attribs=True, slots=True)
class PlayerCountUpdateRequest(Message):
    """This is the server updating the client with the new player count"""
    count: int


@attr.s(auto_attribs=True, slots=True)
class PlayerCountUpdateResponse(Message):
    """This is the response to the server updating the player count"""
    accepted: bool