from setuptools import setup

setup(
    name='imdb-game',
    version='0.9.0',
    packages=['flask_app', 'imdb_game', 'imdb_game.utils', 'imdb_game.scraper',
              'imdb_game.database', 'imdb_game.gameshow',
              'imdb_game.healthcheck'],
    url='https://github.com/mikebgio/imdb-game',
    license='',
    author='Michael Giordano',
    author_email='michaelbgiordano@gmail.com',
    description='Web version of Nick Martucci\'s Inappropriate Movie Database Game Show'
)
