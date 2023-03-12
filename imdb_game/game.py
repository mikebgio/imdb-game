"""
GameHost class
"""
import os
from datetime import datetime
import random
import uuid
from imdb_dataclasses import Game, Player, Clue, Movie
from database import DBHandler


class Tooch:
    game: Game
    player: Player
    db: DBHandler = DBHandler()
    id = uuid.uuid4()

    def __init__(self, player_instance: Player, game_instance: Game):
        self.categories = self.db.get_categories()
        self.player = player_instance
        self.game = game_instance

    def get_three_years(self):
        """
        Get data to populate the Choose A Year Screen of the game
        """
        years = self.db.get_three_movie_options()
        print(years)
        return years

    def get_clues_for_movie_choice(self, choice: dict):
        clues = self.db.get_clues_by_movie_id(choice['movie_id'])
        return clues

    def announce_category_name(self, clue_number: str, clue: Clue):
        category = [cat['display_name'] for cat in self.categories if
                cat['category_id'] == clue.category_id][0]
        print(f'The {clue_number} clue is in the {category} category...')

def main():
    """
    Run for CLI play testing
    """
    player = Player(username='mike', player_id=uuid.uuid4())
    game = Game(player_id=player.player_id)
    tooch = Tooch(player, game)
    print(f'Categories are {tooch.categories}')

    choices = tooch.get_three_years()
    years = ', '.join([str(year['release_year']) for year in choices])
    player_choice = input(f"Select from the following Years:\n{years}\n> ")
    chosen_movie = [movie for movie in choices if
                    movie['release_year'] == int(player_choice)][0]
    print(chosen_movie)
    clues = tooch.get_clues_for_movie_choice(chosen_movie)
    first_clue = random.choice(clues)
    tooch.announce_category_name('first', first_clue)
    print(first_clue.clue_text)


if __name__ == '__main__':
    main()

