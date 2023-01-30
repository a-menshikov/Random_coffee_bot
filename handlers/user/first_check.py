from aiogram import types
from aiogram.types import ReplyKeyboardRemove

from data import ADMIN_TG_ID
from handlers.user.get_info_from_table import check_user_in_base
from handlers.user.ban_check import check_user_in_ban
from keyboards.admin import admin_main_markup
from keyboards.user import start_registr_markup, main_markup
from loader import bot
from states import UserData, BannedState


async def check_and_add_registration_button(message: types.Message):
    """Проверка пользователя для последующих действий."""
    if not await check_user_in_base(message):
        await bot.send_message(
            message.from_user.id,
            text="Нажмите кнопку Регистрации для старта.",
            reply_markup=start_registr_markup()
        )
        await UserData.start.set()
    elif message.from_user.id in list(map(int, ADMIN_TG_ID.split())):
        await bot.send_message(
            message.from_user.id,
            text="Привет, Админ. Добро пожаловать в меню администратора",
            reply_markup=admin_main_markup(),
        )
    else:
        if not await check_user_in_ban(message):
            await bot.send_message(
                message.from_user.id,
                text="Нажмите кнопку Меню и выберите из доступных вариантов",
                reply_markup=main_markup(),
            )
        else:
            await bot.send_message(
                message.from_user.id,
                text="К сожалению вы нарушили наши правила и попали в бан. "
                     "Для решения данного вопроса просим обратиться к "
                     "администратору @Loravel",
                reply_markup=ReplyKeyboardRemove()
            )
            await BannedState.start.set()