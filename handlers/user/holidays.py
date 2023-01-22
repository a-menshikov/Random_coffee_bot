from datetime import date, datetime, timedelta

from aiogram import types

from handlers.decorators import user_handlers
from handlers.user.get_info_from_table import *
from keyboards import one_week_holidays_message, two_week_holidays_message, \
    three_week_holidays_message, turn_off_holidays
from keyboards.user import holidays_length, set_holiday_message
from loader import bot, db_controller, dp, logger


@dp.message_handler(text=set_holiday_message)
@user_handlers
async def check_and_choice_holidays(message: types.Message):
    """Проверка и выбор срока каникул"""
    logger.info(f"Пользователь с TG_ID {message.from_user.id} "
                f"перешел к установке срока каникул")
    await check_holidays_until(message.from_user.id)
    await bot.send_message(
        message.from_user.id,
        text='Выберите на какой срок вы хотите установить каникулы',
        reply_markup=holidays_length()
    )


@dp.message_handler(text=one_week_holidays_message)
@user_handlers
async def get_one_week_holidays(message: types.Message):
    """Установка каникул на 1 неделю"""
    date_to_return = str(date.today() + timedelta(days=7))
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id,
        text=f'Вы установили каникулы до {date_to_return}'
    )


@dp.message_handler(text=two_week_holidays_message)
@user_handlers
async def get_two_week_holidays(message: types.Message):
    """Установка каникул на 2 недели"""
    date_to_return = str(date.today() + timedelta(days=14))
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id,
        text=f'Вы установили каникулы до {date_to_return}'
    )


@dp.message_handler(text=three_week_holidays_message)
@user_handlers
async def get_three_week_holidays(message: types.Message):
    """Установка каникул на 3 недели"""
    date_to_return = str(date.today() + timedelta(days=21))
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id,
        text=f'Вы установили каникулы до {date_to_return}'
    )


@dp.message_handler(text=turn_off_holidays)
@user_handlers
async def cancel_holidays(message: types.Message):
    """Отключение режима каникул"""
    user_id = get_id_from_user_info_table(message.from_user.id)
    queries = {
        """update holidays_status SET status=?, till_date=? where id = ?""":
            (0, "null", user_id),
        """UPDATE user_status SET status=? WHERE id = ? """: (1, user_id)
    }
    for query, values in queries.items():
        db_controller.query(query, values)
    await bot.send_message(
        message.from_user.id,
        text='Режим каникул был отключен'
    )
    logger.info(f"Пользователь с TG_ID {message.from_user.id} "
                f"отключил режим каникул")


async def get_holidays(message: types.Message, date_to_return):
    """Запись данных о каникулах в БД"""
    user_id = get_id_from_user_info_table(message.from_user.id)
    queries = {
        """UPDATE holidays_status SET status=?, till_date=? 
        WHERE id = ?""": (1, date_to_return, user_id),
        """UPDATE user_status SET status=? WHERE id = ? """: (0, user_id)
    }
    for query, values in queries.items():
        db_controller.query(query, values)
    logger.info(f"Пользователь с TG_ID {message.from_user.id} "
                f"установил режим каникул до {date_to_return}")


async def check_holidays_until(teleg_id):
    """Проверка даты окончания каникул пользователя в БД"""
    user_id = get_id_from_user_info_table(teleg_id)
    query = """SELECT * FROM holidays_status WHERE id = ?"""
    values = (user_id,)
    row = db_controller.select_query(query, values).fetchone()
    if row[1] == 0:
        pass
    else:
        await bot.send_message(
            teleg_id,
            text=f'Каникулы установлены до {row[2]}.'
        )


async def sheduled_check_holidays():
    """Отключение режима каникул при окончании срока. Проверка по расписанию"""
    query = """SELECT * FROM holidays_status WHERE status = 1"""
    data = db_controller.select_query(query).fetchall()
    for row in data:
        date_obj = datetime.strptime(row[2], '%Y-%m-%d')
        date_obj = date_obj.date()
        if date_obj == date.today():
            user_id = get_teleg_id_from_user_info_table(row[0])
            queries = {
                """update holidays_status SET status=?, till_date=? 
                WHERE id=?""": (0, "null", row[0]),
                """UPDATE user_status SET status=? WHERE id = ?""":
                    (1, row[0])
            }
            for query, values in queries.items():
                db_controller.query(query, values)
            await bot.send_message(
                user_id,
                text='Режим каникул был отключен'
            )
