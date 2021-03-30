from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Any


@dataclass
class User:

    username: str
    user_id: int
    tasks: List[Task]


@dataclass
class Task:
    task_id: int
    task_desc: str
    task_date: str

    def __str__(self) -> str:
        return f"Task ID: {self.task_id}\nTask Desc: {self.task_desc}\nTask Date: {self.task_date}"


@dataclass
class UserQueueData:
    """The data collected when the user is entered into the QUEUE"""

    user_id: int
    username: str
    chat_id: int
    text: str


@dataclass
class NonUserInfo:
    """Will hold anything other info realted to the user"""

    info: Any
    cmd: UserCommands


@dataclass
class UserCmd:
    """The current state of the user / or the current command the user is tryign to run"""

    time_inserted: int
    cmd: UserCommands


@dataclass
class TodaysTasks:
    user_id: int
    tasks: List[Task]


class UserCommands(Enum):

    NEWTASK = 1
    TASKDESC = 2
    TASKDATE = 3
    REMOVETASK = 4
    VIEWALLTASKS = 5
    TASKDONE = 6
    TIMEOUT = 10
