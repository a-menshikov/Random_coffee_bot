from aiogram.types import ReplyKeyboardMarkup

yes_button = "Состоялась"
no_button = "Не состоялась"


skip_message = "👉 Пропустить"


def review_yes_or_no():
    """Кнопки с вариантами да или нет."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(yes_button, no_button)
    markup.add(skip_message)
    return markup


def review_skip():
    """Кнопки с вариантами отзыва о встрече."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(skip_message)
    return markup
