import time
import uuid
from collections import deque
from typing import Deque, Dict, Union, List

from .user import NonUserInfo, Task, User, UserCmd, UserQueueData


class UserQueueHandler:
    def __init__(self) -> None:

        self._q: Deque[Union[UserQueueData, NonUserInfo]] = deque()

    def add_user(self, user: UserQueueData) -> None:
        self._q.append(user)

    def get_user(self) -> UserQueueData:
        if self._q:
            return self._q.popleft()


class UserCommandHandler:
    def __init__(self) -> None:

        self._c_dict: Dict[int, UserCmd] = {}

    def set_user_command(self, user_id: int, cmd: UserCmd) -> None:
        self._c_dict[user_id] = cmd

    def get_user_command(self, user_id) -> Union[UserCmd, None]:
        if user_id in self._c_dict:
            return self._c_dict[user_id]

    def remove_old_commands(self, time_limit_s=300) -> List[int]:
        """removes all the entry that are more than [time_limit_s] seconds old"""
        c_time = int(time.time())
        user_id_to_remove = []
        for user_id in self._c_dict:
            if c_time - self._c_dict[user_id].time_inserted >= time_limit_s:
                user_id_to_remove.append(user_id)
                del self._c_dict[user_id]

        return user_id_to_remove


class UserTaskHandler:
    def __init__(self) -> None:
        self._tq: Dict[int, Task] = {}

    def add_task(self, user_id: int, task_desc: str) -> None:
        _uuid = int(str(uuid.uuid4())[:10])
        self._tq[user_id] = Task(task_id=_uuid, task_desc=task_desc, task_date="")

    def add_date(self, user_id: int, date: str) -> None:
        self._tq[user_id].task_date = date

    def remove_user(self, user_id_list: List[int]) -> None:
        for _id in user_id_list:
            if _id in self._tq:
                del self._tq[_id]