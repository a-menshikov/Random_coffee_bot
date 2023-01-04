import sqlite3
from datetime import date, timedelta, datetime
from aiogram import types

from data.config import dp, bot

from keyboards.user import *


@dp.callback_query_handler(text=set_holiday_message)
async def get_holidays(message: types.Message):
    await check_holidays_until(message.from_user.id)
    await bot.send_message(
        message.from_user.id,
        text=f'Выберите на какой срок выхотите установить каникулы',
        reply_markup=holidays_length()
    )

@dp.callback_query_handler(text="one_week_holidays")
async def get_one_week_holidays(message: types.Message):
    date_to_return = str(date.today() + timedelta(days=7))
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id,
        text=f'Вы установили каникулы до {date_to_return}'
    )

@dp.callback_query_handler(text="two_week_holidays")
async def get_two_week_holidays(message: types.Message):
    date_to_return = str(date.today() + timedelta(days=14))
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id,
        text=f'Вы установили каникулы до {date_to_return}'
    )

@dp.callback_query_handler(text="three_week_holidays")
async def get_three_week_holidays(message: types.Message):
    date_to_return = str(date.today() + timedelta(days=21))
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id,
        text=f'Вы установили каникулы до {date_to_return}'
    )

@dp.callback_query_handler(text="cancel_holidays")
async def cancel_holidays(message: types.Message):
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


async def get_holidays(message: types.Message, date_to_return):
    conn = sqlite3.connect('data/coffee_database.db')
    cur = conn.cursor()
    id_obj = cur.execute(
        """SELECT id FROM user_info WHERE teleg_id=?""", (message.from_user.id,)
    )
    teleg_id = id_obj.fetchone()[0]
    cur.execute("""update holidays_status SET status=?, till_date=? where id = ?""", (
        1,
        date_to_return,
        teleg_id,
    ))
    cur.execute("""UPDATE user_status SET status=? WHERE id = ? """, (
        0,
        teleg_id,
    ))
    conn.commit()

async def check_holidays_until(tg_id):
    conn = sqlite3.connect('data/coffee_database.db')
    cur = conn.cursor()
    id_obj = cur.execute(
        """SELECT id FROM user_info WHERE teleg_id=?""", (tg_id,)
    )
    info = cur.execute(
        """SELECT * FROM holidays_status WHERE id = ?""",(id_obj.fetchone()[0],)
    )
    row = info.fetchone()
    if row[1] == 0:
        # Делаем когда нету человека в бд
        pass
    else:
        await bot.send_message(
            tg_id,
            text=f'Каникулы установлены до {row[2]}.'
        )

async def sheduled_check_holidays():
    conn = sqlite3.connect('random_coffee.db')
    cur = conn.cursor()
    info = cur.execute(
        """SELECT * FROM holidays_status WHERE holidays = 1"""
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
            cur.execute(
                """update holidays_status SET status=?, till_date=?""",
                (
                    0,
                    "null"
                ))
            cur.execute("""UPDATE user_status SET status=? """, (
                1,
            ))
            conn.commit()
            await bot.send_message(
                id_obj.fetchone()[0],
                text=f'Режим каникул был отключен'
            )
