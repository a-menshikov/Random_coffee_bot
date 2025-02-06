import re

from aiogram import types
from sqlalchemy import exists

from controllerBD.db_loader import Session
from controllerBD.models import Users
from handlers.user.ban_check import check_id_in_ban_with_status
from loader import bot, logger


async def comment_validator(text):
    """Валидация поля комментария."""
    if 10 <= len(text) <= 500:
        return True
    return False


async def ban_validator(message: types.Message):
    """Валидация id пользователя для добавления в бан."""
    if re.fullmatch(r"^\d{1,10}$", message.text):
        if await check_id_in_base(message.text):
            if not await check_id_in_ban_with_status(message.text, 1):
                logger.info("Валидация пройдена.")
                return True
            await bot.send_message(message.from_user.id, "Пользователь уже забаннен.")
            return False
        await bot.send_message(
            message.from_user.id, "Пользователя с таким id не существует."
        )
        return False
    await bot.send_message(message.from_user.id, "Неверный ввод, введите число.")
    return False


async def unban_validator(message: types.Message):
    """Валидация id пользователя для вывода из бана."""
    if re.fullmatch(r"^\d{1,10}$", message.text):
        if await check_id_in_base(message.text):
            if await check_id_in_ban_with_status(message.text, 1):
                logger.info("Валидация пройдена.")
                return True
            await bot.send_message(message.from_user.id, "Пользователь не забаннен.")
            return False
        await bot.send_message(
            message.from_user.id, "Пользователя с таким id не существует."
        )
        return False
    await bot.send_message(message.from_user.id, "Неверный ввод, введите число.")
    return False


async def check_id_in_base(user_id):
    """Проверяем пользователя на наличие в БД."""
    with Session() as db_session:
        is_exist = db_session.query(exists().where(Users.id == user_id)).scalar()
        if not is_exist:
            return False
        return True
