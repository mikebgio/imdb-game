DROP TABLE IF EXISTS categories CASCADE;
CREATE TABLE categories
(
    category_id  SERIAL PRIMARY KEY,
    short_name   VARCHAR(12) NOT NULL,
    display_name VARCHAR(32) NOT NULL
);

INSERT INTO categories(short_name, display_name)
VALUES ('nudity', 'Sex & Nudity'),
       ('violence', 'Violencfe & Gore'),
       ('profanity', 'Profanity'),
       ('alcohol', 'Alcohol, Drugs & Smoking'),
       ('frightening', 'Frightening & Intense Scenes');


DROP TABLE IF EXISTS players CASCADE;
CREATE TABLE players
(
    player_id    UUID      DEFAULT gen_random_uuid() UNIQUE PRIMARY KEY,
    username     VARCHAR(50)  UNIQUE NOT NULL,
    password     VARCHAR(255) NOT NULL,
    date_created TIMESTAMP DEFAULT NOW()
);

DROP TABLE IF EXISTS movies CASCADE;
CREATE TABLE movies
(
    movie_id    UUID      DEFAULT gen_random_uuid() UNIQUE PRIMARY KEY,
    movie_title VARCHAR(255) NOT NULL,
    year        INTEGER      NOT NULL,
    imdb_id     varchar(12) UNIQUE NOT NULL,
    date_added  TIMESTAMP DEFAULT NOW()
);
CREATE UNIQUE INDEX idx_imdb_id ON movies (imdb_id);
CREATE INDEX idx_title_year ON movies (movie_title, year);



DROP TABLE IF EXISTS games CASCADE;
CREATE TABLE games
(
    game_id    UUID      DEFAULT gen_random_uuid() PRIMARY KEY,
    player_id  UUID REFERENCES players (player_id),
    score      INTEGER   DEFAULT 0     NOT NULL,
    round      INTEGER   DEFAULT 0     NOT NULL,
    start_time TIMESTAMP DEFAULT NOW() NOT NULL,
    end_time   TIMESTAMP DEFAULT NOW() ON UPDATE NOW()
);
CREATE UNIQUE INDEX idx_game_of_player ON games(game_id, player_id);

DROP TABLE IF EXISTS guesses CASCADE;
CREATE TABLE guesses
(
    guess_id         UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    player_id        UUID REFERENCES players (player_id),
    game_id          UUID REFERENCES games (game_id),
    guess_text       TEXT      NOT NULL,
    guessed_movie_id UUID REFERENCES movies (movie_id),
    guess_time       TIMESTAMP DEFAULT NOW() NOT NULL,
    is_correct       BOOLEAN   NOT NULL
);


DROP TABLE IF EXISTS scores CASCADE;
CREATE TABLE scores
(
    score_id   UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    player_id  UUID REFERENCES players (player_id),
    score      INTEGER   NOT NULL,
    score_time TIMESTAMP DEFAULT NOW() NOT NULL
);

DROP TABLE IF EXISTS clues CASCADE;
CREATE TABLE clues
(
    clue_id      UUID      DEFAULT gen_random_uuid() PRIMARY KEY,
    movie_id     UUID REFERENCES movies (movie_id),
    category_id  INT REFERENCES categories (category_id),
    clue_text    TEXT NOT NULL,
    spoiler      BOOL      DEFAULT FALSE,
    date_created TIMESTAMP DEFAULT NOW()
);
