import pytest
from uuid import UUID
import imdb_game.database._dataclasses as dc
from datetime import datetime
from uuid import UUID, uuid4

@pytest.fixture(scope='module')
def player():
    new_player = dc.Player(username='test_player_name',
                           player_id=uuid4(),
                           date_created=datetime.now())
    yield new_player

def test_player_dict(player):
    pdict = player.dict()
    assert isinstance(pdict, dict)
    assert pdict['username'] == player.username
    assert pdict['player_id'] == player.player_id
    assert pdict['date_created'] == player.date_created