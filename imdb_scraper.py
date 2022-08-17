#!/usr/bin/env python3
import urllib.parse
from pprint import pprint

import requests
from bs4 import BeautifulSoup

IMDB_ROOT = 'https://www.imdb.com'


def clean_whitespace(text):
    warning_whitespace = ' ' * 24
    return text.replace('\n', '').replace(warning_whitespace, '').strip()


def load_webpage(url):
    r = requests.get(url)
    return BeautifulSoup(r.text, "html.parser")


def create_warnings_object(soup):
    categories = {
        'nudity': {'full_name': 'Sex & Nudity', 'warnings': []},
        'violence': {'full_name': 'Violence & Gore', 'warnings': []},
        'profanity': {'full_name': 'Profanity', 'warnings': []},
        'alcohol': {'full_name': 'Alcohol, Drugs & Smoking', 'warnings': []},
        'frightening': {'full_name': 'Frightening & Intense Scenes',
                        'warnings': []},
    }
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
                categories[key]['warnings'].append(entry)
    return categories


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


if __name__ == '__main__':
    results = search_imdb('south park bigger longer and uncut')
    movie = f'{IMDB_ROOT}/{results[0]}parentalguide'
    print(movie)
    warnings = create_warnings_object(load_webpage(movie))
    pprint(warnings)
    print('done.')
