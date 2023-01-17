import re

from aiogram import types

from loader import db_controller, bot, logger


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
            await bot.send_message(
                message.from_user.id,
                "Пользователь уже забаннен."
            )
            return False
        await bot.send_message(
            message.from_user.id,
            "Пользователя с таким id не существует."
        )
        return False
    await bot.send_message(
        message.from_user.id,
        "Неверный ввод, введите число."
    )
    return False


async def unban_validator(message: types.Message):
    """Валидация id пользователя для вывода из бана."""
    if re.fullmatch(r"^\d{1,10}$", message.text):
        if await check_id_in_base(message.text):
            if await check_id_in_ban_with_status(message.text, 1):
                logger.info("Валидация пройдена.")
                return True
            await bot.send_message(
                message.from_user.id,
                "Пользователь не забаннен."
            )
            return False
        await bot.send_message(
            message.from_user.id,
            "Пользователя с таким id не существует."
        )
        return False
    await bot.send_message(
        message.from_user.id,
        "Неверный ввод, введите число."
    )
    return False


async def check_id_in_base(user_id):
    """Проверяем пользователя на наличие в БД."""
    query = """SELECT * FROM user_info WHERE id=?"""
    values = (user_id,)
    info = db_controller.select_query(query, values)
    if info.fetchone() is None:
        return False
    return True


async def check_id_in_ban_with_status(user_id, status):
    """Проверяем пользователя на наличие в бане с определенным статусом."""
    query = """SELECT * FROM ban_list WHERE banned_user_id=? 
    AND ban_status = ?"""
    values = (user_id, status)
    info = db_controller.select_query(query, values)
    if info.fetchone() is None:
        return False
    return True
