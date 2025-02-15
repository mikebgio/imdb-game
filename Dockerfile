FROM python:3.12-slim as base
WORKDIR /imdb-game

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM base as application
WORKDIR /imdb-game
COPY . .
HEALTHCHECK CMD ./imdb_game/healthcheck.py
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=3000"]
