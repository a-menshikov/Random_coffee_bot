import datetime

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from sqlalchemy import and_, desc, exists, or_

from controllerBD.db_loader import Session
from controllerBD.models import MetInfo, MetsReview
from handlers.decorators import admin_handlers
from handlers.user.get_info_from_table import (
    get_id_from_user_info_table,
    get_teleg_id_from_user_info_table,
)
from handlers.user.validators import (
    validate_about,
    validate_review_grade,
    validate_review_yes_or_no,
)
from keyboards.admin import review_messages
from keyboards.user import (
    menu_markup,
    no_button,
    review_skip,
    review_yes_or_no,
    skip_message,
    yes_button,
)
from loader import bot, logger
from states import ReviewState


# @dp.message_handler(text=review_messages)
@admin_handlers
async def start_review(message: types.Message):
    """Запускаем процесс сбора отзывов."""
    logger.info("Подготавливаем список ID для запроса отзыва.")
    users_id = set(preparing_list_of_users_id())
    if len(users_id) > 0:
        await request_review(users_id)
    else:
        await bot.send_message(message.from_user.id, "На этой неделе не было встреч.")


async def request_review(users_id):
    """Отправка сообщений запросов по прошедшей встрече."""
    logger.info("Начинаем процесс рассылки сообщений для отзыва")
    for user_id in users_id:
        user_teleg_id = get_teleg_id_from_user_info_table(user_id)
        try:
            await bot.send_message(
                user_teleg_id,
                "Состоялась ли твоя встреча?",
                reply_markup=review_yes_or_no(),
            )
            await ReviewState.start.set()
            logger.info(
                f"Сообщение пользователю {user_teleg_id} "
                f"для оценки встречи отправлено."
            )
        except Exception as error:
            logger.error(
                f"Сообщение пользователю c {user_teleg_id} " f"не доставлено. {error}"
            )
            continue
    logger.info("Все сообщения разосланы")


# @dp.message_handler(state=ReviewState.start)
async def review_answer_yes_or_now(message: types.Message, state: FSMContext):
    """Вопрос состоялась ли встреча."""
    answer = message.text
    if not await validate_review_yes_or_no(message):
        return
    if answer == skip_message:
        await bot.send_message(
            message.from_user.id,
            "Ты можешь оставить отзыв позже. "
            "Для этого нажми в главном меню кнопку Мои встречи.",
            reply_markup=menu_markup(message),
        )
        await state.reset_state()
        logger.info(
            f"Пользователь {message.from_user.id} отклонил " f"предоставление отзыва"
        )
    elif answer == no_button:
        await state.update_data(grade=0)
        await question_comment(message)
    elif answer == yes_button:
        await question_grade(message)


async def question_comment(message: types.Message):
    """Вопрос комментария к оценке."""
    await bot.send_message(
        message.from_user.id,
        "Пожалуйста, введи комментарий к оценке (не более 500 символов).",
        reply_markup=review_skip(),
    )
    await ReviewState.comment.set()


# @dp.message_handler(state=ReviewState.comment)
async def answer_review_comment(message: types.Message, state: FSMContext):
    """Получение комментария к оценке встречи."""
    if not await validate_about(message):
        return
    answer = message.text
    if answer == skip_message:
        answer = "null"
    await state.update_data(comment=answer)
    data = await state.get_data()
    if not data.get("user_id") or not data.get("met_id"):
        user_id = get_id_from_user_info_table(message.from_user.id)
        await state.update_data(user_id=user_id)
        met_id = get_met_id_with_user_last_week(user_id)[0]
        await state.update_data(met_id=met_id)
    await save_or_update_review(message, state)


async def question_grade(message: types.Message):
    """Вопрос предоставления оценки встречи."""
    await bot.send_message(
        message.from_user.id,
        "Оцени встречу от 1 до 5, где \n"
        "    - 1 - Совсем не понравилось,\n"
        "    - 5 - Все было супер.",
        reply_markup=review_skip(),
    )
    await ReviewState.grade.set()


# @dp.message_handler(state=ReviewState.grade)
async def answer_review_grade(message: types.Message, state: FSMContext):
    """Получение ответа по оценке встречи."""
    grade = message.text
    if grade == skip_message:
        await bot.send_message(
            message.from_user.id,
            "Ты можешь оставить отзыв позже. "
            "Для этого нажми в главном меню кнопку Мои встречи.",
            reply_markup=menu_markup(message),
        )
        await state.reset_state()
        logger.info(
            f"Пользователь {message.from_user.id} отклонил " f"предоставление отзыва"
        )
    elif not await validate_review_grade(grade):
        await bot.send_message(message.from_user.id, "Введи оценку от 1 до 5")
        return
    else:
        await state.update_data(grade=grade)
        await question_comment(message)


