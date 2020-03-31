import uuid
from typing import Dict, List

import attr


@attr.s(auto_attribs=True, slots=True)
class Message(object):
    """Generic message template with built-in classmethods, functions etc."""
    message_id: int
    player: str

    @classmethod
    def from_dict(cls, data):
        return cls(**data)

    def to_dict(self):
        return attr.asdict(self)


@attr.s(auto_attribs=True, slots=True)
class PlayerSuggestion(Message):
    """This is a benign suggestion made in a user's normal turn."""
    accused: str
    weapon: str
    room: str


@attr.s(auto_attribs=True, slots=True)
class PlayerAccusation(Message):
    """This is a game-ending accusation, identical to a suggestion."""
    accused: str
    weapon: str
    room: str

@attr.s(auto_attribs=True, slots=True)
class PlayerMove(Message):
    """This is a player's request to move to a new location."""
    new_location: str


@attr.s(auto_attribs=True, slots=True)
class GameState(Message):
    """This is the servers broadcast of game state to all clients."""
    player_locations: Dict[str, str]
    cards: List[str]
    current_player: str
    suggester: str
    suggestion_accused: str
    suggestion_weapon: str
    suggestion_room: str
    suggestion_refuted_by: str

def generate_message_id() -> int:
    return uuid.uuid4().fields[1]