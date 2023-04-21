from flask import Flask, render_template
from imdb_game.game import GameShowHost
from imdb_game.imdb_dataclasses import Player

app = Flask(__name__, template_folder="templates")
player = Player('mike')
host = GameShowHost(player)


@app.route('/')
def home():
    """
    Display Home Page.
    :return: rendered home.html template.
    """
    return render_template('home.html', name='Nick Martucci')


@app.route('/game')
def game():
    """
    Display Game Page.
    :return: rendered game.html template.
    """
    options = host.get_three_years()
    return render_template('game.html', choices=options)


@app.route('/movie/<movie_id>')
def select_movie(movie_id):
    print(movie_id)
    # movie = host.DB.get_movie_by_movie_id(movie_id)
    obj = host.web_start_round()
    print(obj)
    return render_template('movie.html',
                           current_clue=obj['clue_text'])


# Todo:
#   - add clues route/page with text box for player input and submit button
#   - add functionality for win/loss of each round
#   - add functionality for playing a five round game that reveals a final score


if __name__ == "__main__":
    app.run()
