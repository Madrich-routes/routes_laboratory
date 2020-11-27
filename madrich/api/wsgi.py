"""gunicorn WSGI server configuration."""
from multiprocessing import cpu_count

from dotenv import load_dotenv

from madrich.config import settings

load_dotenv()


def max_workers():
    return cpu_count()


bind = f"{settings.HOST}:{settings.PORT}"
workers = max_workers()
