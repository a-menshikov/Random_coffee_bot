import datetime

from aiogram import types
from aiogram.types import ReplyKeyboardRemove

from handlers.user import get_teleg_id_from_user_info_table
from keyboards import skip_message, main_markup, review_messages
from keyboards.user.review_markups import review_markup
from loader import db_controller, dp, bot, logger
from states import ReviewState, AdminData


@dp.message_handler(text=review_messages, state=AdminData.start)
async def start_review(message: types.Message):
    """Запускаем процесс сбора отзывов"""
    logger.info("Подготавливаем список ID для запроса отзыва.")
    users_id = set(preparing_list_of_users_id())
    if len(users_id) > 0:
        await request_review(users_id)
    else:
        await bot.send_message(message.from_user.id,
                               "На этой неделе не было встреч.")


async def request_review(users_id):
    """Отправка сообщений запросов по прошедшей встрече"""
    logger.info("Начинаем процесс рассылки сообщений для отзыва")
    for user_id in users_id:
        user_teleg_id = get_teleg_id_from_user_info_table(user_id)
        try:
            await bot.send_message(
                user_teleg_id,
                "Пожалуйста оцените Вашу встречу:\n"
                "(Вы можете выбрать из доступных вариантов "
                "или написать свой отзыв)",
                reply_markup=review_markup()
            )
            logger.info(f"Соообщение пользователю {user_teleg_id} "
                        f"для оценки встречи отправлено.")
        except Exception as error:
            logger.error(f"Сообщение пользователю c {user_teleg_id} "
                         f"не доставлено. {error}")
            continue
    await ReviewState.start.set()
    logger.info("Все сообщения разосланы")


@dp.message_handler(state=ReviewState.start)
async def review_answer(message: types.Message, state=ReviewState.start):
    """Получаем отзыв и записываем в базу"""
    answer = message.text
    if answer != skip_message:
        try:
            await bot.send_message(
                message.from_user.id,
                f"Спасибо за Ваш отзыв. Ваш отзыв \n"
                f"{answer}\n"
                f"будет записан в базу",
                reply_markup=main_markup()
            )
        except Exception as error:
            logger.error(f"Сообщение пользователю c {message.from_user.id} "
                         f"не доставлено. {error}")
            pass
    else:
        await bot.send_message(
            message.from_user.id,
            f"Спасибо за Ваш отзыв.",
            reply_markup=main_markup()
        )
    await state.reset_state()


def preparing_list_of_users_id():
    today = datetime.date.today()
    start_period = today - datetime.timedelta(days=7)
    query = """SELECT first_user_id, second_user_id 
    FROM met_info 
    WHERE date
    BETWEEN strftime('%d.%m.%Y', ?) AND strftime('%d.%m.%Y', ?)"""
    values = (start_period, today)
    data = db_controller.select_query(query, values).fetchall()
    logger.info("Список ID для рассылки на отзывы сформирован")
    return [element[0] for element in data] + [element[1] for element in data]
