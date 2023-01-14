from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

admin_menu = "Меню администратора"
inform = "Отчет за прошедшую неделю"
ban_list = "Бан-лист"
user_menu = "🏠 Меню пользователей"
back_to_main = 'Главное меню'
add_to_ban_list = "Добавить в бан-лист"
remove_from_ban_list = "Убрать из бана"
go_back = "Назад"


def admin_main_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(admin_menu)
    markup.add(user_menu)
    return markup

def admin_menu_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(inform)
    markup.add(ban_list)
    markup.add(back_to_main)
    return markup

def admin_ban_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(add_to_ban_list)
    markup.add(remove_from_ban_list)
    markup.add(go_back)
    return markup

def admin_back_markup():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(go_back)
    return markup
