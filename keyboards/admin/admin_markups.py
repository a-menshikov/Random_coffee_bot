from aiogram import types
from aiogram.types import ReplyKeyboardMarkup
from data import ADMIN_TG_ID
from keyboards.user.defalt_markups import (back_to_main, menu_markup,
                                           menu_message)

admin_menu_button = "Меню администратора"
inform = "Отчет за неделю"
ban_list = "Бан-лист"

add_to_ban_list = "Добавить в бан-лист"
remove_from_ban_list = "Убрать из бана"
go_back = "Назад"
algo_start = "Алгоритм"
review_messages = "Запуск опроса"
change_status = "Статус участия"
cancel = "Отмена"
take_part_button = "Принять участие"
do_not_take_part_button = "Не принимать участие"
send_message_to_all_button = "Сообщение пользователям"


def admin_main_markup():
    """Начальная кнопка админа."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add(admin_menu_button)
    markup.add(menu_message)
    return markup


def admin_menu_markup():
    """Меню админа."""
    markup = ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.row(inform, send_message_to_all_button)
    markup.row(ban_list, change_status)
    markup.row(review_messages, back_to_main)
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


def back_to_main_markup(message: types.Message):
    if message.from_user.id in list(map(int, ADMIN_TG_ID.split())):
        return admin_main_markup()
    return menu_markup(message)
