"""
Functions for scraping imdb.com for movie clues
"""
import urllib.parse
import requests
from bs4 import BeautifulSoup
from database import DBHandler
from utils import strip_text, IMDB_ROOT
from imdb_dataclasses import Movie, Clue
import argparse


def clean_whitespace(text: str):
    """
    Removes whitespace from text
    """
    warning_whitespace = ' ' * 24
    return text.replace('\n', '').replace(warning_whitespace, '').strip()


def load_webpage(url: str):
    """
    Returns a BeautifulSoup object for the provided url.
    If the url is invalid, returns None.
    """
    try:
        response = requests.get(url)
        return BeautifulSoup(response.text, "html.parser")
    except requests.exceptions.RequestException:
        return None


def create_clues_list(soup: BeautifulSoup, categories, movie_object: Movie):
    """
    Creates a list of Clue objects for the provided BeautifulSoup op
    """
    clues: list = []
    list_item = 'ipl-zebra-list__item'
    pfx = 'advisory-'
    for user_submission in soup.find_all(class_=list_item):
        text: str = clean_whitespace(user_submission.contents[0])
        if 'id' in user_submission.parent.parent.attrs:
            if user_submission.parent.parent.attrs['id'].lower() !=\
                    'certificates':
                tag = user_submission.parent.parent.attrs['id']
                cat_short_name = tag.replace(pfx, '')
                spoiler = False
                if 'spoiler' in cat_short_name:
                    spoiler = True
                    cat_short_name = cat_short_name.replace('spoiler-', '')
                category = [cat for cat in categories if
                            cat['short_name'] == cat_short_name]
                entry = Clue(
                    clue_text=text, spoiler=spoiler,
                    movie_id=movie_object.movie_id,
                    category_id=category[0]['category_id']
                )
                clues.append(entry)
    return clues


def search_imdb(search_term: str):
    results = []
    result_item_name = 'findResult'
    query = urllib.parse.quote(search_term)
    url = f'{IMDB_ROOT}/find?s=tt&q={query}'
    soup = load_webpage(url)
    for tag in soup.find_all(class_=result_item_name):
        results.append(tag.a['href'])
    return results


def get_title(url):
    """
    Returns the title of the movie at the provided url
    """
    print(f'Getting the title for {url}...')
    url = f'{IMDB_ROOT}{url}'
    print(url)
    soup = load_webpage(url)
    return soup.h1.text


def get_top_250_movies():
    """
    Generates a list of the IMDB top 250 movies as a list of Movie Objects
    """
    print('Loading the top 250 Movies to MongoDB...')
    soup = load_webpage(f'{IMDB_ROOT}/chart/top/')
    movies = []
    for tag in soup.find_all(class_='titleColumn'):
        movies.append(Movie(
            imdb_id=tag.a['href'].split('/')[-2], title=tag.a.text,
            stripped_title=strip_text(tag.a.text),
            release_year=int(tag.span.text.replace('(', '').replace(')', ''))
        ))
    return movies


def insert_movies(database_handler, movies: list[Movie]):
    """
    Populates the `movies` table with IMDb's top 250 Movies as a starter set
    """
    for movie in movies:
        movie_id = database_handler.add_movie(movie.dict())
        movie.movie_id = movie_id


def initial_setup():
    """
    Sets up a database with the top 250 movies and clues for each movie.
    This is usually for the first time the scraper is run.
    """
    db = DBHandler()
    movies = get_top_250_movies()
    insert_movies(db, movies)
    categories = db.get_categories()
    for movie in movies:
        parental_guide_link = f'{movie.get_link()}/parentalguide'
        soup_page = load_webpage(parental_guide_link)
        clues = create_clues_list(soup_page, categories, movie)
        for clue in clues:
            db.add_clue(clue.dict())
    del db


def get_args(override: list = None):
    """
    Parses the command line arguments
    """
    if override is None:
        override = []
    # """
    parser = argparse.ArgumentParser(
        prog='scraper',
        description='Scrapes IMDb')
    parser.add_argument('--initial-setup', '-S', dest='initial_setup',
                        action='store_true', default=False,
                        help='Generate movies and clues from the IMDB Top'
                             '250 Movies of All Time')
    # add and argument for verbose output
    parser.add_argument('--verbose', '-v', dest='verbose',
                        action='store_true', default=False,
                        help='Print verbose output')
    # arguments to change target database
    parser.add_argument('--database', '-d', dest='database',
                        default='imdb',
                        help='The name of the database to use')
    args = parser.parse_args(override)
    return args


def main():
    args = get_args()
    if args.initial_setup:
        initial_setup()


# Todo:
#     - add function to index cover art when scraping
if __name__ == '__main__':
    print('Let\'s get data!')
    main()
    print('done.')
