from asyncio import sleep
from datetime import date, timedelta

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotBlocked

from handlers.user import get_id_from_user_info_table
from keyboards import menu_markup
from loader import bot, dp, db_controller, logger
from states import AdminData


async def check_message(state: FSMContext):
    logger.info("Запуск проверки пользователей")
    await state.reset_state()
    for user in prepare_user_list():
        await send_message(
            teleg_id=user,
            text="Через несколько минут будем произведена рассылка",
        )
        await sleep(0.05)
    logger.info("Все пользователи проверены.")


def prepare_user_list():
    logger.info("""Подготавливаем список пользователей из базы""")
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
    user_id = get_id_from_user_info_table(teleg_id)
    queries = {
        """UPDATE user_status SET status = 0 WHERE id =?""": (user_id,),
        """UPDATE holidays_status SET status = 1, till_date = ? 
        WHERE id = ? """: (str(date.today() + timedelta(days=6)), user_id)
    }
    for query, values in queries.items():
        db_controller.query(query, values)
