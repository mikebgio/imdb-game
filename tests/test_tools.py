import psycopg
import os

# Set the locale to en_US.UTF-8
os.environ['LC_ALL'] = 'en_US.UTF-8'


def init_test_db(postgresql):
    db_url = postgresql.url()
    with open("db/setup_db.sql", "r", encoding="utf-8") as schema_file:
        schema = schema_file.read()
    connection = psycopg.connect(db_url)
    with connection.cursor() as cur:
        cur.execute(schema)
        connection.commit()
    return connection
