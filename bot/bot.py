import os
import threading
from pathlib import Path
from time import sleep

import schedule
from telebot import TeleBot
from dotenv import load_dotenv
from rich import print, pretty


from meta.logger import Logger, logging

from meta.user import UserQueueData
from meta.handlers import UserCommandHandler, UserQueueHandler, UserTaskHandler
from .bot_func import parse_text
from .keyboards import main_keyboard

pretty.install()

ENV_FILE = os.path.join(Path(__file__).parent.parent, ".env")
load_dotenv(dotenv_path=ENV_FILE)

# stop other loggers from imported modules
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("schedule").setLevel(logging.WARNING)

# loggers
b_l = logging.getLogger("bot")
bot_logger = Logger(b_l, base_level=logging.DEBUG, filename="bot.log")

# handlers
user_q_handler = UserQueueHandler()
user_cmd_handler = UserCommandHandler()
user_task_handler = UserTaskHandler()

bot = TeleBot(token=os.environ.get("BOT_API_TOKEN_TEST"))


@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.from_user.id,
        f"Hello, {msg.from_user.username}.\n",
        reply_markup=main_keyboard(),
    )


@bot.message_handler(func=lambda msg: True)
def handle_all_the_msgs(msg):
    """Add the incoming msgs to the Q"""

    # make the user Q date
    user = UserQueueData(
        user_id=msg.from_user.id,
        username=msg.from_user.username,
        chat_id=msg.chat.id,
        text=msg.text,
    )

    # add the user q data to the Q handler
    user_q_handler.add_user(user)


# some function
def get_q_users():
    # logging.debug(msg="In get_q_users")
    user = user_q_handler.get_user()
    parse_text(
        bot=bot,
        user_q_data=user,
        cmd_handler=user_cmd_handler,
        task_handler=user_task_handler,
    )


def pol():
    bot_logger.log(logging.DEBUG, message="Starting Poll")
    while True:
        bot.polling(none_stop=True)
        sleep(2)


def start_bot():
    def _pol():
        bot_logger.log(logging.INFO, "Starting bot")
        pol()

    def _sched():
        bot_logger.log(logging.DEBUG, message="Starting scheduler")
        schedule.every(0.5).seconds.do(get_q_users)
        # get_q_users()

    pol_t = threading.Thread(target=_pol, daemon=True)
    sched = threading.Thread(target=_sched, daemon=True)
    pol_t.start()
    sched.start()
    # pol_t.join()
    # sched.join()

    # keep the main thread alive 😁 so that i can use Ctrl + c to stop the execution
    while True:
        try:
            schedule.run_pending()
            sleep(1)
        except KeyboardInterrupt:
            quit()