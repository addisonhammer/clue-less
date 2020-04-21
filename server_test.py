import logging

from server import app
from core import client_boundary


def main():
    logging.basicConfig()
    client_boundary._set_up_debug()
    app.DEBUG = True
    app.main()


if __name__ == "__main__":
    main()
