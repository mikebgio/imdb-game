import pytest
from uuid import UUID
from psycopg import connect
from psycopg.errors import UniqueViolation
from imdb_game.database import DBHandler
from imdb_game.imdb_dataclasses import Movie, Clue, Game, Player
from test_tools import init_test_db
import testing.postgresql
from datetime import datetime

TEST_MOVIE_1 = Movie(movie_id=UUID('12345678-1234-5678-1234-567812345678'),
              imdb_id='ttXX345XX', title='Test Movie',
              stripped_title='testmovie', release_year=1999)
TEST_MOVIE_2 = Movie(movie_id=UUID('12345678-1234-5678-1234-567888888888'),
              imdb_id='ttXX456XX', title='Test Movie 2: The Sequel',
              stripped_title='testmovie2thesequel', release_year=2013)

@pytest.fixture(scope="module")
def db_handler():
    with testing.postgresql.Postgresql() as postgresql:
        connection = init_test_db(postgresql)
        db_handler = DBHandler(pg_url=postgresql.url())
        yield db_handler


def test_add_player(db_handler):
    username = 'testuser'
    db_handler.add_player(username)
    player = db_handler.get_player_by_username(username)
    assert player.username == username


def test_get_player_by_username(db_handler):
    username = 'testuser'
    player = db_handler.get_player_by_username(username)
    assert player.username == username


def test_add_game(db_handler):
    player = db_handler.get_player_by_username('testuser')
    game = Game(player_id=player.player_id, score=10, round=1)
    db_handler.add_game(game)
    # Add assertions for the added game


def test_add_movie(db_handler):
    for movie in [TEST_MOVIE_1, TEST_MOVIE_2]:
        db_handler.add_movie(movie)
        movie_from_db = db_handler.get_movie_by_imdb_id(movie.imdb_id)
        assert movie_from_db.title == movie.title
        assert movie_from_db.imdb_id == movie.imdb_id
        assert movie_from_db.release_year == movie.release_year
        assert movie_from_db.stripped_title == movie.stripped_title


def test_add_clue(db_handler):
    movie_from_db = db_handler.get_movie_by_imdb_id(TEST_MOVIE_1.imdb_id)
    assert movie_from_db
    clue = Clue(movie_id=movie_from_db.movie_id,
                category_id=1, clue_text='Test clue', spoiler=False,
                date_created=datetime.now())
    clue_row = db_handler.add_clue(clue)
    print(clue_row)
    clues_from_db = db_handler.get_clues_by_movie_id(movie_from_db.movie_id)
    assert any([clue_from_db.clue_text == clue.clue_text for clue_from_db in
                clues_from_db])


def test_get_categories(db_handler):
    # categories = db_handler.connection.cursor().execute('SELECT * FROM categories').fetchall()
    default_categories = [{'category_id': 1, 'display_name': 'Sex & Nudity',
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
    categories = db_handler.get_categories()
    assert categories == default_categories
    assert len(categories) == len(default_categories)

# def test_get_movie_by_movie_id(db_handler):
#     movie_id = UUID('12345678123456781234567812345678')
#     movie = db_handler.get_movie_by_movie_id(movie_id)
#     assert movie.movie_id == movie_id

# def test_get_three_movie_options(db_handler):
#     movie_options =
