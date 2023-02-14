from aiogram import types
from sqlalchemy import exists, and_

from base_and_services.db_loader import db_session
from base_and_services.models import BanList
from handlers.user.get_info_from_table import get_id_from_user_info_table
from loader import db_controller


async def check_user_in_ban(message: types.Message):
    """Проверка пользователя в бан листе."""
    user_id = get_id_from_user_info_table(message.from_user.id)
    if await check_id_in_ban_with_status(user_id, 1):
        return True
    return False


async def check_id_in_ban_with_status(user_id, status):
    """Проверяем пользователя на наличие в бане с определенным статусом."""
    is_exist = db_session.query(exists().where(
        and_(BanList.banned_user_id == user_id, BanList.ban_status == status)
    )).scalar()
    if not is_exist:
        return False
    return True
