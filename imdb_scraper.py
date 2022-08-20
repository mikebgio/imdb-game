#!/usr/bin/env python3
import urllib.parse

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from replit import db

IMDB_ROOT = 'https://www.imdb.com'


def clean_whitespace(text):
    warning_whitespace = ' ' * 24
    return text.replace('\n', '').replace(warning_whitespace, '').strip()


def load_webpage(url):
    r = requests.get(url)
    return BeautifulSoup(r.text, "html.parser")


def create_warnings_object(soup, movie_meta: dict):
    # TODO: Make a version that utilizes Replit.DB
    movie = {'categories': {'nudity': {'full_name': 'Sex & Nudity', 'warnings':
        []}, 'violence': {'full_name': 'Violence & Gore', 'warnings': []},
                            'profanity': {'full_name': 'Profanity',
                                          'warnings': []},
                            'alcohol': {'full_name': 'Alcohol, Drugs & Smoking',
                                        'warnings': []},
                            'frightening': {
                                'full_name': 'Frightening & Intense Scenes',
                                'warnings': []
                            }, }}
    movie = movie_meta | movie
    list_item = 'ipl-zebra-list__item'
    pfx = 'advisory-'
    for warning in soup.find_all(class_=list_item):
        text = clean_whitespace(warning.contents[0])
        if 'id' in warning.parent.parent.attrs:
            if warning.parent.parent.attrs['id'].lower() != 'certificates':
                tag = warning.parent.parent.attrs['id']
                key = tag.replace(pfx, '')
                spoiler = False
                if 'spoiler' in key:
                    spoiler = True
                    key = key.replace('spoiler-', '')
                entry = {'text': text, 'spoiler': spoiler}
                movie['categories'][key]['warnings'].append(entry)
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
    # TODO: Parameterize for prod
    client = MongoClient('mongodb://localhost:27017')
    db = client['imdb']
    movie_db = db['movies']
    movies = get_top_movie_links()
    for movie in movies:
        movie_doc = create_warnings_object(
            load_webpage(f'{IMDB_ROOT}{movie["link"]}parentalguide'), movie)
        movie_db.insert_one(movie_doc)


if __name__ == '__main__':
    main()
    print('done.')
