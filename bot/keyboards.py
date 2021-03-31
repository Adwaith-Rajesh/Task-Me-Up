from telebot import types


def main_keyboard():

    btn_text = ["New Task", "View Tasks", "Remove Tasks", "Clear History"]
    markup = types.ReplyKeyboardMarkup(row_width=2)
    markup.add(*[types.KeyboardButton(i) for i in btn_text])
    # markup.row_width = 2
    return markup