from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                           ReplyKeyboardMarkup)

back_message = '👈 Назад'
skip_message = '👉 Пропустить'
all_right_message = '✅ Все верно'
cancel_message = '🚫 Отменить'
menu_message = '🏠 Меню'
confirm_message = '✅ Да'
reject_message = '❌ Нет'
edit_profile_message = "👩🏿‍🎨 Изменить Профиль"
my_profile_message = "Мой профиль"
my_status_message = "Мой статус"
set_holiday_message = "⛱️ Каникулы"
about_bot_message = "🤖 О Боте"
man_message = "👨 Мужской"
woman_message = "👩 Женский"
registr_message = "Регистрация"
return_to_menu = "Вернуться в меню"
help_texts = "С чего начать"


def main_markup():
    """Главная клавиатура."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(menu_message)

    return markup


def menu_markup():
    """Клавиатура главного меню."""
    markup = InlineKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(InlineKeyboardButton(my_profile_message,
               callback_data=my_profile_message))
    markup.add(InlineKeyboardButton(
        my_status_message, callback_data=my_status_message))
    markup.add(InlineKeyboardButton(set_holiday_message,
               callback_data=set_holiday_message))
    markup.add(InlineKeyboardButton(
        about_bot_message, callback_data=about_bot_message))
    return markup


def edit_profile_markup():
    """Клавиатура редактирование профиля."""
    markup = InlineKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(InlineKeyboardButton(edit_profile_message,
                                    callback_data=edit_profile_message))
    return markup


def confirm_markup():
    """Клавиатура подтверждения."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(all_right_message)
    markup.add(back_message)

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

    return markup


def register_reply_markup():
    """Кнопка назад."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)

    return markup


def register_man_or_woman_markup():
    """Клавиатура выбора пола."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(man_message, woman_message)
    markup.row(back_message, skip_message)

    return markup


def holidays_length():
    """Выбор длины каникул."""
    markup = InlineKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(
        InlineKeyboardButton(
            '1 неделя',
            callback_data='one_week_holidays'
        ),
        InlineKeyboardButton(
            '2 недели',
            callback_data='two_week_holidays'
        )
    )
    markup.row(
        InlineKeyboardButton(
            '3 недели',
            callback_data='three_week_holidays'
        ),
        InlineKeyboardButton(
            'Отмена',
            callback_data='cancel_holidays'
        )
    )
    return markup


def help_texts_markup():
    """Клавиатура с чего начать разговор."""
    markup = InlineKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(
        InlineKeyboardButton(
            help_texts,
            callback_data='help_texts'
        ))
    return markup
