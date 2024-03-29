"""
Handles all database functions, configured for MongoDB connections
"""
import os
from datetime import datetime
from psycopg import connect, ClientCursor, errors
from psycopg.rows import dict_row, class_row, tuple_row
import sys
from uuid import UUID
import time
from .dataclasses import Movie, Clue, Game, Player
# from dotenv import load_dotenv
#
# load_dotenv('../../.env')


class DBHandler:
    """
    Handles all Database actions for IMDb Game
    """
    _TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, pg_url: str = None) -> None:
        """
        Initializes the database handler
        """
        if not pg_url:
            pg_url = os.getenv('POSTGRES_URL')
        self.connection = self._get_postgres_connection(pg_url)

    def __del__(self):
        """
        Closes the connection to the database
        """
        if self.connection:
            self.connection.close()

    def _get_postgres_connection(self, pg_url: str):
        """
        Accepts a postgresql URL and returns a connection
        """
        try:
            connection = connect(conninfo=pg_url, autocommit=True)
        except Exception as exc:
            print(exc)
            print('Failed to connect')
            sys.exit(1)
        return connection

    def _execute_sql(self, query: str, values=None,
                     return_data: bool = False,
                     row_factory=tuple_row):
        """
        Executes the query string passed to it
        """
        result = None
        with self.connection.cursor(row_factory=row_factory) as cur:
            try:
                if values:
                    cur.execute(query, values)
                else:
                    cur.execute(query)
            except errors.UniqueViolation as err:
                print('SKIPPING DUPLICATE KEY')
                print(err)
            if return_data and query.startswith('SELECT'):
                result = cur.fetchall()
                return result
            elif return_data:
                self.connection.commit()
                result = cur.fetchall()
                return result
        self.connection.commit()
        return None

    def _update_player_last_played(self, player: Player):
        """
        Updates the timestamp column of the table passed to it
        """
        update_query = f"""
        UPDATE players SET date_last_played = now()
        WHERE player_id = %s"""
        update_values = str(player.player_id)
        self._execute_sql(update_query, [update_values])

    def add_player_by_username(self, player: Player):
        """
        Adds a new entry to the `players` table when a new player plays their
        first game
        """
        insert_query = """
            INSERT INTO players (username)
            VALUES (%s)
        """
        print(f"Adding {player.username}")

        self._execute_sql(insert_query, [player.username])
        print(f"Player {player.username} added successfully")

    def add_full_player(self, player: Player):
        """
        Add a complete Player object as a row to explicitly write all columns
        from object
        """
        insert_query = """
        INSERT INTO players (player_id, username, date_created,
        date_last_played)
        VALUES (%(player_id)s, %(username)s, %(date_created)s,
        %(date_last_played)s)
        """
        self._execute_sql(insert_query, player.dict())
        print(f"Player {player.username} added successfully")

    def add_game(self, game_obj: Game):
        """
        Creates new game in the `games` table
        """
        insert_query = """
        INSERT INTO games(player_id, score, round)
        VALUES (%(player_id)s, %(score)s, %(round)s)
        """
        self._execute_sql(insert_query, game_obj.dict())
        print("New Game created successfully!")

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
        self._execute_sql(insert_query, movie_object.dict())
        db_entry = self.get_movie_by_imdb_id(movie_object.imdb_id)
        print(f"Movie {movie_object.title} added successfully")
        return db_entry.movie_id

    def get_categories(self):
        """
        Gets all data from categories table and returns it as a list of dicts
        """
        categories = {}
        select_query = """SELECT category_id, display_name, short_name
         FROM categories"""
        categories = self._execute_sql(select_query, row_factory=dict_row,
                                       return_data=True)
        return categories

    def get_movie_by_imdb_id(self, imdb_id):
        """
        Returns a Movie object from the data returned by searching for movie by
        IMDb's unique ID
        """
        select_query = """SELECT movie_id, imdb_id, title, stripped_title,
        release_year FROM movies WHERE imdb_id=%s"""
        record = None
        print(f'Finding {imdb_id}')
        with self.connection.cursor(row_factory=class_row(Movie)) as cur:
            try:
                cur.execute(select_query, [imdb_id])
                record = cur.fetchone()
            except errors.InFailedSqlTransaction as exc:
                print(exc)
            return record

    def get_movie_by_movie_id(self, movie_id):
        """
        Returns a Movie object from the data returned by searching for movie by
        IMDb's unique ID
        """
        select_query = """SELECT movie_id, imdb_id, title, stripped_title,
        release_year FROM movies WHERE movie_id=%s"""
        record = None
        print(f'Finding {movie_id}')
        with self.connection.cursor(row_factory=class_row(Movie)) as cur:
            try:
                record = cur.execute(select_query, [movie_id]).fetchone()
            except errors.InFailedSqlTransaction as error:
                print(error)
            return record

    def add_clue(self, clue_obj: Clue):
        """
        Add new Clue to `clues` table when scraped from IMDB
        Args:
            clue_obj: instance of Clue class
        """
        insert_query = """
            INSERT INTO clues (movie_id, category_id, clue_text, spoiler)
            VALUES (%(movie_id)s, %(category_id)s, %(clue_text)s, %(spoiler)s)
        """
        result = self._execute_sql(insert_query, values=clue_obj.dict())

    # def add_guess(self, player_id: UUID, guessed_movie_id: UUID,
    #               is_correct: bool):
    #     """
    #     Adds new player guess to `guesses` table when a player makes a guess
    #     """
    #     insert_query = """
    #         INSERT INTO guesses (player_id, guessed_movie_id, is_correct, guess_text)
    #         VALUES (%s, %s, %s, %s)
    #     """
    #     insert_values = (player_id, guessed_movie_id, is_correct)
    #     self._execute_sql(insert_query, insert_values)
    #     print("Guess added successfully")

    # def add_score(self, player_id: UUID, score: int):
    #     """
    #     Inserts new row into `scores` table
    #     """
    #     insert_query = """
    #         INSERT INTO scores (player_id, score)
    #         VALUES (%s, %s)
    #     """
    #     insert_values = (player_id, score)
    #     self._execute_sql(insert_query, insert_values)
    #     print('Successfully added player score')

    # def get_clues(self, movie_object: Movie):
    #     """
    #     Selects all clues for a given Movie from `clues` table.
    #     Returns:
    #         a list of Clue objects.
    #     """
    #     select_query = """
    #         SELECT m.title, m.release_year, m.imdb_id, cat.display_name,
    #         c.clue_text, c.spoiler
    #         FROM clues c
    #         JOIN movies m ON c.movie_id = m.movie_id
    #         JOIN categories cat ON c.category_id = cat.category_id
    #         WHERE m.imdb_id = %(imdb_id)s
    #         ORDER BY cat.category_id;"""
    #     results = self._execute_sql(select_query, movie_object.dict(), True)
    #     return results

    def get_three_movie_options(self):
        """
        Selects three random rows from `movies`
        Returns:
            dict_row
        """
        select_query = """
            SELECT movie_id, release_year
            FROM movies
            --WHERE movie_id NOT IN (
            --    SELECT movie_id
            --    FROM player_movies
            --    WHERE player_id = %s
            --)
            ORDER BY random() DESC
            LIMIT 3;
        """
        # TODO: Figure out how to quickly filter movies that the player has
        #  already played
        records = None
        with self.connection.cursor(row_factory=dict_row) as cur:
            try:
                records = cur.execute(select_query, {}).fetchall()
            except Exception as e:
                print(e)
            except errors.InFailedSqlTransaction as e:
                print(e)
            return records

    def get_clues_by_movie_id(self, movie_id: UUID):
        """
        Selects all clues for a given movie id from `clues` table.
        Returns a list of Clue objects.
        """
        select_query = """
        SELECT * FROM clues WHERE movie_id = %s
        """
        records = self._execute_sql(select_query, [movie_id], return_data=True,
                                    row_factory=class_row(Clue))
        return records

    def get_player_by_username(self, player: Player):
        """
        Selects a player by username from `players` table.
        Returns a Player object.
        """
        select_query = "SELECT * FROM players WHERE username = %s"
        player_data = self._execute_sql(select_query, [player.username],
                                   row_factory=class_row(Player),
                                   return_data=True)[0]
        print(f'player is {player_data}')
        return player_data
