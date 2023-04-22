import imdb_game.utils.utils as utils

CLUE_TEXT = "The group that routinely gang rapes the protagonist references " \
            "oral sex during an assault by telling the main character he " \
            "will swallow whatever he's given to swallow. Nothing is " \
            "shown onscreen."

CLUE_RESULTS = {
    'fifteen': "The  group that\nroutinely  gang\nrapes       the\nprotagonist\nreferences oral\nsex  during  an\nassault      by\ntelling     the\nmain  character\nhe will swallow\nwhatever   he's\ngiven        to\nswallow.\nNothing      is\nshown onscreen.",
    'ten': "The  group\nthat\nroutinely\ngang rapes\nthe protag\nonist\nreferences\noral   sex\nduring  an\nassault by\ntelling\nthe   main\ncharacter\nhe    will\nswallow\nwhatever\nhe's given\nto\nswallow.\nNothing is\nshown\nonscreen.",
    'five': "The\ngroup\nthat\nrouti\nnely\ngang\nrapes\nthe p\nrotag\nonist\nrefer\nences\noral\nsex d\nuring\nan as\nsault\nby te\nlling\nthe\nmain\nchara\ncter\nhe\nwill\nswall\now wh\nateve\nr\nhe's\ngiven\nto sw\nallow\n. Not\nhing\nis\nshown\nonscr\neen.",
    'one': "T\nh\ne\ng\nr\no\nu\np\nt\nh\na\nt\nr\no\nu\nt\ni\nn\ne\nl\ny\ng\na\nn\ng\nr\na\np\ne\ns\nt\nh\ne\np\nr\no\nt\na\ng\no\nn\ni\ns\nt\nr\ne\nf\ne\nr\ne\nn\nc\ne\ns\no\nr\na\nl\ns\ne\nx\nd\nu\nr\ni\nn\ng\na\nn\na\ns\ns\na\nu\nl\nt\nb\ny\nt\ne\nl\nl\ni\nn\ng\nt\nh\ne\nm\na\ni\nn\nc\nh\na\nr\na\nc\nt\ne\nr\nh\ne\nw\ni\nl\nl\ns\nw\na\nl\nl\no\nw\nw\nh\na\nt\ne\nv\ne\nr\nh\ne\n'\ns\ng\ni\nv\ne\nn\nt\no\ns\nw\na\nl\nl\no\nw\n.\nN\no\nt\nh\ni\nn\ng\ni\ns\ns\nh\no\nw\nn\no\nn\ns\nc\nr\ne\ne\nn\n."
}

TEXTS_TO_STRIP = [
    "The Lord of the Rings: The Return of the King",

    "The Lord of the Rings: The Fellowship of the Ring",
    "Star Wars: Episode V - The Empire Strikes Back",
    "Star Wars: Episode VI - Return of the Jedi",
    "Dr. Strangelove or: How I Learned to Stop Worrying and Love the Bomb",
    "Hachi: A Dog's Tale"
]

STRIPPED_TEXTS = [
    "thelordoftheringsthereturnoftheking",

    "thelordoftheringsthefellowshipofthering",
    "starwarsepisodevtheempirestrikesback",
    "starwarsepisodevireturnofthejedi",
    "drstrangeloveorhowilearnedtostopworryingandlovethebomb",
]

ACCENTED_TEXTS = [

    "Árvíztűrűték",
    "Éáűűáűáűáűáűáűáűáűáűáűáűáűáűáűáű",
    "El NiÑo",
    "Írás",
    "Játék",
    "Király",
]

UNACCENTED_TEXTS = ['Arvizturutek', 'Eauuauauauauauauauauauauauauauau',
                    'El NiNo', 'Iras', 'Jatek', 'Kiraly']


def test_imdb_root():
    assert isinstance(utils.IMDB_ROOT, str)
    assert utils.IMDB_ROOT == 'https://www.imdb.com'


def test_justify_text():
    assert utils.justify_text(CLUE_TEXT, 15) == CLUE_RESULTS['fifteen']
    assert utils.justify_text(CLUE_TEXT, 10) == CLUE_RESULTS['ten']
    assert utils.justify_text(CLUE_TEXT, 5) == CLUE_RESULTS['five']
    assert utils.justify_text(CLUE_TEXT, 1) == CLUE_RESULTS['one']


def test_strip_text():
    for text, stripped_text in zip(TEXTS_TO_STRIP, STRIPPED_TEXTS):
        assert utils.strip_text(text) == stripped_text

def test_remove_accents():
    for text, unaccented_text in zip(ACCENTED_TEXTS, UNACCENTED_TEXTS):
        assert utils.remove_accents(text) == unaccented_text
