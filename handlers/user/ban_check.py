from aiogram import types

from handlers.user import get_id_from_user_info_table
from loader import db_controller


async def check_user_in_ban(message: types.Message):
    """Проверка пользователя в бан листе."""
    user_id = get_id_from_user_info_table(message.from_user.id)
    if await check_id_in_ban_with_status(user_id, 1):
        return True
    return False


async def check_id_in_ban_with_status(user_id, status):
    """Проверяем пользователя на наличие в бане с определенным статусом."""
    query = """SELECT * FROM ban_list WHERE banned_user_id=? 
        AND ban_status = ?"""
    values = (user_id, status)
    info = db_controller.select_query(query, values)
    if info.fetchone() is None:
        return False
    return True
