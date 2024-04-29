from contextlib import contextmanager
from pyrekordbox import Rekordbox6Database


@contextmanager
def managed_database_connection():
    db = Rekordbox6Database()
    db.open()
    try:
        yield db
    finally:
        db.close()
