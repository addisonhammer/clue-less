# Declare constants for Game
from typing import Tuple

def format_hallway_name(hallway: Tuple[str, str]) -> str:
    return f'{hallway[0]} - {hallway[1]} Hallway'

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

EMPTY = ''
ROOMS_LAYOUT = (
    STUDY,                   format_hallway_name((STUDY, HALL)),            HALL,                 format_hallway_name((HALL, LOUNGE)),      LOUNGE,
    format_hallway_name((STUDY, LIBRARY)),        EMPTY,                    format_hallway_name((HALL, BILLIARD)),     EMPTY,               format_hallway_name((LOUNGE, DINING)),
    LIBRARY,                 format_hallway_name((LIBRARY, BILLIARD)),      BILLIARD,             format_hallway_name((DINING, BILLIARD)),  DINING, 
    format_hallway_name((CONSERVATORY, LIBRARY)), EMPTY,                    format_hallway_name((BALLROOM, BILLIARD)), EMPTY,               format_hallway_name((DINING, KITCHEN)),
    CONSERVATORY,            format_hallway_name((BALLROOM, CONSERVATORY)), BALLROOM,             format_hallway_name((KITCHEN, BALLROOM)), KITCHEN)

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