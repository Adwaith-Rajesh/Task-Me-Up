import os
from pathlib import Path

from pysondb import db


DB_FILE_PATH = os.path.join(Path(__file__).parent, "db.json")


class Database:
    def __init__(self) -> None:
        self._db = db.getDb(DB_FILE_PATH)