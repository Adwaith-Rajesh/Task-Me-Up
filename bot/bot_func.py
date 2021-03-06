import time
from datetime import datetime
from typing import List
from time import sleep

from telebot import TeleBot
import telebot

from meta.logger import Logger, logging

from meta.user import TodaysTasks, UserQueueData, UserCommands, UserCmd, User
from meta.handlers import UserCommandHandler, UserTaskHandler

from database.database import Database
from database.message_id import MessageID

bf_log = logging.getLogger("bot_func")
bf_logger = Logger(bf_log, base_level=logging.DEBUG, filename="")
db = Database()
msg_id_db = MessageID()


def set_cmd_handler(_id, cmd_handler: UserCommandHandler, cmd: UserCommands):
    cmd_handler.set_user_command(
        user_id=_id,
        cmd=UserCmd(
            time_inserted=int(time.time()),
            cmd=cmd,
        ),
    )


def send_msg(bot: telebot.TeleBot, user_id: int, message: str) -> None:
    rv = bot.send_message(user_id, text=message)
    msg_id_db.add_msg_id(user_id, rv.message_id)


def delete_msgs(bot: telebot.TeleBot, user_id: int, msg_ids: List[int]) -> None:
    for msg_id in msg_ids:
        bot.delete_message(user_id, message_id=msg_id)


def his_delete(bot: telebot.TeleBot):
    user_ids = db.get_users()
    for _id in user_ids:
        msg_ids = msg_id_db.get_msg_id(_id)
        delete_msgs(bot, _id, msg_ids)
        msg_id_db.remove_msg_id(_id)
        sleep(0.5)


def parse_text(
    bot: TeleBot,
    user_q_data: UserQueueData,
    cmd_handler: UserCommandHandler,
    task_handler: UserTaskHandler,
):

    data = user_q_data

    if data:
        _id = user_q_data.user_id
        text = data.text.lower().replace(" ", "")
        bf_logger.log(logging.DEBUG, message=f"Got {text} from {data.user_id}")
        if text == "newtask":
            set_cmd_handler(_id, cmd_handler, UserCommands.NEWTASK)
            send_msg(bot, _id, message="Enter the task description")
            set_cmd_handler(_id, cmd_handler, UserCommands.TASKDESC)

        elif text == "removetasks":
            set_cmd_handler(_id, cmd_handler, UserCommands.REMOVETASK)
            send_msg(bot, _id, message="Enter the Task ID of the task to remove..")

        elif text == "viewtasks":
            set_cmd_handler(_id, cmd_handler, UserCommands.VIEWALLTASKS)
            tasks = db.get_all_tasks(_id)
            if tasks:
                tasks = tasks.tasks
                if not tasks:
                    send_msg(bot, _id, message="You don't have any tasks.")
                for task in tasks:
                    send_msg(bot, _id, message=str(task))
            else:
                send_msg(bot, _id, message="You don't have any tasks.")

        elif text == "clearhistory":
            set_cmd_handler(_id, cmd_handler, UserCommands.CLEARHISTORY)
            msg_ids = msg_id_db.get_msg_id(_id)
            delete_msgs(bot, _id, msg_ids)
            msg_id_db.remove_msg_id(_id)

        else:
            if cmd_handler.get_user_command(_id):
                if cmd_handler.get_user_command(_id).cmd == UserCommands.TASKDESC:
                    task_handler.add_task(_id, task_desc=data.text)
                    send_msg(bot, _id, message="Enter the date")
                    set_cmd_handler(_id, cmd_handler, UserCommands.TASKDATE)

                if cmd_handler.get_user_command(_id).cmd == UserCommands.TASKDATE:
                    time_e = cmd_handler.get_user_command(_id).time_inserted
                    # validating date
                    try:
                        d_obj = datetime.strptime(user_q_data.text, "%d-%m-%Y")
                        date = datetime.strftime(d_obj, "%d-%m-%Y")
                        del d_obj
                        task_handler.add_date(_id, date)
                        task = task_handler.get_task(_id)
                        user = User(
                            username=user_q_data.username, user_id=_id, tasks=[task]
                        )
                        db.add_task(user)
                        send_msg(bot, _id, message="Task added successfully")
                        set_cmd_handler(_id, cmd_handler, UserCommands.TASKDONE)
                    except ValueError:
                        send_msg(
                            bot, _id, message="Date should be of the form DD-MM-YYYY"
                        )

                if cmd_handler.get_user_command(_id).cmd == UserCommands.REMOVETASK:
                    try:
                        db.delete_user_tasks(_id, task_id=int(data.text))
                        send_msg(bot, _id, message="Task removed successfully..")
                    except ValueError:
                        send_msg(bot, _id, message="Task ID must be a number..")


def send_cmd_time_out(bot: telebot.TeleBot, users: List[int]):
    for user in users:
        send_msg(bot, user, message="Ooops. Your last command or task timed out")


def todays_tasks_func(bot: telebot.TeleBot, bot_logger) -> List[TodaysTasks]:
    tasks = db.get_todays_tasks()
    bot_logger.log(logging.INFO, message=f"Sending todays tasks {tasks=}")

    for task in tasks:
        send_msg(bot, task.user_id, message="Today's Task's")
        if not task.tasks:
            send_msg(bot, task.user_id, message="You don't have any tasks..")
        else:
            for t in task.tasks:
                send_msg(bot, task.user_id, message=str(t))
                db.delete_user_tasks(task.user_id, t.task_id)
