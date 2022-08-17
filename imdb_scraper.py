#!/usr/bin/env python3
from pprint import pprint
import re
import requests
from bs4 import BeautifulSoup

# TODO: this could be the parser of HTML pages that a crawler script is downloading
#   the crawler script should smartly seek out existing /parentalguide pages
#   it should verify the page exists and download it to a staging folder
#   this script would parse static downloaded .html files and then ship data to DB
#   Perhaps the interface can be javascript

def clean_whitespace(text):
    warning_whitespace = ' ' * 24
    return text.replace('\n', '').replace(warning_whitespace, '').strip()


def get_imdb_page(movie):
    r = requests.get(movie)
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



if __name__ == '__main__':
    movie = 'https://www.imdb.com/title/tt0158983/parentalguide'
    # soup = get_imdb_page(movie)
    southpark = create_warnings_object(get_imdb_page(movie))
    pprint(southpark)
    print('done.')

