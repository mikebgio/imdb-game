import os

from bson.objectid import ObjectId
from pymongo import MongoClient


class GameHost:
    """
    Runs an instance of the IMDb Game by selecting and returning movies and
    clues while also tracking the status of an individual game
    """

    def __init__(self, mongo_url):
        self.client = MongoClient(mongo_url)
        db = self.client['imdb']
        self.movie_db = db['movies']
        self.game_db = db['games']
        self.played_movies = []

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
        print(query_pipeline)
        return self.movie_db.aggregate(query_pipeline)

    def get_movie(self, doc_id):
        """
        Queries a movie document from mongodb.movies by the doc_id
        :param doc_id:
        :return:
        """
        filter = {'_id': doc_id}
        return self.movie_db.find_one(filter)

    def get_clue(self, movie, points_weight):
        """
        Using the current movie document in play, picks a random clue from the
        warnings object based on the weight of the current clue
        (NOTE: clues are not yet weighted)
        :param movie:
        :param points_weight:
        :return:
        """


if __name__ == '__main__':
    host = GameHost(os.getenv('MONGO_URL'))
    choices = host._get_three_movie_options()
    for choice in choices:
        print(choice)
        print(f"{choice['year']} --- {choice['_id']}")
