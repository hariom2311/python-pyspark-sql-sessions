import psycopg2
from config.settings import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
from config.logger import get_logger

logger = get_logger("database")


def get_connection():
    connection = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    logger.info(f"DB connection successful — {DB_NAME}@{DB_HOST}:{DB_PORT}")
    return connection
