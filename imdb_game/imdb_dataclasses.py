import random
from dataclasses import dataclass, field
from datetime import datetime
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
        """
        Returns the imdb.com URL for the Movie
        """
        return f'{IMDB_ROOT}/title/{self.imdb_id}'


@dataclass
class Clue:
    """
    Represents an IMDb user-submitted Parental Warning to be used as a clue for
    IMDb Game
    """
    movie_id: UUID
    category_id: int
    clue_text: str
    spoiler: bool
    date_created: datetime
    clue_id: UUID = None


@dataclass
class Player:
    """
    Represents a human player of IMDb Game
    """
    username: str
    player_id: UUID = None


@dataclass
class Round:
    """
    Dataclass for a single round of IMDb Game, contains Movie and Clues,
    as well as delivers random clues, and tracks clue point weight
    """
    round_number: int
    current_movie: Movie
    clues_pool: list[Clue] = field(default_factory=list)
    clues_played: list[Clue] = field(default_factory=list)
    current_clue_number: int = 0
    total_clues: int = 5

    def increment_clue_number(self):
        """
        Increases the clue number by 1
        """
        self.current_clue_number += 1

    def get_clue_number(self):
        """
        Returns the current clue number, 1-indexed
        """
        return self.current_clue_number + 1

    def get_random_clue(self):
        """
        Returns a random clue from the clues_pool. Does not account for
        difficulty yet
        """
        clue = random.choice(self.clues_pool)
        self.clues_pool.remove(clue)
        self.clues_played.append(clue)
        return clue

    def get_current_points(self):
        """
        Returns the points value of a correct answer based on current clue count
        """
        return self.total_clues - self.current_clue_number

    def remove_clues_with_movie_title(self):
        """
        Filter out Clue objects that contain the movie_title in their clue_text
        """
        filtered_clues = [clue for clue in self.clues_pool if
                          self.current_movie.title not in clue.clue_text]
        self.clues_pool = filtered_clues


@dataclass
class Game:
    """
    Object containing a single game metrics and statistics
    """
    player_id: UUID
    score: int = 0
    round: int = 0
    start_time: datetime = datetime.utcnow()
    end_time: datetime = None
    game_id: UUID = None
    current_round: Round = None
    MAX_ROUNDS: int = 5
    GAME_OVER: bool = False

    # rounds: list = field(default_factory=list)

    def increment_round(self):
        """
        Increases the round count by 1 and checks to see if the game has ended.
        If the game is over, set GAME_OVER to True and record the game end time.
        """
        self.round += 1
        if self.round > self.MAX_ROUNDS:
            self.GAME_OVER = True
            self.end_time = datetime.utcnow()

    def increment_score(self, points: int):
        """
        Increase player's score by input points
        """
        self.score += points

    def decrement_score(self, points):
        """
        Reduces score by input points
        """
        self.score -= points

    def get_round(self) -> int:
        """
        Returns the current round number, 1-indexed
        """
        return self.round + 1

    def report_score(self):
        """
        Pretty print the player's current score in console
        """
        print(f'Your current score is: {self.score}')
