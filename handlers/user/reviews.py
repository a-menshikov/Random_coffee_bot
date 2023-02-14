import datetime

from aiogram import types
from sqlalchemy import and_, or_, desc

from base_and_services.db_loader import db_session
from base_and_services.models import MetInfo
from handlers.decorators import admin_handlers
from handlers.user.get_info_from_table import \
    get_teleg_id_from_user_info_table, \
    get_id_from_user_info_table
from keyboards.admin import review_messages
from keyboards.user import review_markup, skip_message, menu_markup
from loader import bot, dp, logger
from states import ReviewState


@dp.message_handler(text=review_messages)
@admin_handlers
async def start_review(message: types.Message):
    """Запускаем процесс сбора отзывов."""
    logger.info("Подготавливаем список ID для запроса отзыва.")
    users_id = set(preparing_list_of_users_id())
    if len(users_id) > 0:
        await request_review(users_id)
    else:
        await bot.send_message(message.from_user.id,
                               "На этой неделе не было встреч.")


async def request_review(users_id):
    """Отправка сообщений запросов по прошедшей встрече."""
    logger.info("Начинаем процесс рассылки сообщений для отзыва")
    for user_id in users_id:
        user_teleg_id = get_teleg_id_from_user_info_table(user_id)
        try:
            await bot.send_message(
                user_teleg_id,
                "Пожалуйста оцените вашу встречу:\n"
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
    """Получаем отзыв и записываем в базу."""
    answer = message.text
    if answer != skip_message:
        await save_review(message.from_user.id, answer)
        try:
            await bot.send_message(
                message.from_user.id,
                f"Спасибо за отзыв. Его текст\n"
                f"{answer}\n"
                f"будет записан в базу",
                reply_markup=menu_markup(message)
            )
        except Exception as error:
            logger.error(f"Сообщение пользователю c {message.from_user.id} "
                         f"не доставлено. {error}")
            pass
    else:
        await bot.send_message(
            message.from_user.id,
            "Спасибо за ваш отзыв.",
            reply_markup=menu_markup(message)
        )
    await state.reset_state()


def preparing_list_of_users_id():
    """Выгрузка списка ID пользователей из
    таблицы проведенных встреч за неделю."""
    start_period = datetime.date.today() - datetime.timedelta(days=7)
    data = db_session.query(
        MetInfo.first_user_id,
        MetInfo.second_user_id
    ).filter(
        MetInfo.date.between(str(start_period), str(datetime.date.today))).all()
    logger.info("Список ID для рассылки на отзывы сформирован")
    return [element[0] for element in data] + [element[1] for element in data]


async def save_review(teleg_id, text):
    """Сохранние комментария в БД."""
    pass
    # user_id = get_id_from_user_info_table(teleg_id)
    # met_id = get_met_id_with_user_last_week(user_id)[0]
    # query = """INSERT INTO mets_reviews (met_id, user_id, comment)
    #         VALUES (?, ?, ?)"""
    # values = (met_id, user_id, text)
    # db_controller.query(query, values)
    # db_session.add(MetsReviews(met_id=met_id, ))


def get_met_id_with_user_last_week(user_id):
    """Получение id встречи по пользователю за прошедшую неделю."""
    start_period = datetime.date.today() - datetime.timedelta(days=7)
    met_id = db_session.query(MetInfo.id).filter(
        and_(MetInfo.date.between(str(start_period), str(datetime.date.today)),
             or_(
                 MetInfo.first_user_id == user_id,
                 MetInfo.second_user_id == user_id
             ))).order_by(desc(MetInfo.id)).limit(1).one()
    return met_id
