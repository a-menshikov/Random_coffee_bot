from aiogram.types import ReplyKeyboardMarkup

from keyboards.user.defalt_markups import menu_message, back_to_main
admin_menu_button = "Меню администратора"
inform = "Отчет за прошедшую неделю"
ban_list = "Бан-лист"

add_to_ban_list = "Добавить в бан-лист"
remove_from_ban_list = "Убрать из бана"
go_back = "Назад"
algo_start = "Запуск алгоритма"
review_messages = "Запуск опроса"
change_status = "Изменить статус участия"
cancel = "Отмена"
take_part_button = "Принять участие"
do_not_take_part_button = "Не принимать участие"


def admin_main_markup():
    """Начальная кнопка админа."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(admin_menu_button)
    markup.add(menu_message)
    return markup


def admin_menu_markup():
    """Меню админа."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(inform)
    markup.add(ban_list)
    markup.add(algo_start)
    markup.add(review_messages)
    markup.add(change_status)
    markup.add(back_to_main)
    return markup


def admin_ban_markup():
    """Кнопки добавлени и отзыва с бана."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(add_to_ban_list)
    markup.add(remove_from_ban_list)
    markup.add(go_back)
    return markup

def admin_change_status_markup():
    """Кнопки изменения статуса участия админа"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(take_part_button)
    markup.add(do_not_take_part_button)
    markup.add(go_back)
    return markup


def admin_back_markup():
    """Кнопка назад"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(go_back)
    return markup

def admin_cancel_markup():
    """Кнопка назад"""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(cancel)
    return markup
