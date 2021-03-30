import time
from datetime import datetime
from typing import List

from telebot import TeleBot
import telebot

from meta.logger import Logger, logging

from meta.user import TodaysTasks, UserQueueData, UserCommands, UserCmd, User
from meta.handlers import UserCommandHandler, UserTaskHandler

from database.database import Database


bf_log = logging.getLogger("bot_func")
bf_logger = Logger(bf_log, base_level=logging.DEBUG, filename="")
db = Database()


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
            cmd_handler.set_user_command(
                user_id=_id,
                cmd=UserCmd(
                    time_inserted=int(time.time()),
                    cmd=UserCommands.TASKDESC,
                ),
            )
            bot.send_message(_id, text="Enter the task description")

        elif text == "removetasks":
            cmd_handler.set_user_command(
                user_id=_id,
                cmd=UserCmd(
                    time_inserted=int(time.time()),
                    cmd=UserCommands.REMOVETASK,
                ),
            )
            bot.send_message(_id, text="Enter the Task ID of the task to remove..")

        elif text == "viewtasks":
            cmd_handler.set_user_command(
                user_id=_id,
                cmd=UserCmd(
                    time_inserted=int(time.time()),
                    cmd=UserCommands.VIEWALLTASKS,
                ),
            )

            tasks = db.get_all_tasks(_id)
            if tasks:
                tasks = tasks.tasks
                for task in tasks:
                    bot.send_message(_id, text=str(task))

        else:
            if cmd_handler.get_user_command(_id):
                if cmd_handler.get_user_command(_id).cmd == UserCommands.TASKDESC:
                    task_handler.add_task(_id, task_desc=data.text)
                    bot.send_message(_id, text="Enter the date")
                    cmd_handler.set_user_command(
                        _id,
                        cmd=UserCmd(
                            time_inserted=int(time.time()), cmd=UserCommands.TASKDATE
                        ),
                    )

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
                        bot.send_message(_id, text="Task added successfully")
                        cmd_handler.set_user_command(
                            _id,
                            UserCmd(time_inserted=time_e, cmd=UserCommands.TASKDONE),
                        )
                    except ValueError:
                        bot.send_message(_id, f"Date should be of the form DD-MM-YYYY")

                if cmd_handler.get_user_command(_id).cmd == UserCommands.REMOVETASK:
                    try:
                        db.delete_user_tasks(_id, task_id=int(data.text))
                        bot.send_message(_id, text="Task removed successfully..")
                    except ValueError:
                        bot.send_message(_id, text="Task ID must be a number..")


def send_cmd_time_out(bot: telebot.TeleBot, users: List[int]):
    for user in users:
        bot.send_message(user, text="Ooops. Your last command/ task timed out")


def todays_tasks_func(bot: telebot.TeleBot, bot_logger) -> List[TodaysTasks]:
    tasks = db.get_todays_tasks()
    bot_logger.log(logging.INFO, message=f"Sending todays tasks {tasks=}")

    for task in tasks:
        bot.send_message(task.user_id, text="Today's Task's")
        for t in task.tasks:
            bot.send_message(task.user_id, str(t))
            db.delete_user_tasks(task.user_id, t.task_id)