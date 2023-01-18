from aiogram import types

from data import ADMIN_TG_ID
from loader import bot, dp
from states import AdminData
from keyboards.admin import admin_menu, admin_menu_markup, inform, go_back


@dp.message_handler(text=admin_menu)
async def admin_menu(message: types.Message):
    """Вывод меню администратора."""
    if message.from_user.id in list(map(int, ADMIN_TG_ID.split())):
        await bot.send_message(
            message.from_user.id,
            text="Выберите из доступных вариантов:",
            reply_markup=admin_menu_markup()
        )
        await AdminData.start.set()
    else:
        await bot.send_message(
            message.from_user.id,
            text="Посторонним вход запрещен"
        )


@dp.message_handler(text=inform, state=AdminData.start)
async def inform_message(message: types.Message):
    """Вывод отчета."""
    await bot.send_message(
        message.from_user.id,
        "Тут информация о встречах за прошедшую неделю"
    )


@dp.message_handler(text=go_back, state=AdminData)
async def go_back(message: types.Message):
    """Возврат в меню админа."""
    await admin_menu(message)
