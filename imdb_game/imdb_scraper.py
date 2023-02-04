"""
Functions for scraping imdb.com for movie clues
"""
import urllib.parse
import os
import hashlib
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient

IMDB_ROOT = 'https://www.imdb.com'


def clean_whitespace(text):
    warning_whitespace = ' ' * 24
    return text.replace('\n', '').replace(warning_whitespace, '').strip()


def load_webpage(url):
    r = requests.get(url)
    return BeautifulSoup(r.text, "html.parser")


def create_warnings_object(soup, movie_meta: dict):
    # TODO: Make a version that utilizes Replit.DB
    categories = {'nudity': 'Sex & Nudity',
                  'violence': 'Violence & Gore',
                  'profanity': 'Profanity',
                  'alcohol': 'Alcohol, Drugs & Smoking',
                  'frightening': 'Frightening & Intense Scenes',
                  }
    movie = {
        'clues': []
    }
    movie = movie_meta | movie
    list_item = 'ipl-zebra-list__item'
    pfx = 'advisory-'
    for warning in soup.find_all(class_=list_item):
        text: str = clean_whitespace(warning.contents[0])
        if 'id' in warning.parent.parent.attrs:
            if warning.parent.parent.attrs['id'].lower() != 'certificates':
                tag = warning.parent.parent.attrs['id']
                key = tag.replace(pfx, '')
                spoiler = False
                if 'spoiler' in key:
                    spoiler = True
                    key = key.replace('spoiler-', '')
                entry = {'text': text, 'spoiler': spoiler, 'points': 0,
                         'id': hashlib.md5(text.encode()).hexdigest(),
                         'category': categories[key]}
                movie['clues'].append(entry)
    return movie


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
    soup = load_webpage(url)
    return soup.h1.text


def get_top_movie_links():
    print('Loading the top 250 Movies to MongoDB...')
    soup = load_webpage('https://www.imdb.com/chart/top/')
    movies = []
    for tag in soup.find_all(class_='titleColumn'):
        movies.append(
            {'imdb_id': tag.a['href'].split('/')[-2], 'title': tag.a.text,
             'link': tag.a['href'],
             'year': int(tag.span.text.replace('(', '').replace(')', ''))})
    return movies


def main():
    client = MongoClient(os.getenv('MONGO_URL'))
    db = client['imdb']
    movie_db = db['movies']
    movies = get_top_movie_links()
    for movie in movies:
        movie_doc = create_warnings_object(
            load_webpage(f'{IMDB_ROOT}{movie["link"]}parentalguide'), movie)
        movie_db.insert_one(movie_doc)

# Todo:
#     - add function to index cover art when scraping
if __name__ == '__main__':
    print('Let\'s get data!')
    main()
    print('done.')
