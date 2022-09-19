import os
import sys
import uuid
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime
import random
import re


class GameHost:
    """
    Runs an instance of the IMDb Game by selecting and returning movies and
    clues while also tracking the status of an individual game
    """

    def __init__(self, mongo_url: str = "mongodb://mongo:27017",
                 player_id: str = None, game_instance=None):
        self.mongo = DB(mongo_url)
        this_player_id = player_id or str(uuid.uuid4())
        self.player = Player(this_player_id)
        this_game_id = game_instance or str(uuid.uuid4())
        self.game = Game(this_game_id)
        self.game_inst_query = {'game_instance': self.game.id,
                                'player_id': self.player.id}

        self.played_movies = []
        self.rounds = []
        self.current_round = None and self._set_current_round()
        self._create_new_game()

    def _set_player_data(self):
        player_data = self.mongo.get_player(self.player.id)
        self.player.set_player_data(player_data)

    def _set_current_round(self):
        self.current_round = len(self.rounds) + 1

    def _create_new_game(self):
        self.mongo.games.insert_one(self.game_inst_query)
        self.mongo.players.update_one({'player_id': self.player.id},
                                      {'$push': {'games': self.game.id}})

    def _get_three_movie_options(self):
        # TODO: This should probably move to DB class
        """
        Queries MongoDB for 3 random movies documents (doc_id, year)
        :return:
        """
        query_pipeline = [
            {'$project': {'_id': 1, 'year': 1}},
            {'$match': {'_id': {'$nin': self.played_movies}}},
            {'$sample': {'size': 3}}
        ]
        results = [choice for choice in self.mongo.movies.aggregate(query_pipeline)]
        self.mongo.games.update_one(self.game_inst_query, {
            '$push': {'rounds': [{'round': 1, 'choices': results}]}})
        return results

    def get_movie(self, doc_id):
        """
        Queries a movie document from mongodb.movies by the doc_id
        :param doc_id:
        :return:
        """
        filter = {'_id': ObjectId(doc_id)}
        movie = self.mongo.movies.find_one(filter)
        game_update = {'$push': {'movies':
                                     {'id': movie['_id'],
                                      'ts': datetime.utcnow()}}}
        self.mongo.games.update_one(self.game_inst_query, game_update)
        self.played_movies.append(movie['_id'])
        current_round = len(self.rounds) + 1
        self.rounds.append(
            {'round': current_round, 'movie_id': movie['_id']})
        return movie

    def get_clues_from_movie(self, movie):
        """
        Generates list of 5 clues to be revealed to player
        :param movie:
        :return:
        """
        clues = random.sample(movie['clues'], 5)
        # Temp method until clues are properly ranked
        self._assign_points(clues)
        for round in self.rounds:
            if round['movie_id'] == movie['_id']:
                round['clues'] = clues

    def _assign_points(self, clues: list):
        """
        Temp method until clues are properly ranked
        """
        points = 5
        for clue in clues:
            clue['points']: int = points
            points -= 1

    def _register_guess(self, guess):
        pass

    def verify_answer(self, movie_obj: dict, guess: str):
        true_answer = ''.join(
            e for e in movie_obj['title'].lower() if e.isalnum())
        player_answer = ''.join(
            e for e in guess.lower() if e.isalnum())
        print(f'{true_answer}\n{player_answer}')
        if player_answer == true_answer:
            return True
        else:
            return False


class Player:
    def __init__(self, player_id: str = None):
        self.id = player_id or str(uuid.uuid4())

    def set_player_data(self, data: dict):
        self.info = data


class Game:
    def __init__(self, game_id: str = None):
        self.id = game_id or str(uuid.uuid4())

    def _is_game_new(self):
        pass


class DB:
    def __init__(self, mongo_url: str = "mongodb://mongo:27017"):
        client = MongoClient(mongo_url)
        db = client['imdb']
        self.movies = db['movies']
        self.games = db['games']
        self.players = db['players']
        self.current_player = None
        self.current_game = None
        self.current_movie = None

    def create_player(self, player_id):
        player = {
            'player_id': player_id,
            'date_created': datetime.utcnow().isoformat(),
            'games_played': 1,
            'cookies': []  # TODO: Figure out how cookies work
        }
        self.players.insert_one(player)
        return player

    def get_player(self, player_id: str):
        """
        Gets player object from MongoDB OR creates and writes new player to
        MongoDB and returns that dict
        :param player_id:
        :return: dict
        """
        cur = self.players.find({'player_id': player_id})
        docs = [c for c in cur]
        if len(docs) == 1:
            return docs[0]
        elif len(docs) == 0:
            print(f'New player {player_id} must be created.')
            return self.create_player(player_id)
        else:
            print(f'Something is wrong\ndocs: {docs}')
            sys.exit(100)

    def create_game(self, game_id: str, ):
        """
        creates new game object in
        :param game_id:
        :param player_id:
        :return:
        """
        game = {
            'game_id': game_id,
            'date_started': datetime.utcnow().isoformat(),
            'player_id': player_id,

        }
        self.games.insert_one(game)
        return game

    def get_game(self, player_id):
        pass

    def write_guess_to_game(self, guess):
        pass

    def get_previous_movies(self):
        pass


# Todo:
#   - add scoring system (Game() stores it, GameHost() changes it)
#   - - points based on clue count (5 points at clue 1, 1 point at clue 5)
#   - - Lose 1 point for guessing wrong once each round
#   - add guessing timer (30 seconds per clue? 15?)
if __name__ == '__main__':
    host = GameHost(os.getenv('MONGO_URL'), player_id='mgiordano', )
    win = False
    choices = host._get_three_movie_options()
    print(f'Please select a year:')
    for idx, year in enumerate(choices):
        display_choice = idx + 1
        print(f'({display_choice}) {year["year"]}')
    choice: int = int(input('> ')) - 1
    movie = host.get_movie(choices[choice]['_id'])
    host.get_clues_from_movie(movie)
    print(f"****ANSWER: '{movie['title']}' {movie['year']}  *****")
    for idx, clue in enumerate(host.rounds[0]['clues']):
        print(f'This warning is in the {clue["category"]} category:\n')
        print(f'For {clue["points"]} points...\n')
        print(clue['text'])
        player_guess = input('Guess a movie > ').lower()
        host.verify_answer(movie, player_guess)

    if not win:
        print('You lose, loser!')
    else:
        print('Winner Winner, Chicken Dinner!')
