"""
Handles all database functions, configured for MongoDB connections
"""
import os
from datetime import datetime
from psycopg import connect, ClientCursor, errors
from psycopg.rows import dict_row, class_row
import sys
from uuid import UUID
import time
from imdb_dataclasses import Movie, Clue


class DBHandler:
    _TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, pg_url: str = None):
        if not pg_url:
            pg_url = os.getenv('POSTGRES_URL')
        self.connection = None
        try:
            print(pg_url)
            self.connection = connect(conninfo=pg_url, autocommit=True)
        except Exception as e:
            print(e)
            print('Failed to connect')
            sys.exit(1)

    def __del__(self):
        if self.connection:
            self.connection.close()

    def __execute_sql(self, query: str, values: dict,
                      return_data: bool = False):
        """
        Executes the query string passed to it
        """
        result = None
        with self.connection.cursor() as cur:
            try:
                cur.execute(query, values)
            except errors.UniqueViolation as e:
                print('SKIPPING DUPLICATE KEY')
                print(e)
            finally:
                if return_data:
                    result = cur.fetchall()
                    return result

    def _update_timestamp_row(self, table_name, timestamp_column, target_id,
                              id_value):
        update_query = """UPDATE %s SET %s = NOW() WHERE id = %s;"""
        update_values = (table_name, timestamp_column, target_id, id_value)
        self.__execute_sql(update_query, update_values)

    def add_player(self, username: str, password: str):
        """
        Adds a new entry to the `players` table when a new player plays their
        first game
        """
        insert_query = """
            INSERT INTO players (username, password)
            VALUES (%s, %s, %s)
        """
        insert_values = (username, password)
        self.__execute_sql(insert_query, insert_values)
        print("Player added successfully")

    def add_movie(self, movie_object: Movie):
        """
        Add a movie to the `movies` table when scraped from IMDB
        """
        insert_query = """
            INSERT INTO movies (title, release_year, imdb_id,
                                stripped_title)
            VALUES (%(title)s, %(release_year)s, %(imdb_id)s,
                    %(stripped_title)s)
        """
        self.__execute_sql(insert_query, movie_object.dict())
        db_entry = self.get_movie_by_imdb_id(movie_object.imdb_id)
        print(f"Movie {movie_object.title} added successfully")
        return db_entry.movie_id

    def get_categories(self):
        """
        Gets all data from categories table and returns it as a list of dicts
        """
        categories = {}
        with self.connection.cursor(row_factory=dict_row) as cur:
            try:
                cur.execute(
                    """SELECT category_id, display_name, short_name 
                    FROM categories""")
            except Exception as e:
                print(e)
            categories = cur.fetchall()
        return categories

    def get_movie_by_imdb_id(self, imdb_id):
        """
        Returns a Movie object from the data returned by searching for movie by
        IMDb's unique ID
        """
        select_query = """SELECT movie_id, imdb_id, title, stripped_title, 
        release_year FROM movies WHERE imdb_id=%s"""
        print(f'Finding {imdb_id}')
        with self.connection.cursor(row_factory=class_row(Movie)) as cur:
            try:
                record = cur.execute(select_query, [imdb_id]).fetchone()
            except errors.InFailedSqlTransaction as e:
                print(e)
            finally:
                if record:
                    return record

    def add_clue(self, clue: dict):
        """
        Add new hint to `hints` table when scraped from IMDB
        """
        insert_query = """
            INSERT INTO clues (movie_id, category_id, clue_text, spoiler)
            VALUES (%(movie_id)s, %(category_id)s, %(clue_text)s, %(spoiler)s)
        """
        self.__execute_sql(insert_query, clue)

    def add_guess(self, player_id: UUID, guessed_movie_id: UUID,
                  is_correct: bool):
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

    def add_score(self, player_id: UUID, score: int):
        insert_query = """
            INSERT INTO scores (player_id, score)
            VALUES (%s, %s)
        """
        insert_values = (player_id, score)
        self.__execute_sql(insert_query, insert_values)
        print('Successfully added player score')

    def get_clues(self, movie_object: Movie):
        select_query = """SELECT m.title, m.release_year, m.imdb_id,
                cat.display_name, c.clue_text, c.spoiler
                FROM clues c
                JOIN movies m ON c.movie_id = m.movie_id
                JOIN categories cat ON c.category_id = cat.category_id
                WHERE m.imdb_id = %(imdb_id)s
                ORDER BY cat.category_id;"""
        results = self.__execute_sql(select_query, movie_object.dict(), True)
        return results
