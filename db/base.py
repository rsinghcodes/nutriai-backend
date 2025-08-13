import psycopg2
from psycopg2.extras import RealDictCursor
from core.config import settings

def get_connection():
    return psycopg2.connect(settings.DATABASE_URL, cursor_factory=RealDictCursor)
