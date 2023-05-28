import pytest
import imdb_game.database.dataclasses as dc
from datetime import datetime
from uuid import UUID, uuid4
from imdb_game.utils.utils import strip_text, IMDB_ROOT


@pytest.fixture(scope='module')
def player():
    new_player = dc.Player(username='test_player_name',
                           player_id=uuid4(),
                           date_created=datetime.utcnow())
    yield new_player


@pytest.fixture(scope="module")
def movie():
    title = 'The Test Movie: Redemption 2: In the Heat of the CPU'
    movie = dc.Movie(
        imdb_id='ttXX789XX',
        title=title,
        stripped_title=strip_text(title),
        release_year=1984
    )
    yield movie


@pytest.fixture(scope="module")
def clue(movie):
    clue = dc.Clue(movie_id=movie.movie_id,
                   category_id=1,
                   clue_text="This movie contains many naughty words.",
                   spoiler=False,
                   date_created=datetime.utcnow(),
                   clue_id=uuid4())
    yield clue


@pytest.fixture(scope="module")
def game(player):
    game = dc.Game(player_id=player.player_id)
    yield game


@pytest.fixture(scope="module")
def round(game, movie):
    new_round = dc.Round(round_number=1,
                         current_movie=movie,
                         game_id=game.game_id)
    yield new_round


def test_create_player():
    username = 'test_username_1'
    new_player = dc.Player(username)
    assert isinstance(new_player, dc.Player)
    assert new_player.username == username


def test_player_dict(player):
    pdict = player.dict()
    assert isinstance(pdict, dict)
    assert pdict['username'] == player.username
    assert pdict['player_id'] == player.player_id
    assert pdict['date_created'] == player.date_created


def test_create_movie(movie):
    assert isinstance(movie, dc.Movie)
    title = 'El Tést Mövîe: El Niño'
    movie_2 = dc.Movie(
        imdb_id='ttXX608XX',
        title=title,
        stripped_title=strip_text(title),
        release_year=1945
    )
    assert isinstance(movie_2, dc.Movie)


def test_movie_dict(movie):
    mdict = movie.dict()
    assert isinstance(mdict, dict)
    assert mdict['imdb_id'] == movie.imdb_id
    assert mdict['title'] == movie.title
    assert mdict['stripped_title'] == movie.stripped_title
    assert mdict['release_year'] == movie.release_year


def test_movie_get_link(movie):
    link = movie.get_link()
    assert link == f'https://www.imdb.com/title/{movie.imdb_id}'
    assert link == f'{IMDB_ROOT}/title/{movie.imdb_id}'


def test_create_clue(movie):
    clue = dc.Clue(movie_id=movie.movie_id,
                   category_id=1,
                   clue_text="This movie contains many naughty words.",
                   spoiler=False,
                   date_created=datetime.utcnow(),
                   clue_id=uuid4())
    assert isinstance(clue, dc.Clue)
    clue_2 = dc.Clue(movie_id=movie.movie_id,
                     category_id=3,
                     clue_text="This movie contains many inappropriate scenes.",
                     spoiler=True,
                     date_created=datetime.utcnow())
    assert isinstance(clue_2, dc.Clue)


def test_clue_dict(clue):
    cdict = clue.dict()
    assert isinstance(cdict, dict)
    assert cdict['movie_id'] == clue.movie_id
    assert cdict['category_id'] == clue.category_id
    assert cdict['clue_text'] == clue.clue_text
    assert cdict['spoiler'] == clue.spoiler
    assert cdict['date_created'] == clue.date_created
    assert cdict['clue_id'] == clue.clue_id


def test_create_game(game, player):
    assert isinstance(game, dc.Game)
    game_2 = dc.Game(player_id=player.player_id)
    assert isinstance(game_2, dc.Game)


def test_game_dict(game):
    gdict = game.dict()
    assert isinstance(gdict, dict)
    assert gdict['game_id'] == game.game_id
    assert gdict['player_id'] == game.player_id
    assert gdict['score'] == game.score
    assert gdict['start_time'] == game.start_time
    assert gdict['end_time'] == game.end_time
    assert gdict['start_time'] == game.start_time
    assert gdict['GAME_OVER'] == game.GAME_OVER


def test_game_increment_round(game):
    start_round = game.round
    game.increment_round()
    next_round = game.round
    assert start_round < next_round
    assert start_round != next_round
    assert start_round + 1 == next_round


def test_game_increment_score(game):
    start_score = game.score
    first_points_change = 5
    second_points_change = 3
    third_points_change = -1
    game.increment_score(first_points_change)
    first_score = game.score
    game.increment_score(second_points_change)
    second_score = game.score
    assert start_score < first_score
    assert start_score < second_score
    assert first_score < second_score
    assert start_score + first_points_change == first_score
    assert first_score + second_points_change == second_score
    assert start_score + first_points_change + second_points_change ==\
           game.score
    # Validate it also works with negative numbers
    game.increment_score(third_points_change)
    third_score = game.score
    assert third_score < second_score
    assert third_score > first_score
    assert third_score > start_score
    assert second_score + third_points_change == third_score
    assert second_score - 1 == third_score

def test_game_decrement_score(game):
    start_score = game.score
    first_score_change = 1
    game.decrement_score(first_score_change)
    new_score = game.score
    assert start_score > new_score
    assert start_score - 1 == new_score

def test_game_get_round(game):
    round = game.get_round()
    assert isinstance(round, int)
    assert game.round + 1 == round

def test_game_report_score(game):
    score = game.report_score()
    assert score == game.score


def test_create_round(round, game, movie):
    assert isinstance(round, dc.Round)
    new_round = dc.Round(
        round_number=2,
        current_movie=movie,
        game_id=game.game_id
    )
    assert isinstance(new_round, dc.Round)
    assert new_round.round_number == 2
    assert new_round.current_movie == movie
    assert new_round.game_id == game.game_id


def test_round_dict(round):
    rdict = round.dict()
    assert isinstance(rdict, dict)
    assert rdict['round_number'] == round.round_number
    assert rdict['current_movie'] == round.current_movie.dict()
    assert rdict['clues_pool'] == round.clues_pool
    assert rdict['clues_played'] == round.clues_played
    assert rdict['current_clue_number'] == round.current_clue_number
    assert rdict['total_clues'] == round.total_clues
