import time
import uuid
from collections import deque
from typing import Deque, Dict, Union, List

from meta.logger import Logger, logging
from .user import NonUserInfo, Task, User, UserCmd, UserQueueData

q_log = logging.getLogger("UserQueueHandler")
q_logger = Logger(q_log, base_level=logging.DEBUG, filename="")

ch_log = logging.getLogger("UserCommandHandler")
ch_logger = Logger(ch_log, base_level=logging.DEBUG, filename="")

th_log = logging.getLogger("UserTaskHandler")
th_logger = Logger(th_log, base_level=logging.DEBUG, filename="")


class UserQueueHandler:
    def __init__(self) -> None:

        self._q: Deque[Union[UserQueueData, NonUserInfo]] = deque()

    def add_user(self, user: UserQueueData) -> None:
        q_logger.log(logging.DEBUG, message=f"Got user {user}")
        self._q.append(user)

    def get_user(self) -> UserQueueData:
        if self._q:
            user = self._q.popleft()
            q_logger.log(logging.DEBUG, message=f"Popped user {user}")
            return user


class UserCommandHandler:
    def __init__(self) -> None:

        self._c_dict: Dict[int, UserCmd] = {}

    def set_user_command(self, user_id: int, cmd: UserCmd) -> None:
        ch_logger.log(logging.DEBUG, message=f"set_user_command: {user_id=}: {cmd=}")
        self._c_dict[user_id] = cmd

    def get_user_command(self, user_id) -> Union[UserCmd, None]:
        ch_logger.log(logging.DEBUG, message=f"get user {user_id=}")
        if user_id in self._c_dict:
            ch_logger.log(
                logging.INFO, message=f"get_user_command :return for {user_id=}"
            )
            return self._c_dict[user_id]

    def remove_old_commands(self, time_limit_s=300) -> List[int]:
        """removes all the entry that are more than [time_limit_s] seconds old"""
        c_time = int(time.time())
        user_id_to_remove = []
        for user_id in self._c_dict:
            if c_time - self._c_dict[user_id].time_inserted >= time_limit_s:
                user_id_to_remove.append(user_id)
                del self._c_dict[user_id]
        ch_logger.log(logging.INFO, message=f"Users to remove {user_id_to_remove=}")

        return user_id_to_remove


class UserTaskHandler:
    def __init__(self) -> None:
        self._tq: Dict[int, Task] = {}

    def add_task(self, user_id: int, task_desc: str) -> None:
        th_logger.log(logging.DEBUG, message=f"add task {user_id=}: {task_desc=}")
        _uuid = int(str(uuid.uuid4().int)[:10])
        self._tq[user_id] = Task(task_id=_uuid, task_desc=task_desc, task_date="")

    def add_date(self, user_id: int, date: str) -> None:
        th_logger.log(logging.DEBUG, message=f"add date {user_id=}: {date=}")
        self._tq[user_id].task_date = date

    def get_task(self, user_id: int) -> Task:
        if user_id in self._tq:
            return self._tq[user_id]

    def remove_user(self, user_id_list: List[int]) -> None:
        th_logger.log(logging.DEBUG, "in remove user")
        for _id in user_id_list:
            if _id in self._tq:
                th_logger.log(logging.INFO, message=f"successfully removed user {_id=}")
                del self._tq[_id]