from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

back_message = '👈 Назад'
skip_message = '👉 Пропустить'
all_right_message = '✅ Все верно'
cancel_message = '🚫 Отменить'
menu_message = '🏠 Меню'
confirm_message = '✅ Да'
reject_message = '❌ Нет'
edit_profile_message = "👩🏿‍🎨 Изменить Профиль"
my_profile_message = "Мой профиль"# Может добавить смайлик
my_status_message = "Мой статус"# Может добавить смайлик
set_holiday_message = "⛱️ Каникулы"
about_bot_message = "🤖 О Боте"
man_message = "👨 Мужской"
woman_message = "👩 Женский"
registr_message = "Регистрация"


def main_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(menu_message)

    return markup


def menu_markup():
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
    markup = InlineKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(InlineKeyboardButton(edit_profile_message,
                                    callback_data=edit_profile_message))
    return markup



def confirm_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(all_right_message)
    markup.add(back_message)

    return markup


def start_registr_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(registr_message)

    return markup

#TODO Добавить кнопку назад в регистрации
def register_can_skip_reply_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(back_message, skip_message)

    return markup


def register_reply_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(back_message)

    return markup


def register_man_or_woman_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(man_message, woman_message)
    markup.row(back_message, skip_message)

    return markup

def holidays_length():
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
