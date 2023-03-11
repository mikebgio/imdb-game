from datetime import datetime
from dataclasses import dataclass, asdict
from uuid import UUID
from utils import IMDB_ROOT


@dataclass
class Movie:
    """
    SELECT imdb_id, title, stripped_title, release_year, imdb_id
    """
    imdb_id: UUID
    title: str
    stripped_title: str
    release_year: int
    movie_id: UUID = None

    def get_link(self):
        return f'{IMDB_ROOT}/title/{self.imdb_id}'

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}

@dataclass
class Clue:
    movie_id: UUID
    category_id: int
    clue_text: str
    spoiler: bool
    clue_id: UUID = None

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}


@dataclass
class Player:
    username: str
    player_id: UUID = None

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}

@dataclass
class Game:
    player_id: UUID
    score: int
    round: int
    start_time: datetime
    end_time: datetime = None
    game_id: UUID = None
    MAX_ROUNDS: int = 5
    rounds: list = []

    def dict(self):
        return {k: str(v) for k, v in asdict(self).items()}