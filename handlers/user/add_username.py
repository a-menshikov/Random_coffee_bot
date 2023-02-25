from aiogram import types

from handlers.user.get_info_from_table import get_id_from_user_info_table


async def check_username(message: types.Message):
    user_id = get_id_from_user_info_table(message.from_user.id)
    username = message.from_user.username



