import psycopg2
from config import params

def get_db_connection():
    return psycopg2.connect(**params)