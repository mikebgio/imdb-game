import pytest
import os
from uuid import UUID, uuid4
import imdb_game.database.handler as database_handler
import imdb_game.database.dataclasses as dc
from test_tools import init_test_db
import testing.postgresql
from datetime import datetime, timedelta
from psycopg import Connection

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

TEST_DB_URL = None


@pytest.fixture(scope="module")
def db_handler():
    with testing.postgresql.Postgresql() as postgresql:
        global TEST_DB_URL
        TEST_DB_URL = postgresql.url()
        connection = init_test_db(postgresql)
        db_handler = database_handler.DBHandler(pg_url=postgresql.url())
        yield db_handler


@pytest.fixture(scope='module')
def movie_1():
    test_movie_1 = dc.Movie(
        movie_id=UUID('12345678-1234-5678-1234-567812345678'),
        imdb_id='ttXX345XX', title='Test Movie',
        stripped_title='testmovie', release_year=1999)
    yield test_movie_1


@pytest.fixture(scope='module')
def movie_2():
    test_movie_2 = dc.Movie(
        movie_id=UUID('12345678-1234-5678-1234-567888888888'),
        imdb_id='ttXX456XX', title='Test Movie 2: The Sequel',
        stripped_title='testmovie2thesequel', release_year=2013)
    yield test_movie_2


@pytest.fixture(scope='module')
def player(db_handler):
    username = 'test_user'
    new_player = dc.Player(username=username)
    db_handler.add_player_by_username(new_player)
    new_player = db_handler.get_player_by_username(new_player)
    yield new_player


def test__get_postgres_connection(db_handler):
    """
    Verifies that a connection can be made with private method
     _get_postgres_connection
    """
    conn = db_handler._get_postgres_connection(TEST_DB_URL)
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
    #  Add a second player separate from player()
    username_only_player = dc.Player(username='second_test_user')
    db_handler.add_player_by_username(username_only_player)
    player_data = db_handler.get_player_by_username(username_only_player)
    assert username_only_player.username == player_data.username
    assert player_data.player_id is not None
    assert isinstance(player_data.player_id, UUID)
    assert isinstance(player_data.date_created, datetime)
    assert isinstance(player_data.date_last_played, datetime)


def test_add_full_player(db_handler):
    today = datetime.utcnow()
    three_days_ago = today - timedelta(days=3)
    player_id = uuid4()
    full_player_creation = dc.Player(username='all_data_user',
                                     player_id=player_id,
                                     date_created=three_days_ago,
                                     date_last_played=today)
    db_handler.add_full_player(full_player_creation)
    player_data = db_handler.get_player_by_username(full_player_creation)
    assert full_player_creation.username == player_data.username
    assert player_data.player_id == full_player_creation.player_id
    assert player_data.date_created == full_player_creation.date_created
    assert player_data.date_last_played == full_player_creation.date_last_played
    assert player_data.player_id == player_id
    assert isinstance(player_data.player_id, UUID)
    assert isinstance(player_data.date_created, datetime)
    assert isinstance(player_data.date_last_played, datetime)


def test_update_player_last_played(db_handler, player):
    old_data = db_handler.get_player_by_username(player)
    db_handler._update_player_last_played(player)
    new_data = db_handler.get_player_by_username(player)
    assert player.date_last_played < new_data.date_last_played
    assert old_data.date_last_played < new_data.date_last_played


def test_get_player_by_username(db_handler, player):
    """
    Tests SELECTing a player by their username from players Table
    """
    player_data = db_handler.get_player_by_username(player)
    assert player.username == player_data.username


def test_add_game(db_handler, player):
    """
    Tests adding Game to the games Table
    """
    player_data = db_handler.get_player_by_username(player)
    game = dc.Game(player_id=player.player_id, score=10, round=1)
    db_handler.add_game(game)
    # Add assertions for the added game


def test_add_movie(db_handler, movie_1, movie_2):
    """
    Tests adding a new Movie to the movies Table
    """
    for movie in [movie_1, movie_2]:
        db_handler.add_movie(movie)
        movie_from_db = db_handler.get_movie_by_imdb_id(movie.imdb_id)
        assert movie_from_db.title == movie.title
        assert movie_from_db.imdb_id == movie.imdb_id
        assert movie_from_db.release_year == movie.release_year
        assert movie_from_db.stripped_title == movie.stripped_title


def test_get_movie_by_movie_id(db_handler, movie_1, movie_2):
    """
    Tests getting a Movie from the movies Table by a movie_id
    """
    for movie in [movie_1, movie_2]:
        movie_from_db = db_handler.get_movie_by_imdb_id(movie.imdb_id)
        assert movie_from_db.title == movie.title
        assert movie_from_db.imdb_id == movie.imdb_id
        assert movie_from_db.release_year == movie.release_year
        assert movie_from_db.stripped_title == movie.stripped_title


def test_add_clue(db_handler, movie_1):
    """
    Tests creating a new clue for a target movie in the clues Table
    """
    movie_from_db = db_handler.get_movie_by_imdb_id(movie_1.imdb_id)
    assert movie_from_db
    clue = dc.Clue(movie_id=movie_from_db.movie_id,
                   category_id=1, clue_text='Test clue', spoiler=False,
                   date_created=datetime.utcnow())
    db_handler.add_clue(clue)
    clues_from_db = db_handler.get_clues_by_movie_id(movie_from_db.movie_id)
    assert any([clue_from_db.clue_text == clue.clue_text for clue_from_db in
                clues_from_db])

def test_get_clues_by_movie_id(db_handler, movie_1):
    clues = db_handler.get_clues_by_movie_id(movie_1.movie_id)
    assert isinstance(clues, list)
    for clue in clues:
        assert isinstance(clue, dc.Clue)

def test_get_categories(db_handler):
    """
    Tests getting the categories dictionary
    """
    categories = db_handler.get_categories()
    assert categories == DEFAULT_CATEGORIES
    assert len(categories) == len(DEFAULT_CATEGORIES)

