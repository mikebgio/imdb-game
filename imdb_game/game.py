"""
GameShowHost class
"""
from uuid import UUID, uuid4

from database import DBHandler
from imdb_dataclasses import Clue, Game, Player, Round
from utils import justify_text, strip_text


class GameShowHost:
    """
    The "game show host" class of the IMDb Game. Controls functions for playing
    a game of IMDb. Currently only for running in the console.
    Args:
        player_instance (Player): The player object for the current game
        game_instance (Game): The game object for the current game
    """
    DB: DBHandler = DBHandler()
    ID: UUID = uuid4()
    WRONG_ANSWER_DEDUCTION: int = 1
    PROMPT: str = '=> '

    def __init__(self, player_instance: Player,
                 game_instance: Game = None):
        self.categories = self.DB.get_categories()
        self.player: Player = player_instance
        self.game: Game = game_instance or Game(
            player_id=player_instance.player_id)
        self._greet_player()

    def _get_three_years(self) -> list[dict]:
        """
        Get data to populate the Choose A Year Screen of the game
        :return: list[dict] - list of movie data
        """
        return self.DB.get_three_movie_options()

    def prompt_user_for_year_choice(self) -> dict:
        """
        Gets three random movie IDs and years and then presents the years to the
        player in a prompt, waiting for the user choice.
        :return: dict - {movie_id, movie_year}
        """
        choices = self._get_three_years()
        years = [str(year['release_year']) for year in choices]
        years_print = ', '.join(years)
        chosen_movie = None
        while True:
            try:
                player_choice = input(f"Select from the following "
                                      f"Years:\n{years_print}\n{self.PROMPT}")
                if player_choice not in years:
                    print(
                        "Invalid selection. Please choose one of the "
                        "available years.")
                else:
                    chosen_movie = [movie for movie in choices if
                                    movie['release_year'] == int(
                                        player_choice)][0]
                    break

            except ValueError:
                print("Invalid input. Please enter a valid year.")
        return chosen_movie

    def __setup_current_round(self, chosen_movie: dict):
        """
        Creates a Round object that tracks clues played for a round
        Args:
            chosen_movie (dict): The movie data for the chosen movie
        Returns:
            None
        """
        movie = self.DB.get_movie_by_movie_id(chosen_movie['movie_id'])
        self.game.current_round = Round(self.game.round, movie)
        self.__set_clues_for_current_movie_choice()

    def __set_clues_for_current_movie_choice(self):
        """
        Accepts a player movie choice dict and requests all clues associated
        with the movie
        :return: list[dict] - list of clue objects
        """
        self.game.current_round.clues_pool = self.DB.get_clues_by_movie_id(
            self.game.current_round.current_movie.movie_id)

    def _announce_category_name(self, clue: Clue):
        """
        Print console message to player to say what kind of warning the clue is
        intended to convey
        """
        category = [cat['display_name'] for cat in self.categories if
                    cat['category_id'] == clue.category_id][0]
        print(f'Clue number {self.game.current_round.get_clue_number()} is in'
              f' the {category} category...\n')

    def _announce_categories(self):
        """
        Print console message to announce all possible categories and indicate
        connection to database
        """
        print('Our categories for tonight are...')
        for category in self.categories:
            print(f"\t{category['display_name']}")

    def _greet_player(self):
        """
        Print console message to start game and indicate proper initialization
        """
        print(f'\n***Hello there {self.player.username}! Welcome to the '
              f'Inappropriate Movie Database!***\n\n')

    def _evaluate_guess(self, guess) -> str:
        """
        Takes a player's guess text and decides whether it matches the title of
        the round's movie or not.
        """
        if strip_text(
                guess) == self.game.current_round.current_movie.stripped_title:
            return self._player_answer_correct()
        if strip_text(guess) == '/pass':
            return self._player_skip()
        else:
            return self._player_answer_wrong(guess)

    def _next_round(self) -> str:
        """
        Advances the game to the next round by increasing the round count and
        returns the 'next_round' action.
        """
        self.game.increment_round()
        return 'next_round'

    def _next_clue(self) -> str:
        """
        Increase Round.current_clue_number and return 'next_clue' as action.
        """
        self.game.current_round.increment_clue_number()
        return 'next_clue'

    def present_clue(self):
        """
        Get a random clue from Round.clues_pool and pretty print to the console
        """
        clue = self.game.current_round.get_random_clue()
        self._announce_category_name(clue)
        print(justify_text(clue.clue_text, 80))

    def _player_answer_correct(self):
        """
        Actions to execute when the player answers correctly: increasing score
        by the amount of points per current clue number
        returns _next_round() actions
        """
        print(f'CORRECT: +{self.game.current_round.get_current_points()}')
        self.game.increment_score(self.game.current_round.get_current_points())
        return self._next_round()

    def _player_answer_wrong(self, guess):
        """
        Actions to execute when the player answers incorrectly: decreasing score
        by the default point decrement amount (self.WRONG_ANSWER_DEDUCTION)
        returns _next_clue() actions
        """
        print(f'WRONG: -{self.WRONG_ANSWER_DEDUCTION}')
        self.game.decrement_score(self.WRONG_ANSWER_DEDUCTION)
        return self._next_clue()

    def _player_skip(self) -> str:
        """
        Returns _next_clue() actions without changing score
        """
        print("Okay, let's try the next clue, then!")
        return self._next_clue()

    def _get_player_guess(self) -> str:
        """
        Prompt player to input a text guess in console, returns guess text
        """
        player_guess = None
        try:
            player_guess = input(self.PROMPT)
        except ValueError as error:
            print(error)
        return player_guess

    def game_loop(self):
        """
        Runs through the gameplay loop of IMDb Game. Will go until
        Game.MAX_ROUNDS is met and Game.GAME_OVER is true.
        """
        next_action = 'next_round'
        while not self.game.GAME_OVER:
            if next_action == 'next_round':
                player_movie_choice = self.prompt_user_for_year_choice()
                self.__setup_current_round(player_movie_choice)
                self.present_clue()
            elif next_action == 'next_clue':
                self.present_clue()
            guess = self._get_player_guess()
            next_action = self._evaluate_guess(guess)
            self.game.report_score()
        print('GAME OVER')
        print(f'Final Score: {self.game.score}')


def main():
    """
    Run for CLI play testing
    """
    player = Player(username='mike',
                    player_id=UUID('507343e5-8790-4732-adf0-b3349e14e460'))
    game_show_host = GameShowHost(player)
    game_show_host.game_loop()


if __name__ == '__main__':
    main()
