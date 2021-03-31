import os
from typing import List
from pathlib import Path

from meta.logger import Logger, logging

from pysondb import db
from rich.logging import RichHandler


# stop imported loggers
logging.getLogger("pysondb").setLevel(logging.WARNING)
logging.getLogger("filelock").setLevel(logging.WARNING)
logging.getLogger("filelock").addHandler(RichHandler())

# db loggers
ms_log = logging.getLogger("msg_id")
ms_logger = Logger(logger=ms_log, base_level=logging.DEBUG, filename="message_id.log")


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "msg_id.json")

if not Path(DB_PATH).is_file():
    with open(DB_PATH, "w") as f:
        f.write('{"data":[]}')


class MessageID:
    def __init__(self) -> None:
        self._db = db.getDb(filename=DB_PATH)

    def add_msg_id(self, user_id: int, msg_id: int) -> None:

        if not self.check_user_id_exists(user_id):
            self._db.add({"user_id": user_id, "msg_ids": [msg_id]})
        else:
            data = self._db.getBy({"user_id": user_id})[0]
            data["msg_ids"].append(msg_id)

            self._db.update({"user_id": user_id}, data)

        ms_logger.log(
            logging.INFO,
            message=f"add_msg_id added user {user_id=} message_id {msg_id=}",
        )

    def get_msg_id(self, user_id: int) -> List[int]:
        ms_logger.log(logging.INFO, message=f"get_msg_id get {user_id=}")
        if self.check_user_id_exists(user_id):
            data = self._db.getBy({"user_id": user_id})[0]
            return data["msg_ids"]
        else:
            return []

    def remove_msg_id(self, user_id: int) -> None:
        if self.check_user_id_exists(user_id):
            data = self._db.getBy({"user_id": user_id})[0]
            data["msg_ids"].clear()
            self._db.update({"user_id": user_id}, data)
            ms_logger.log(
                logging.INFO,
                message=f"remove_msg_id message ids remove successfully {user_id=}",
            )

    def check_user_id_exists(self, user_id: int) -> bool:
        if self._db.getBy({"user_id": user_id}):
            return True
        return False