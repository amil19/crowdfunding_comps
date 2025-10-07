import psycopg2
from dotenv import load_dotenv
import os

class Connections():
    """Class to manage connections between cloud sources."""

    def __init__(self):
        """Loads environment variables and opens connection."""

        # Load environment variables from .env
        load_dotenv()

        # # Fetch variables
        USER = os.getenv("user")
        PASSWORD = os.getenv("password")
        HOST = os.getenv("host")
        PORT = os.getenv("port")
        DBNAME = os.getenv("dbname")

        self.uri = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}'

        try:
            self.db_connection = psycopg2.connect(
                user=USER,
                password=PASSWORD,
                host=HOST,
                port=PORT,
                dbname=DBNAME
            )
        except Exception as e:
            print("Encountered an error when trying to establish a connection.")
            print(e[:100])