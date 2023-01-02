import re

from datetime import datetime

from aiogram import types

from config.bot_config import bot


def validate_name(message):
    return re.fullmatch(
        r"^[a-яА-ЯЁёa-yA-Y]{1,100}$",
        message
    )


async def validate_birthday(message: types.Message):
    if re.fullmatch(
        r"^((0[1-9]|[12]\d)\.(0[1-9]|1[012])|30\.(0[13-9]|1[012])|31\.(0[13578]|1[02]))\.(19|20)\d\d$",
        message.text
    ):
        date_obj = datetime.strptime(message.text, '%d.%m.%Y')
        difference = datetime.now() - date_obj
        age = int(difference.days) / 365
        if age < 0:
            await bot.send_message(message.from_user.id,
                                   f'Вы что из будущего? Введите правильную дату рождения"')
            return False
        elif age > 120:
            await bot.send_message(message.from_user.id,
                                   f'Указанный возраст болеее 120 лет. Введите правильную дату рождения')
            return False
        return True
    await bot.send_message(message.from_user.id,
        f'Что то не так с введенными данными. Дата должно состоять из цифр и точек ДД.ММ.ГГГГ"')
    return False

