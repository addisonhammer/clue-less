import logging

from core.game import Game
from core import game_const as g
from core import client_boundary as c


def main():
    logging.basicConfig()
    client1 = c.Client(g.MUSTARD, 'www.mocky.io/v2', '')
    client2 = c.Client(g.SCARLET, 'www.mocky.io/v2', '')
    client3 = c.Client(g.WHITE, 'www.mocky.io/v2', '')
    game = Game([client1, client2, client3])
    game.take_turn()
    game.take_turn()
    game.take_turn()
    print('Done!')


if __name__ == "__main__":
    main()
