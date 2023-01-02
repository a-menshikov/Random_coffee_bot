import sqlite3
from datetime import date, timedelta, datetime
from aiogram import types

from config.bot_config import dp, bot
from handlers.users_handlers.handlers import question_about_take_part


@dp.message_handler(commands=['holidays'])
async def get_holidays(message: types.Message):
    await check_holidays_until(message.from_user.id)
    await bot.send_message(
        message.from_user.id,
        text=f'Выберите на какой срок выхотите установить каникулы',
        reply_markup=keyboard_get_holidays
    )

keyboard_get_holidays = types.InlineKeyboardMarkup()

one_week_holidays = types.InlineKeyboardButton(
    '1 неделя',
    callback_data='one_week_holidays'
)
two_week_holidays = types.InlineKeyboardButton(
    '2 недели',
    callback_data='two_week_holidays'
)
three_week_holidays = types.InlineKeyboardButton(
    '3 недели',
    callback_data='three_week_holidays'
)
cancel_holidays = types.InlineKeyboardButton(
    'Отмена',
    callback_data='cancel_holidays'
)
keyboard_get_holidays.row(one_week_holidays, two_week_holidays)
keyboard_get_holidays.row(three_week_holidays, cancel_holidays)

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
    conn = sqlite3.connect('random_coffee.db')
    cur = conn.cursor()
    cur.execute(
        """update users SET holidays = ?, holidays_until = ? where tg_id = ?""",
        (
            0,
            'null',
            message.from_user.id
        ))
    conn.commit()
    await bot.send_message(
        message.from_user.id,
        text=f'Режим каникул был отключен'
    )
    await question_about_take_part(message.from_user.id)

async def get_holidays(message: types.Message, date_to_return):
    conn = sqlite3.connect('random_coffee.db')
    cur = conn.cursor()
    cur.execute("""update users SET take_part = ?, holidays = ?, holidays_until = ? where tg_id = ?""", (
        0,
        1,
        date_to_return,
        message.from_user.id
    ))
    conn.commit()

async def check_holidays_until(tg_id):
    conn = sqlite3.connect('random_coffee.db')
    cur = conn.cursor()
    info = cur.execute(
        """SELECT * FROM users WHERE tg_id=?""", (tg_id,)
    )
    conn.commit()
    row = info.fetchone()
    if row[4] == 0:
        # Делаем когда нету человека в бд
        pass
    else:
        await bot.send_message(
            tg_id,
            text=f'Каникулы установлены до {row[5]}.'
        )

async def sheduled_check_holidays():
    conn = sqlite3.connect('random_coffee.db')
    cur = conn.cursor()
    info = cur.execute(
        """SELECT * FROM users WHERE holidays = 1"""
    )

    data = info.fetchall()
    for row in data:
        date_obj = datetime.strptime(row[5], '%Y-%m-%d')
        date_obj = date_obj.date()
        if date_obj == date.today():
            cur.execute(
                """update users SET holidays = ?, holidays_until = ? where tg_id = ?""",
                (
                    0,
                    'null',
                    row[0]
                ))
            conn.commit()
            await bot.send_message(
                row[0],
                text=f'Режим каникул был отключен'
            )
            await question_about_take_part(row[0])
