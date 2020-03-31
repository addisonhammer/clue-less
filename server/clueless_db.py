import psycopg2 as database
import traceback
import socket
import logging
import uuid
from socket import SHUT_RDWR


class Clueless_Database:

    connection = None
    settings = None

    def __init__(self, settings):
        self.settings = settings
        return

    def connect(self, settings = None):
        # Check if connection exists and is open
        if self.connection != None and self.connection == 0:
            # If we have new settings
            if settings != self.settings and settings != None:
                # Close old connection
                self.disconnect()
                # New connection opened later
            else:
                # connection is good
                return True
        
        # Check to make sure we have settings to create the connection
        if self.settings == None and settings == None:
            return False

        # Favor new settings over old settings.
        if settings != None:
            self.settings = settings

        # Try creating a new connection
        try:
            self.connection = database.connect(**self.settings)
            return True
        except:
            # .connect throws if it fails.
            # print(traceback.format_exc())
            return False
        
    def disconnect(self):
        self.connection.close()
        return
    
    def db_error(self):
        return not self.connect()

    def create_database(self):
            if self.db_error():
                return "Database Error"

            try:
                cursor = self.connection.cursor()
                cursor.execute(open("server/database_setup.postgres","r").read())
                cursor.close()
                self.connection.commit()
                return str("Success")
            except:
                return traceback.format_exc()

# Note on cursors: in general, create a new one for each command, 
#   and close them when the result data is no longer necessary.
# Only reuse cursors when doing a bunch of updates or inserts.

    def generate_uuid(self) -> int:
        return uuid.uuid4().fields[1]

    def get_users(self):
        if self.db_error():
            return "Database Error"

        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM "User"')
        result = cursor.fetchall()
        cursor.close()
        return result

    def start_game(self, game_id: int, user_id: int, user_name: str,
                   country_code: int, status: str):
        if self.db_error():
            return 'Database Error'

        cursor = self.connection.cursor()
        insert_user = """INSERT INTO "User"("UserID", "Name", "CountryCode")
                         VALUES (%s, %s, %s)"""
        logging.info(insert_user, user_id, user_name, country_code)
        cursor.execute(insert_user, (user_id, user_name, country_code))

        insert_game = """INSERT INTO "Game"("GameID", "UserID", "Status")
                         VALUES (%s, %s, %s)"""
        logging.info(insert_game, game_id, user_id, status)
        cursor.execute(insert_game, (game_id, user_id, status))
        self.connection.commit()
        cursor.close()
        return 'Success'        

    def set_murder_deck(self, game_id: int, suspect_card: str,
                        weapon_card: str, room_card: str):
        if self.db_error():
            return 'Database Error'

        cursor = self.connection.cursor()
        insert_murder_deck = """INSERT INTO "MurderDeck"("GameID", "SuspectCard", "WeaponCard", "RoomCard")
                                VALUES (%s, %s, %s, %s)"""
        logging.info(insert_murder_deck, game_id, suspect_card, weapon_card, room_card)
        cursor.execute(insert_murder_deck, (game_id, suspect_card, weapon_card, room_card))
        self.connection.commit()
        cursor.close()
        return 'Success'

    def validate_accusation(self, game_id: int, suspect_card: str,
                            weapon_card: str, room_card: str):
        if self.db_error():
            return 'Database Error'

        cursor = self.connection.cursor()
        select_murder_deck = """SELECT "GameID", "SuspectCard", "WeaponCard", "RoomCard"
                                FROM "MurderDeck" """
        cursor.execute(select_murder_deck)
        result = cursor.fetchone()
        cursor.close()
        accusation = (game_id, suspect_card, weapon_card, room_card)
        logging.info('Comparing: %s==%s', result, accusation)
        return result == accusation
