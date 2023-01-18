from asyncio import sleep
from datetime import date, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotBlocked
from loader import bot, db_controller, logger

from .new_member import get_id_from_user_info_table


async def check_message(state: FSMContext):
    """Рассылка проверочного сообщения по всем пользователям."""
    logger.info("Запуск проверки пользователей")
    await state.reset_state()
    for user in prepare_user_list():
        await send_message(
            teleg_id=user,
            text="Совсем скоро будет произведено распределение пар",
        )
        await sleep(0.05)
    logger.info("Все пользователи проверены.")


def prepare_user_list():
    """Подготовка списка id пользователей со статусом готов к встрече."""
    logger.info("""Подготавливаем список пользователей из базы""")
    query = """SELECT user_info.teleg_id FROM user_status 
    JOIN user_info ON user_info.id = user_status.id 
    WHERE user_status.status = 1 """
    data = db_controller.select_query(query).fetchall()
    return [element[0] for element in data]


async def send_message(teleg_id, **kwargs):
    """Отправка проверочного сообщения и обработка исключений."""
    try:
        await bot.send_message(teleg_id, **kwargs)
    except BotBlocked:
        logger.error(f"Невозможно доставить сообщение пользователю {teleg_id}."
                     f"Бот заблокирован.")
        await change_status(teleg_id)
    except Exception as error:
        logger.error(f"Невозможно доставить сообщение пользователю {teleg_id}."
                     f"{error}")


async def change_status(teleg_id):
    """Смена статуса участия."""
    user_id = get_id_from_user_info_table(teleg_id)
    queries = {
        """UPDATE user_status SET status = 0 WHERE id =?""": (user_id,),
        """UPDATE holidays_status SET status = 1, till_date = ? 
        WHERE id = ? """: (str(date.today() + timedelta(days=6)), user_id)
    }
    for query, values in queries.items():
        db_controller.query(query, values)
