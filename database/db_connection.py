# Conexión a la base de datos
import psycopg2
from contextlib import contextmanager

@contextmanager
def db_connection():
    connection = None
    try:
        connection = psycopg2.connect(
            database="sigma2",
            user="sandra",
            password="123456",
            host="localhost",
            port="5432"
        )
        yield connection
    finally:
        if connection:
            connection.close()
