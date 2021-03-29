from telebot import types


def main_keyboard():

    btn_text = ["New Task", "View Tasks", "Remove Tasks"]
    markup = types.ReplyKeyboardMarkup(row_width=2)
    for name in btn_text:
        markup.add(types.KeyboardButton(text=name))

    return markup