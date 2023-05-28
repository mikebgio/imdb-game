# Creates an image for the PostgreSQL database supporting the IMDB game
# Image will have the schema built-in with setup_db.sql being placed in
# an autorun location for postgres docker
FROM postgres:15
WORKDIR /docker-entrypoint-initdb.d
COPY setup_db.sql .
COPY data data
