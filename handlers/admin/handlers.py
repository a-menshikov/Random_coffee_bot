from aiogram import types

from loader import bot, dp, db_controller, logger
from states import AdminData
from keyboards.admin import *


@dp.message_handler(text=admin_menu, state=AdminData.start)
async def inform_message(message: types.Message):
    await bot.send_message(message.from_user.id,
                     text="Выберите из доступных вариантов:",
                     reply_markup=admin_menu_markup()
                     )


@dp.message_handler(text=inform, state=AdminData.start)
async def inform_message(message: types.Message):
    await bot.send_message(message.from_user.id,
                     "Тут информация о встречах за прошедшую неделю"
                     )


@dp.message_handler(text=ban_list, state=AdminData.start)
async def ban_list(message: types.Message):
    await bot.send_message(message.from_user.id,
                     "здесь возможность добавления пользователей в бан и из него"
                     )


@dp.message_handler(text=back_to_main, state=AdminData.start)
async def ban_list(message: types.Message):
    await bot.send_message(message.from_user.id,
                     "Вы в главном меню",
                     reply_markup=admin_main_markup()
                     )
