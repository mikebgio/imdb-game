"""
Tests for imdb_game.gameshow module.
"""
import pytest
from imdb_game.gameshow.game import GameShowHost
from imdb_game.database.dataclasses import Game, Player, Round, Clue, Movie
from imdb_game.database.handler import DBHandler
from test_tools import init_test_db
from uuid import uuid4, UUID
import testing.postgresql

PLAYER_ID = uuid4()


@pytest.fixture(scope="module")
def db_handler():
    """
    Fixture for creating a database handler.
    """
    with testing.postgresql.Postgresql() as postgresql:
        global TEST_DB_URL
        TEST_DB_URL = postgresql.url()
        connection = init_test_db(postgresql)
        db_handler = DBHandler(pg_url=postgresql.url())
        yield db_handler


@pytest.fixture(scope="module")
def player():
    """
    Fixture for creating a player.
    """
    yield Player(username="test_player", player_id=PLAYER_ID)


def test_gameshowhost_create(db_handler, player):
    """
    Test creating a gameshow host.
    """
    host = GameShowHost(player_instance=player, database=db_handler)
    assert host.DB == db_handler
    assert isinstance(host.game, Game)
    assert isinstance(host.player, Player)
    assert isinstance(host.ID, UUID)
    assert host.player.player_id == PLAYER_ID
