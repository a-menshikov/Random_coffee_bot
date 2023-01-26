from aiogram import types
from handlers.decorators import admin_handlers
from handlers.user.check_message import check_message
from handlers.user.get_info_from_table import get_id_from_user_info_table
from keyboards import take_part_button, do_not_take_part_button, \
    change_status, admin_change_status_markup, algo_start
from keyboards.admin import admin_menu_button, admin_menu_markup, go_back, \
    inform
from loader import bot, dp, db_controller
from match_algoritm import MachingHelper


@dp.message_handler(text=go_back)
@admin_handlers
async def go_back(message: types.Message):
    """Возврат в меню админа."""
    await admin_menu(message)


@dp.message_handler(text=admin_menu_button)
@admin_handlers
async def admin_menu(message: types.Message):
    """Вывод меню администратора."""
    await bot.send_message(
        message.from_user.id,
        text="Выберите из доступных вариантов:",
        reply_markup=admin_menu_markup()
    )


@dp.message_handler(text=inform)
@admin_handlers
async def inform_message(message: types.Message):
    """Вывод отчета."""
    await bot.send_message(
        message.from_user.id,
        "Тут информация о встречах за прошедшую неделю"
    )


@dp.message_handler(text=change_status)
@admin_handlers
async def change_status_message(message: types.Message):
    """Вывод отчета."""
    await bot.send_message(
        message.from_user.id,
        "Выберите вариант:",
        reply_markup=admin_change_status_markup()
    )


@dp.message_handler(text=take_part_button)
@admin_handlers
async def take_part_yes(message: types.Message):
    """Изменение статуса на принимать участие."""
    change_admin_status(message, 1)
    await bot.send_message(
        message.from_user.id,
        "Теперь вы участвуете в распределении."
    )


@dp.message_handler(text=do_not_take_part_button)
@admin_handlers
async def take_part_no(message: types.Message):
    """Изменение статуса на не принимать участие."""
    change_admin_status(message, 0)
    await bot.send_message(
        message.from_user.id,
        "Вы изменили статус и теперь не участвуете в распределении."
    )


@dp.message_handler(text=algo_start)
@admin_handlers
async def start_algoritm(message: types.Message):
    """Запуск алгоритма распределения"""
    await check_message()
    mc = MachingHelper()
    res = mc.start()
    await mc.send_and_write(res)


def change_admin_status(message: types.Message, status):
    user_id = get_id_from_user_info_table(message.from_user.id)
    query = """UPDATE user_status SET status=? WHERE id=?"""
    values = (status, user_id)
    db_controller.query(query, values)
