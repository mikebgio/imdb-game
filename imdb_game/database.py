"""
Handles all database functions, configured for MongoDB connections
"""
from datetime import datetime
import psycopg
import sys
import uuid


class DBHandler:
    _TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, pg_url: str = "postgresql://imdb_host:password@localhost:5432/imdb"):
        self.connection = None
        try:
            print(pg_url)
            self.connection = psycopg.connect(conninfo=pg_url)
        except Exception as e:
            print(e)
            print('Failed to connect')
            sys.exit(1)

    def __del__(self):
        if self.connection:
            self.connection.close()

    def __execute_sql(self, query: str, values: tuple):
        """
        Executes the query string passed to it
        """
        result = None
        with self.connection.cursor() as cur:
            try:
                result = cur.execute(query, values)
                # id_of_new_row = cur.fetchone()[0]
            except Exception as e:
                print(e)
            finally:
                if result:
                    self.connection.commit()
                    # return id_of_new_row

    def _update_timestamp_row(self, table_name, timestamp_column, target_id, id_value):
        update_query = """UPDATE %s SET %s = NOW() WHERE id = %s;"""
        update_values = (table_name, timestamp_column, target_id, id_value)
        self.__execute_sql(update_query, update_values)
    def add_player(self, username: str, password: str):
        """
        Adds a new entry to the `players` table when a new player plays their
        first game
        """
        player_id = str(uuid.uuid4())
        insert_query = """
            INSERT INTO players (player_id, username, password)
            VALUES (%s, %s, %s)
        """
        insert_values = (player_id, username, password)
        self.__execute_sql(insert_query, insert_values)
        print("Player added successfully")

    def add_movie(self, movie_title: str, year: int, imdb_id: str):
        """
        Add a movie to the `movies` table when scraped from IMDB
        """
        insert_query = """
            INSERT INTO movies (movie_title, year, imdb_id)
            VALUES (%s, %s, %s)
        """
        insert_values = (movie_title, year, imdb_id)
        self.__execute_sql(insert_query, insert_values)
        print("Movie added successfully")

    def add_clue(self, movie_id: uuid, category_id: int, clue_text: str,
                 spoiler: bool):
        """
        Add new hint to `hints` table when scraped from IMDB
        """
        insert_query = """
            INSERT INTO clues (movie_id, category_id, clue_text, spoiler)
            VALUES (%s, %s, %s, %s)
        """
        insert_values = (movie_id, category_id, clue_text, spoiler)
        self.__execute_sql(insert_query, insert_values)
        print("Hint added successfully")

    def add_guess(self, player_id: uuid, guessed_movie_id: uuid, is_correct: bool):
        """
        Adds new player guess to `guesses` table when a player makes a guess
        """
        insert_query = """
            INSERT INTO guesses (player_id, guessed_movie_id, is_correct)
            VALUES (%s, %s, %s)
        """
        insert_values = (player_id, guessed_movie_id, is_correct)
        self.__execute_sql(insert_query, insert_values)
        print("Guess added successfully")

    def add_score(self, player_id: uuid, score: int):
        insert_query = """
            INSERT INTO scores (player_id, score)
            VALUES (%s, %s)
        """
        insert_values = (player_id, score)
        self.__execute_sql(insert_query, insert_values)
        print('Successfully added player score')
