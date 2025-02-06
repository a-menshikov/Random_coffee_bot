from aiogram.types import ReplyKeyboardMarkup

from data import ADMIN_TG_ID

back_message = "👈 Назад"
skip_message = "👉 Пропустить"
all_right_message = "✅ Все верно"
cancel_message = "🚫 Отменить"
menu_message = "🏠 Меню"
confirm_message = "✅ Да"
reject_message = "❌ Нет"
edit_profile_message = "👩🏿‍🎨 Изменить Профиль"
my_profile_message = "Мой профиль"
my_status_message = "Мой статус"
my_reviews = "Мои встречи"
set_holiday_message = "⛱️ Каникулы"
about_bot_message = "🤖 О Боте/FAQ"
man_message = "👨 Мужской"
woman_message = "👩 Женский"
registr_message = "Регистрация"
return_to_begin_button = "Вернуться в начало"
help_texts = "С чего начать"
one_week_holidays_message = "1 неделя"
two_week_holidays_message = "2 недели"
three_week_holidays_message = "3 недели"
turn_off_holidays = "Отключить"
back_to_menu = "Вернуться в меню"
my_pare_button = "Моя пара"
back_to_main = "Главное меню"


def main_markup():
    """Главная клавиатура."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(menu_message)

    return markup


def menu_markup(message):
    """Клавиатура главного меню."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(my_profile_message, my_pare_button)
    markup.row(my_status_message, set_holiday_message)
    markup.row(about_bot_message, my_reviews)
    if message.from_user.id in list(map(int, ADMIN_TG_ID.split())):
        markup.row(back_to_main)

    return markup


def edit_profile_markup():
    """Клавиатура редактирование профиля."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(edit_profile_message)
    markup.row(back_to_menu)
    return markup


def confirm_markup():
    """Клавиатура подтверждения."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(all_right_message)
    markup.add(back_message, return_to_begin_button)
    return markup


def return_to_begin_markup():
    """Клавиатура подтверждения."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(return_to_begin_button)
    return markup


def start_registr_markup():
    """Клавиатура начала регистрации."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(registr_message)

    return markup


def register_can_skip_reply_markup():
    """Клавиатура назад-пропустить"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, skip_message)
    markup.row(return_to_begin_button)

    return markup


def register_reply_markup():
    """Кнопка назад."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message, return_to_begin_button)

    return markup


def register_man_or_woman_markup():
    """Клавиатура выбора пола."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(man_message, woman_message)
    markup.row(back_message, skip_message)
    markup.row(return_to_begin_button)

    return markup


def holidays_length():
    """Выбор длины каникул."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(one_week_holidays_message, two_week_holidays_message)
    markup.row(three_week_holidays_message, turn_off_holidays)
    markup.row(back_to_menu)
    return markup


def help_texts_markup():
    """Клавиатура с чего начать разговор."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(help_texts)
    markup.row(return_to_begin_button)
    return markup
