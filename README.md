# imdb-game

[![PyTest](https://github.com/mikebgio/imdb-game/actions/workflows/main.yml/badge.svg)](https://github.com/mikebgio/imdb-game/actions/workflows/main.yml) [![CodeQL](https://github.com/mikebgio/imdb-game/actions/workflows/github-code-scanning/codeql/badge.svg?branch=main)](https://github.com/mikebgio/imdb-game/actions/workflows/github-code-scanning/codeql)

Web version of Nick Martucci's Inappropriate Movie Database gameshow

A game where players are presented with a release year and a series of
real posts from IMDB's parental guide section as the only clues to guess
the name of a movie. The earlier you guess correctly, the more points you earn.

## Technologies Used

* Python 3.9
    * Flask
    * BeatifulSoup
    * psycopg3
* PostgreSQL
* Docker

## Run with Docker Compose

### Pre-Requisites

1. Linux
2. [Docker](https://docs.docker.com/get-docker/)
3. [docker-compose](https://docs.docker.com/compose/install/)
4. clone this repo

### Commands
From the root of the repository, run the following commands
```shell
docker-compose build
docker-compose up -d
```

To shut down the containers
```shell
docker-compose down
```

