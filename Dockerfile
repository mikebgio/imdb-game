FROM python:3.9-slim
WORKDIR /imdb-game

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
HEALTHCHECK CMD ./imdb_game/healthcheck.py
CMD [ "python3", "-m" , "flask", "--app", "flask_app.app", "run", "--host=0.0.0.0", "--port=3000"]
