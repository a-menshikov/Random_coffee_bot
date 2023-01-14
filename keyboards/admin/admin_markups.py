from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

admin_menu = "Меню администратора"
inform = "Отчет за прошедшую неделю"
ban_list = "Бан-лист"
menu_message = "🏠 Меню пользователей"
back_to_main = 'Главное меню'


def admin_main_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(admin_menu)
    markup.add(menu_message)
    return markup

def admin_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(inform)
    markup.add(ban_list)
    markup.add(back_to_main)
    return markup
