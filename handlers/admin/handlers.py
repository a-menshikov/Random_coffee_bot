from aiogram import types
from aiogram.dispatcher import FSMContext

from data import ADMIN_TG_ID
from handlers.user import main_menu
from loader import bot, dp, db_controller, logger
from states import AdminData
from keyboards.admin import *


@dp.message_handler(text=admin_menu)
async def admin_menu(message: types.Message):
    if message.from_user.id == int(ADMIN_TG_ID):
        await bot.send_message(message.from_user.id,
                     text="Выберите из доступных вариантов:",
                     reply_markup=admin_menu_markup()
                     )
        await AdminData.start.set()
    else:
        await bot.send_message(message.from_user.id,
                     text="Посторонним вход запрещен")


@dp.message_handler(text=inform, state=AdminData.start)
async def inform_message(message: types.Message):
    await bot.send_message(message.from_user.id,
                     "Тут информация о встречах за прошедшую неделю"
                     )


@dp.message_handler(text=ban_list, state=AdminData.start)
async def ban_list(message: types.Message):
    await bot.send_message(message.from_user.id,
                     "Что вы хотите сделать?",
                    reply_markup=admin_ban_markup()
                     )

@dp.message_handler(text=add_to_ban_list, state=AdminData.start)
async def ban_list_add(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "тут добавляем в бан",
        reply_markup=admin_back_markup()
    )


@dp.message_handler(text=remove_from_ban_list, state=AdminData.start)
async def ban_list_remove(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "тут убираем из бана",
        reply_markup=admin_back_markup()
    )


@dp.message_handler(text=back_to_main, state=AdminData.start)
async def back_to_main(message: types.Message, state: FSMContext):
    await state.reset_state()
    await bot.send_message(message.from_user.id,
                     "Вы в главном меню",
                     reply_markup=admin_main_markup()
                     )


@dp.message_handler(text=go_back, state=AdminData)
async def go_back(message: types.Message):
    await admin_menu(message)


@dp.message_handler(text=user_menu)
async def user_menu(message: types.Message):
    await main_menu(message)
