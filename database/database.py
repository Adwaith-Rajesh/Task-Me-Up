import os

# import logging
from pathlib import Path
from typing import Dict, List, Union

from pysondb import db

from meta.logger import Logger, logging
from meta.user import User, Task


import_loggers = ["pysondb", "filelock"]
for loggers in import_loggers:
    l = logging.getLogger(loggers)
    l.setLevel(logging.CRITICAL)

del l

l = logging.getLogger("database")

db_logger = Logger(logger=l, filename="database.log", base_level=logging.DEBUG)

DB_FILE_PATH = os.path.join(Path(__file__).parent, "db.json")
DictType = Dict[str, Union[str, int, List[Task]]]


class Database:
    def __init__(self) -> None:
        self._db = db.getDb(DB_FILE_PATH)

    def add_user(self, user: User) -> None:
        db_logger.log(logging.DEBUG, self.convet_user_object_to_json(user))
        self._db.add(self.convet_user_object_to_json(user))

    def convet_user_object_to_json(self, user: User) -> DictType:
        default_json = {"username": "", "user_id": 0, "tasks": []}

        # set all the values to the default json object
        default_json["username"] = user.username
        default_json["user_id"] = user.user_id

        for task in user.tasks:
            default_json["tasks"].append(
                {
                    "task_id": task.task_id,
                    "task_desc": task.task_desc,
                    "task_date": task.task_date,
                }
            )

        return default_json
