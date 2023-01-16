from aiogram import types

from handlers.admin import check_id_in_ban_with_status
from handlers.user import get_id_from_user_info_table
from loader import dp, bot
from states import BannedState


async def check_user_in_ban(message: types.Message):
    user_id = get_id_from_user_info_table(message.from_user.id)
    if await check_id_in_ban_with_status(user_id, 1):
        return True
    return False
