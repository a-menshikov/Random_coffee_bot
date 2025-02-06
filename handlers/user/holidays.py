from datetime import date, timedelta

from aiogram import types
from aiogram.dispatcher import Dispatcher
from sqlalchemy import and_

from controllerBD.db_loader import Session
from controllerBD.models import Holidays, UserStatus
from handlers.decorators import user_handlers
from handlers.user.check_message import send_message
from handlers.user.get_info_from_table import (
    get_id_from_user_info_table,
    get_teleg_id_from_user_info_table,
)
from handlers.user.work_with_date import date_from_db_to_message
from keyboards.user import (
    holidays_length,
    one_week_holidays_message,
    set_holiday_message,
    three_week_holidays_message,
    turn_off_holidays,
    two_week_holidays_message,
)
from loader import bot, logger


# @dp.message_handler(text=set_holiday_message)
@user_handlers
async def check_and_choice_holidays(message: types.Message):
    """Проверка и выбор срока каникул"""
    logger.info(
        f"Пользователь с TG_ID {message.from_user.id} "
        f"перешел к установке срока каникул"
    )
    await check_holidays_until(message.from_user.id)
    await bot.send_message(
        message.from_user.id,
        text="Выбери на какой срок ты хочешь установить каникулы",
        reply_markup=holidays_length(),
    )


def message_for_holidays(date_to_return):
    return (
        f"Ты установил каникулы до "
        f'{date_to_return.strftime("%d.%m.%Y")} '
        f"и начнёшь участвовать в "
        f"распределении с "
        f'{(date_to_return + timedelta(days=1)).strftime("%d.%m.%Y")}.'
    )


# @dp.message_handler(text=one_week_holidays_message)
@user_handlers
async def get_one_week_holidays(message: types.Message):
    """Установка каникул на 1 неделю"""
    date_to_return = date.today() + timedelta(days=7)
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id, text=message_for_holidays(date_to_return)
    )


# @dp.message_handler(text=two_week_holidays_message)
@user_handlers
async def get_two_week_holidays(message: types.Message):
    """Установка каникул на 2 недели"""
    date_to_return = date.today() + timedelta(days=14)
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id, text=message_for_holidays(date_to_return)
    )


# @dp.message_handler(text=three_week_holidays_message)
@user_handlers
async def get_three_week_holidays(message: types.Message):
    """Установка каникул на 3 недели"""
    date_to_return = date.today() + timedelta(days=21)
    await get_holidays(message, date_to_return)
    await bot.send_message(
        message.from_user.id, text=message_for_holidays(date_to_return)
    )


# @dp.message_handler(text=turn_off_holidays)
@user_handlers
async def cancel_holidays(message: types.Message):
    """Отключение режима каникул"""
    with Session() as db_session:
        user_id = get_id_from_user_info_table(message.from_user.id)
        db_session.query(Holidays).filter(Holidays.id == user_id).update(
            {"status": 0, "till_date": "null"}
        )
        db_session.query(UserStatus).filter(UserStatus.id == user_id).update({"status": 1})
        db_session.commit()
        await bot.send_message(message.from_user.id, text="Режим каникул был отключен")
        logger.info(
            f"Пользователь с TG_ID {message.from_user.id} " f"отключил режим каникул"
        )


async def get_holidays(message: types.Message, date_to_return):
    """Запись данных о каникулах в БД"""
    with Session() as db_session:
        user_id = get_id_from_user_info_table(message.from_user.id)
        db_session.query(Holidays).filter(Holidays.id == user_id).update(
            {"status": 1, "till_date": str(date_to_return)}
        )
        db_session.query(UserStatus).filter(UserStatus.id == user_id).update({"status": 0})
        db_session.commit()
        logger.info(
            f"Пользователь с TG_ID {message.from_user.id} "
            f"установил режим каникул до {date_to_return}"
        )


async def check_holidays_until(teleg_id):
    """Проверка даты окончания каникул пользователя в БД"""
    with Session() as db_session:
        user_id = get_id_from_user_info_table(teleg_id)
        row = db_session.query(Holidays).filter(Holidays.id == user_id).first().__dict__
        if row["status"] == 0:
            pass
        else:
            await bot.send_message(
                teleg_id,
                text=f"Каникулы установлены до "
                f'{date_from_db_to_message(row["till_date"])}.\n'
                f"Ты начнешь участвовать в распределении пар "
                f"со следующего дня.",
            )


async def sheduled_check_holidays():
    """Отключение режима каникул при окончании срока. Проверка по расписанию"""
    logger.info("Начало автопроверки статуса каникул")
    with Session() as db_session:
        data = (
            db_session.query(Holidays.id)
            .filter(and_(Holidays.status == 1, Holidays.till_date == str(date.today())))
            .all()
        )
        if data:
            for row in data:
                user_id = get_teleg_id_from_user_info_table(row[0])
                db_session.query(Holidays).filter(Holidays.id == row[0]).update(
                    {"status": 0, "till_date": "null"}
                )
                db_session.query(UserStatus).filter(UserStatus.id == row[0]).update(
                    {"status": 1}
                )
                db_session.commit()
                await send_message(teleg_id=user_id, text="Режим каникул был отключен")
                logger.info(f"Каникулы юзера {user_id} отключены автопроверкой")
        logger.info("Конец автопроверки статуса каникул")


def register_holidays_handlers(dp: Dispatcher):
    dp.register_message_handler(check_and_choice_holidays, text=set_holiday_message)
    dp.register_message_handler(get_one_week_holidays, text=one_week_holidays_message)
    dp.register_message_handler(get_two_week_holidays, text=two_week_holidays_message)
    dp.register_message_handler(
        get_three_week_holidays, text=three_week_holidays_message
    )
    dp.register_message_handler(cancel_holidays, text=turn_off_holidays)
