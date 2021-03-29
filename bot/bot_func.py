from telebot import TeleBot

from meta.logger import Logger, logging

from meta.user import UserQueueData
from meta.handlers import UserCommandHandler


bf_log = logging.getLogger("bot_func")
bf_logger = Logger(bf_log, base_level=logging.DEBUG, filename="")


def parse_text(
    bot: TeleBot, user_q_data: UserQueueData, cmd_handler: UserCommandHandler
):

    data = user_q_data
    text = data.text.lower().replace(" ", "")

    if text == "newtask":
        bf_logger.log(logging.DEBUG, message=f"Got {text} from {data.user_id}")
        pass
