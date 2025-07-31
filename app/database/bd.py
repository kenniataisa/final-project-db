import psycopg2
from app.database.config import DB_NAME, DB_HOST, DB_ADMIN_USER, DB_ADMIN_PASSWORD, DB_READER_USER, DB_READER_PASSWORD

def get_connection(role: str = 'reader'):
    try:
        if role == 'admin':
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_ADMIN_USER,
                password=DB_ADMIN_PASSWORD,
                host=DB_HOST
            )
        else:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_READER_USER,
                password=DB_READER_PASSWORD,
                host=DB_HOST
            )
        return conn
    except psycopg2.Error as e:
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None
