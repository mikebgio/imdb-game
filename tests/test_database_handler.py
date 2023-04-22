import pytest
import os
from uuid import UUID
import imdb_game.database.handler as database_handler
import imdb_game.database._dataclasses as dc
from test_tools import init_test_db
import testing.postgresql
from datetime import datetime
from psycopg import Connection


@pytest.fixture(scope='module')
def test_movie_1():
    test_movie_1 = dc.Movie(
        movie_id=UUID('12345678-1234-5678-1234-567812345678'),
        imdb_id='ttXX345XX', title='Test Movie',
        stripped_title='testmovie', release_year=1999)
    yield test_movie_1


@pytest.fixture(scope='module')
def test_movie_2():
    test_movie_2 = dc.Movie(
        movie_id=UUID('12345678-1234-5678-1234-567888888888'),
        imdb_id='ttXX456XX', title='Test Movie 2: The Sequel',
        stripped_title='testmovie2thesequel', release_year=2013)
    yield test_movie_2


DEFAULT_CATEGORIES = [{'category_id': 1, 'display_name': 'Sex & Nudity',
                       'short_name': 'nudity'},
                      {'category_id': 2, 'display_name': 'Violence & Gore',
                       'short_name': 'violence'},
                      {'category_id': 3, 'display_name': 'Profanity',
                       'short_name': 'profanity'}, {'category_id': 4,
                                                    'display_name': 'Alcohol, Drugs & Smoking',
                                                    'short_name': 'alcohol'},
                      {'category_id': 5,
                       'display_name': 'Frightening & Intense Scenes',
                       'short_name': 'frightening'}]


@pytest.fixture(scope="module")
def db_handler():
    with testing.postgresql.Postgresql() as postgresql:
        connection = init_test_db(postgresql)
        db_handler = database_handler.DBHandler(pg_url=postgresql.url())
        yield db_handler


def test__get_postgres_connection(db_handler):
    """
    Verifies that a connection can be made with private method
     _get_postgres_connection
    """
    conn = db_handler._get_postgres_connection(os.getenv('POSTGRES_URL'))
    assert isinstance(conn, Connection)

def test__execute_sql(db_handler):
    """
    Tests a basic SELECT query on the categories table
    """
    # Select from Full Table
    select_query = """SELECT * FROM categories"""
    categories = db_handler._execute_sql(select_query, return_data=True,
                                         row_factory=database_handler.dict_row)
    assert categories == DEFAULT_CATEGORIES
    # SELECT from empty Table
    select_query = """SELECT * FROM movies"""
    movies = db_handler._execute_sql(select_query, return_data=True)
    assert movies == []


def test_add_player(db_handler):
    """
    Tests adding player to players Table
    """
    username = 'testuser'
    db_handler.add_player(username)
    player = db_handler.get_player_by_username(username)
    assert player.username == username


def test_get_player_by_username(db_handler):
    """
    Tests SELECTing a player by their username from players Table
    """
    username = 'testuser'
    player = db_handler.get_player_by_username(username)
    assert player.username == username


def test_add_game(db_handler):
    """
    Tests adding Game to the games Table
    """
    player = db_handler.get_player_by_username('testuser')
    game = dc.Game(player_id=player.player_id, score=10, round=1)
    db_handler.add_game(game)
    # Add assertions for the added game


def test_add_movie(db_handler, test_movie_1, test_movie_2):
    """
    Tests adding a new Movie to the movies Table
    """
    for movie in [test_movie_1, test_movie_2]:
        db_handler.add_movie(movie)
        movie_from_db = db_handler.get_movie_by_imdb_id(movie.imdb_id)
        assert movie_from_db.title == movie.title
        assert movie_from_db.imdb_id == movie.imdb_id
        assert movie_from_db.release_year == movie.release_year
        assert movie_from_db.stripped_title == movie.stripped_title


def test_get_movie_by_movie_id(db_handler, test_movie_1, test_movie_2):
    """
    Tests getting a Movie from the movies Table by a movie_id
    """
    for movie in [test_movie_1, test_movie_2]:
        movie_from_db = db_handler.get_movie_by_imdb_id(movie.imdb_id)
        assert movie_from_db.title == movie.title
        assert movie_from_db.imdb_id == movie.imdb_id
        assert movie_from_db.release_year == movie.release_year
        assert movie_from_db.stripped_title == movie.stripped_title


def test_add_clue(db_handler, test_movie_1):
    """
    Tests creating a new clue for a target movie in the clues Table
    """
    movie_from_db = db_handler.get_movie_by_imdb_id(test_movie_1.imdb_id)
    assert movie_from_db
    clue = dc.Clue(movie_id=movie_from_db.movie_id,
                   category_id=1, clue_text='Test clue', spoiler=False,
                   date_created=datetime.now())
    db_handler.add_clue(clue)
    clues_from_db = db_handler.get_clues_by_movie_id(movie_from_db.movie_id)
    assert any([clue_from_db.clue_text == clue.clue_text for clue_from_db in
                clues_from_db])


def test_get_categories(db_handler):
    """
    Tests getting the categories dictionary
    """
    categories = db_handler.get_categories()
    assert categories == DEFAULT_CATEGORIES
    assert len(categories) == len(DEFAULT_CATEGORIES)

def test_update_timestamp_row(db_handler)
