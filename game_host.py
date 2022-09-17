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

    def __init__(self, mongo_url, player_id=None, game_instance=None):
        self.player_id = player_id or str(uuid.uuid4())
        self.game_instance = game_instance or str(uuid.uuid4())
        self.game_inst_query = {'game_instance': self.game_instance,
                           'player_id': self.player_id}
        self.__client = MongoClient(mongo_url)
        db = self.__client['imdb']
        self.movie_db = db['movies']
        self.game_db = db['games']
        self.player_db = db['players']
        self.played_movies = []
        self.rounds = []

    def _create_new_game(self):
        self.game_db.insert_one(self.game_inst_query)
        # self.player_db.update_one({'player_id': self.player_id, {'$push': {'games': self.game_instance}}})

    def _get_three_movie_options(self):
        """
        Queries MongoDB for 3 random movies documents (doc_id, year)
        :return:
        """
        query_pipeline = [
            {'$project': {'_id': 1, 'year': 1}},
            {'$match': {'_id': {'$nin': self.played_movies}}},
            {'$sample': {'size': 3}}
        ]
        results = [choice for choice in self.movie_db.aggregate(query_pipeline)]
        self.game_db.update_one(self.game_inst_query, {
            '$push': {'rounds': [{'round': 1, 'choices': results}]}})
        return results

    def get_movie(self, doc_id):
        """
        Queries a movie document from mongodb.movies by the doc_id
        :param doc_id:
        :return:
        """
        filter = {'_id': ObjectId(doc_id)}
        movie = self.movie_db.find_one(filter)
        self.game_db.update_one(self.game_inst_query, {
            '$push': {'movies': {'id': movie['_id'], 'ts': datetime.utcnow()}}
        })
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


if __name__ == '__main__':
    host = GameHost(os.getenv('MONGO_URL'), )
    win = False
    choices = host._get_three_movie_options()
    print(f'Please select a year:')
    for idx, year in enumerate(choices):
        display_choice = idx + 1
        print(f'({display_choice}) {year["year"]}')
    choice: int = int(input('> ')) - 1
    movie = host.get_movie(choices[choice]['_id'])
    host.get_clues_from_movie(movie)
    ignored_words = ['the', 'a']
    print(f"****ANSWER: '{movie['title']}' {movie['year']}  *****")
    for idx, clue in enumerate(host.rounds[0]['clues']):
        print(f'This warning is in the {clue["category"]} category:\n')
        print(f'For {clue["points"]} points...\n')
        print(clue['text'])
        true_answer = ''.join(e for e in movie['title'].lower() if e.isalnum())
        player_answer = ''.join(
            e for e in input('Guess a movie > ').lower() if e.isalnum())
        print(f'{true_answer}\n{player_answer}')
        if player_answer == true_answer:
            print(f'you win {clue["points"]} points!')
            win = True
            break
        else:
            print(f'WRONG!')
    if not win:
        print('You lose, loser!')
    else:
        print('Winner Winner, Chicken Dinner!')