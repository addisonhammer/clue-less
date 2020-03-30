from typing import List

import networkx as nx

NAMES = (
    'Prof. Plum',
    'Mrs. White',
    'Col. Mustard',
    'Miss Scarlet',
    'Mrs. Peacock',
    'Mr. Green',
)

WEAPONS = (
    'Revolver',
    'Dagger',
    'Lead Pipe',
    'Rope',
    'Candlestick',
    'Wrench',
)

ROOMS = (
    'Study',
    'Hall',
    'Lounge',
    'Library',
    'Billiard Room',
    'Dining Room',
    'Ballroom',
    'Kitchen',
    'Conservatory',
)

HALLWAYS = (
    ('Study', 'Hall'),
    ('Study', 'Library'),
    ('Hall', 'Billiard Room'),
    ('Hall', 'Lounge'),
    ('Lounge', 'Dining Room'),
    ('Dining Room', 'Billiard Room'),
    ('Dining Room', 'Kitchen'),
    ('Kitchen', 'Ballroom'),
    ('Ballroom', 'Conservatory'),
    ('Ballroom', 'Billiard Room'),
    ('Conservatory', 'Library'),
    ('Library', 'Billiard Room'),
)

SECRET_PASSAGES = (
    ('Study', 'Kitchen'),
    ('Conservatory', 'Lounge')
)

BOARD = nx.Graph()
for room in ROOMS:
    BOARD.add_node(room)
for hallway in HALLWAYS:
    BOARD.add_node(hallway)
    for adjacent_room in hallway:
        BOARD.add_edge(adjacent_room, hallway)
for secret_passage in SECRET_PASSAGES:
    BOARD.add_edge(*secret_passage)


def get_adjacent_rooms(room: str) -> List[str]:
    """Uses the game board to return a list of valid moves."""
    return list(BOARD.neighbors(room))