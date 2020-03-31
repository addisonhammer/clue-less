import psycopg2 as database
import traceback
import socket
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

    def get_users(self):
        if self.db_error():
            return "Database Error"

        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM User")
        result = cursor.fetchall()
        cursor.close()
        return result
