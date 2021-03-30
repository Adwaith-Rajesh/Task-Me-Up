import os
from typing import Union, Dict
from pathlib import Path
from pprint import pprint

from pysondb import db
from rich import print
from rich.logging import RichHandler

from meta.logger import Logger, logging
from meta.user import User, Task


DictType = Dict[str, Union[str, int, Dict[str, Union[int, str]]]]

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.json")

# stop imported loggers
logging.getLogger("pysondb").setLevel(logging.WARNING)
# logging.getLogger("filelock").setLevel(logging.WARNING)
logging.getLogger("filelock").addHandler(RichHandler())

# db loggers
db_log = logging.getLogger("database")
db_logger = Logger(logger=db_log, base_level=logging.DEBUG, filename="")

if not Path(DB_PATH).is_file():
    with open(DB_PATH, "w") as f:
        f.write('{"data":[]}')


class Database:
    def __init__(self) -> None:
        self._db = db.getDb(DB_PATH)

    def add_task(self, user: User) -> None:
        db_logger.log(level=logging.INFO, message=f"Adding user {user=}")
        if not self.check_user_exists(user.user_id):
            self._db.add(self.convert_user_to_json(user))

        else:
            tasks = user.tasks

            temp_task_dict = {
                "task": tasks[0].task_desc,
                "task_date": tasks[0].task_date,
                "task_id": tasks[0].task_id,
            }

            # get the data from the DB
            db_data = self._db.getBy({"id": self.get_db_id(user.user_id)})

            # print("db data", db_data)

            # add the task to the data from the DB
            db_data[0]["tasks"].append(temp_task_dict)

            # print("appended", db_data)

            # update the DB
            # self._db.updateById(self.get_db_id(user.user_id), db_data[0])
            self._db.update({"user_id": user.user_id}, db_data[0])

    def delete_user_tasks(self, user_id: int, task_id: int) -> bool:

        done = False

        _id = self.get_db_id(user_id)
        user_data = self._db.getBy({"id": _id})
        users_tasks = user_data[0]["tasks"]

        # delete the task with the given id
        index = 0
        for task in users_tasks:
            if task["task_id"] == task_id:
                done = True
                del users_tasks[index]

            index += 1

        user_data[0]["tasks"] = users_tasks

        # update the DB
        self._db.update({"user_id": user_id}, user_data[0])
        db_logger.log(
            logging.INFO,
            message=f"delete_user_task: User {user_id=} removed successfully",
        )

        return done

    def get_all_tasks(self, user_id: int) -> User:
        if self.check_user_exists(user_id):
            _id = self.get_db_id(user_id)
            user = self._db.getBy({"id": _id})

            db_logger.log(logging.DEBUG, message=f"get_all_tasks: {user_id=}")
            print(user)
            return self.convert_json_to_user_object(user[0])

    def get_db_id(self, user_id: int) -> int:
        if self.check_user_exists(user_id):
            return self._db.getBy({"user_id": user_id})[0]["id"]

    def convert_user_to_json(self, user: User) -> DictType:
        default_json = {"username": user.username, "user_id": user.user_id, "tasks": []}

        for task in user.tasks:
            default_json["tasks"].append(
                {
                    "task": task.task_desc,
                    "task_date": task.task_date,
                    "task_id": task.task_id,
                }
            )

        return default_json

    def convert_json_to_user_object(self, json: DictType) -> User:
        user = User("", "", [])
        user.username = json["username"]
        user.user_id = json["user_id"]

        for task in json["tasks"]:
            user.tasks.append(
                Task(
                    task_desc=task["task"],
                    task_id=task["task_id"],
                    task_date=task["task_date"],
                )
            )

        return user

    def check_user_exists(self, user_id: int):
        if self._db.getBy({"user_id": user_id}):
            return True
        return False