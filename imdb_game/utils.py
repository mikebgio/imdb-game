"""
Shared functions for imdb_game
"""

IMDB_ROOT = 'https://www.imdb.com'

def strip_text(full_title):
    return ''.join(e for e in full_title if e.isalnum()).lower()
