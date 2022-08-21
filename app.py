import os

from flask import Flask, render_template, request
import game_host

from pprint import pprint

app = Flask(__name__)
host = game_host.GameHost(os.getenv('MONGO_URL'))


@app.route('/')
def home():
    return render_template('home.html', name='Nick Martucci')


@app.route('/game')
def game():
    game_rounds = range(1, 6)
    game_round_num = game_rounds[0]
    choices = host._get_three_movie_options()
    return render_template('game.html',
                           game_round_num=game_round_num,
                           choices=)


if __name__ == "__main__":
    app.run(debug=True)
