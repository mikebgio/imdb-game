import os
import random
from flask import Flask, render_template, request
import game_host
import uuid

from pprint import pprint

app = Flask(__name__, template_folder="templates")
host = game_host.GameHost(os.getenv('MONGO_URL'))


@app.route('/')
def home():
    return render_template('home.html', name='Nick Martucci')


@app.route('/game')
def game():
    game_rounds = range(1, 6)
    game_round_num = game_rounds[0]
    choices = [choice for choice in host._get_three_movie_options()]
    print(choices)
    return render_template('game.html',
                           game_round_num=game_round_num,
                           choices=choices)


@app.route('/movie/<movie_id>')
def select_movie(movie_id):
    movie = host.get_movie(movie_id)

    return render_template('movie.html', current_category=cat_title,
                           current_clue=current_clue['text'])




if __name__ == "__main__":
    app.run(debug=True)
