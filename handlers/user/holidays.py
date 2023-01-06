import sqlite3
from datetime import date, timedelta, datetime
from aiogram import types

from loader import bot, dp, logger

from keyboards.user import *


@dp.callback_query_handler(text=set_holiday_message)
async def check_and_choice_holidays(message: types.Message):
    """Проверка и выбор срока каникул"""
    logger.info(f"Пользователь с TG_ID {message.from_user.id} "
                f"перешел к установке срока каникул")
    await check_holidays_until(message.from_user.id)
    await bot.send_message(
        message.from_user.id,
        text=f'Выберите на какой срок выхотите установить каникулы',
        reply_markup=holidays_length()
    )


@dp.callback_query_handler(text="one_week_holidays")
async def get_one_week_holidays(message: types.Message):
    """Установка каникул на 1 неделю"""
    date_to_return = str(date.today() + timedelta(days=7))
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id,
        text=f'Вы установили каникулы до {date_to_return}'
    )


@dp.callback_query_handler(text="two_week_holidays")
async def get_two_week_holidays(message: types.Message):
    """Установка каникул на 2 недели"""
    date_to_return = str(date.today() + timedelta(days=14))
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id,
        text=f'Вы установили каникулы до {date_to_return}'
    )


@dp.callback_query_handler(text="three_week_holidays")
async def get_three_week_holidays(message: types.Message):
    """Установка каникул на 3 недели"""
    date_to_return = str(date.today() + timedelta(days=21))
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id,
        text=f'Вы установили каникулы до {date_to_return}'
    )


@dp.callback_query_handler(text="cancel_holidays")
async def cancel_holidays(message: types.Message):
    """Отключение режима каникул"""
    conn = sqlite3.connect('data/coffee_database.db')
    cur = conn.cursor()
    id_obj = cur.execute(
        """SELECT id FROM user_info WHERE teleg_id=?""", (message.from_user.id,)
    )
    teleg_id = id_obj.fetchone()[0]
    cur.execute(
        """update holidays_status SET status=?, till_date=? where id = ?""", (
            0,
            "null",
            teleg_id
        ))
    cur.execute("""UPDATE user_status SET status=? WHERE id = ? """, (
        1,
        teleg_id
    ))
    conn.commit()
    await bot.send_message(
        message.from_user.id,
        text=f'Режим каникул был отключен'
    )
    logger.info(f"Пользователь с TG_ID {message.from_user.id} "
                f"отключил режим каникул")


async def get_holidays(message: types.Message, date_to_return):
    """Запись данных о каникулах в БД"""
    conn = sqlite3.connect('data/coffee_database.db')
    cur = conn.cursor()
    id_obj = cur.execute(
        """SELECT id FROM user_info WHERE teleg_id=?""", (message.from_user.id,)
    )
    teleg_id = id_obj.fetchone()[0]
    cur.execute("""update holidays_status SET status=?, till_date=? 
                where id = ?""", (
            1,
            date_to_return,
            teleg_id,
        ))
    cur.execute("""UPDATE user_status SET status=? WHERE id = ? """, (
        0,
        teleg_id,
    ))
    conn.commit()
    logger.info(f"Пользователь с TG_ID {message.from_user.id} "
                f"установил режим каникул до {date_to_return}")


async def check_holidays_until(tg_id):
    """Проверка даты окончания каникул пользователя в БД"""
    conn = sqlite3.connect('data/coffee_database.db')
    cur = conn.cursor()
    id_obj = cur.execute(
        """SELECT id FROM user_info WHERE teleg_id=?""",
        (tg_id,)
    )
    info = cur.execute(
        """SELECT * FROM holidays_status WHERE id = ?""",
        (id_obj.fetchone()[0],)
    )
    row = info.fetchone()
    if row[1] == 0:
        pass
    else:
        await bot.send_message(
            tg_id,
            text=f'Каникулы установлены до {row[2]}.'
        )


async def sheduled_check_holidays():
    """Отключение режима каникул при окончании срока. Проверка по расписанию"""
    conn = sqlite3.connect('data/coffee_database.db')
    cur = conn.cursor()
    info = cur.execute(
        """SELECT * FROM holidays_status WHERE status = 1"""
    )

    data = info.fetchall()
    for row in data:
        date_obj = datetime.strptime(row[2], '%Y-%m-%d')
        date_obj = date_obj.date()
        if date_obj == date.today():
            id_obj = cur.execute(
                """SELECT teleg_id FROM user_info WHERE id=?""",
                (row[0],)
            )
            teleg_id = id_obj.fetchone()[0]
            cur.execute(
                """update holidays_status SET status=?, till_date=? 
                WHERE id=?""", (
                    0,
                    "null",
                    row[0]
                ))
            cur.execute("""UPDATE user_status SET status=? WHERE id = ?""", (
                1,
                row[0]
            ))
            conn.commit()
            await bot.send_message(
                teleg_id,
                text=f'Режим каникул был отключен'
            )
