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

    user_id: int
    time_inserted: int
    cmd: UserCommands


class UserCommands(Enum):

    NEWTASK = 1
    TASKDESC = 2
    TASKDATE = 3
    DELETETASK = 4
    VIEWALLTASKS = 5
    TIMEOUT = 10