def preparing_list_of_users_id():
    """Выгрузка списка ID пользователей из
    таблицы проведенных встреч за неделю."""
    start_period = datetime.date.today() - datetime.timedelta(days=7)
    with Session() as db_session:
        data = (
            db_session.query(MetInfo.first_user_id, MetInfo.second_user_id)
            .filter(MetInfo.date.between(str(start_period), str(datetime.date.today)))
            .all()
        )
        logger.info("Список ID для рассылки на отзывы сформирован")
        return [element[0] for element in data] + [element[1] for element in data]


async def save_or_update_review(message, state):
    """Сохранение комментария в БД."""
    data = await state.get_data()
    user_id = data.get("user_id")
    met_id = data.get("met_id")
    grade = data.get("grade")
    comment = data.get("comment")
    if await check_comment_in_bd(user_id, met_id):
        update_review(user_id, met_id, grade, comment)
    else:
        add_review(user_id, met_id, grade, comment)
    await state.reset_state()
    await bot.send_message(
        message.from_user.id, "Спасибо за отзыв.", reply_markup=menu_markup(message)
    )


def get_met_id_with_user_last_week(user_id):
    """Получение id встречи по пользователю за прошедшую неделю."""
    start_period = datetime.date.today() - datetime.timedelta(days=7)
    with Session() as db_session:
        met_id = (
            db_session.query(MetInfo.id)
            .filter(
                and_(
                    MetInfo.date.between(str(start_period), str(datetime.date.today)),
                    or_(
                        MetInfo.first_user_id == user_id, MetInfo.second_user_id == user_id
                    ),
                )
            )
            .order_by(desc(MetInfo.id))
            .limit(1)
            .first()
        )
        return met_id


async def check_comment_in_bd(user_id, met_id):
    """Проверка наличия отзыва на встречу."""
    with Session() as db_session:
        is_exist = db_session.query(
            exists().where(and_(MetsReview.met_id == met_id, MetsReview.who_id == user_id))
        ).scalar()
        if not is_exist:
            return False
        return True


def update_review(user_id, met_id, grade, comment):
    """Обновление комментария о встрече."""
    with Session() as db_session:
        db_session.query(MetsReview).filter(
            and_(MetsReview.met_id == met_id, MetsReview.who_id == user_id)
        ).update(
            {
                "grade": grade,
                "comment": comment,
                "date_of_comment": str(datetime.date.today()),
            }
        )
        db_session.commit()
        logger.info(
            f"Пользователь с ID {user_id} " f"обновил комментарий о встрече {met_id}"
        )


def add_review(user_id, met_id, grade, comment):
    """Добавление комментария о встрече"""
    with Session() as db_session:
        users = db_session.query(MetInfo).filter(MetInfo.id == met_id).first().__dict__
        if users["first_user_id"] == user_id:
            about_whom_id = users["second_user_id"]
        else:
            about_whom_id = users["first_user_id"]
        db_session.add(
            MetsReview(
                met_id=met_id,
                who_id=user_id,
                about_whom_id=about_whom_id,
                grade=grade,
                comment=comment,
                date_of_comment=datetime.date.today(),
            )
        )
        db_session.commit()
        logger.info(
            f"Пользователь с ID {user_id} " f"добавил комментарий о встрече {met_id}"
        )


# def get_met_id_with_user_last_three(user_id):
#    """Получение id встречи по пользователю за прошедшую неделю."""
#    query = """SELECT id
#        FROM met_info
#        WHERE date
#        BETWEEN date('now', '-27 days') AND date('now')
#        AND (first_user_id = ? OR second_user_id = ?)
#        ORDER BY id DESC
#        LIMIT 3"""
#    values = (user_id, user_id)
#    mets_id = db_controller.select_query(query, values).fetchall()
#    return [met_id[0] for met_id in mets_id]


def register_review_handlers(dp: Dispatcher):
    dp.register_message_handler(start_review, text=review_messages)
    dp.register_message_handler(review_answer_yes_or_now, state=ReviewState.start)
    dp.register_message_handler(answer_review_comment, state=ReviewState.comment)
    dp.register_message_handler(answer_review_grade, state=ReviewState.grade)
