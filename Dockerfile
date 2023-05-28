FROM python:3.9-slim as base
WORKDIR /imdb-game

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

FROM base as application
WORKDIR /imdb-game
COPY . .
HEALTHCHECK CMD ./imdb_game/healthcheck.py
CMD [ "python3", "-m" , "flask", "--app", "flask_app.app", "run", "--host=0.0.0.0", "--port=3000"]
