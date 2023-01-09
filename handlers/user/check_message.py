from asyncio import sleep

from aiogram import types
from aiogram.utils.exceptions import BotBlocked

from loader import bot, dp, db_controller, logger


@dp.message_handler(commands=['check'])
async def check_message(message: types.Message):
    await sleep(10)
    for user in prepare_user_list():
        await send_message(
            teleg_id=user,
            text="Через несколько минут будем произведена рассылка"
        )


def prepare_user_list():
    query = """SELECT user_info.teleg_id FROM user_status 
    JOIN user_info ON user_info.id = user_status.id 
    WHERE user_status.status = 1 """
    data = db_controller.select_query(query).fetchall()
    return [element[0] for element in data]


async def send_message(teleg_id, **kwargs):
    try:
        await bot.send_message(teleg_id, **kwargs)
    except BotBlocked:
        logger.error(f"Не возможно доставить сообщение пользователю {teleg_id}."
                     f"Бот заблокирован.")
        await change_status(teleg_id)
    except Exception as error:
        logger.error(f"Не возможно доставить сообщение пользователю {teleg_id}."
                     f"{error}")


async def change_status(teleg_id):
    query_id = """SELECT id FROM user_info WHERE teleg_id=?"""
    values_id = (teleg_id,)
    id_obj = db_controller.select_query(query_id, values_id)
    user_id = id_obj.fetchone()[0]
    query = """UPDATE user_status SET status = 0
        WHERE id = ? """
    values = (user_id,)
    db_controller.query(query, values)
