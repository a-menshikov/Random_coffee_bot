from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from handlers.decorators import user_handlers
from handlers.user.get_info_from_table import get_id_from_user_info_table, \
    get_user_info_by_id
from handlers.user.work_with_date import date_from_db_to_message
from keyboards.user import review_yes_or_no, my_reviews
from loader import dp, bot, db_controller
from states import ReviewState

review_callbackdata = CallbackData("dun_w", "position", "edit")


def list_of_user_mets_id(user_id):
    """Получение id всех встреч пользователя."""
    query = """SELECT id 
        FROM met_info 
        WHERE first_user_id = ? OR second_user_id = ?
        ORDER BY id DESC
        LIMIT 10"""
    values = (user_id, user_id)
    met_ids = db_controller.select_query(query, values).fetchall()
    return [met_id[0] for met_id in met_ids]


@dp.message_handler(text=my_reviews)
@user_handlers
async def example(message: types.Message):
    user_id = get_id_from_user_info_table(message.from_user.id)
    met_ids = list_of_user_mets_id(user_id)
    count_of_mets = len(met_ids)
    if count_of_mets == 0:
        await bot.send_message(message.from_user.id,
                               "У тебя еще не было встреч.")
    else:
        met_id = met_ids[0]
        review_info = get_sqliterow_review(met_id, user_id)
        if review_info:
            edit_button = "Ред. отзыв"
        else:
            edit_button = "Доб. отзыв"
        message_text = prepare_message(user_id, met_id, review_info)
        await bot.send_message(message.from_user.id, message_text,
                               parse_mode='HTML',
                               reply_markup=inline_markup(count_of_mets, 0,
                                                          edit_button))


@dp.callback_query_handler(review_callbackdata.filter())
async def button_press(call: types.CallbackQuery, callback_data: dict,
                       state: FSMContext):
    position = int(callback_data.get('position'))
    user_id = get_id_from_user_info_table(call.from_user.id)
    met_ids = list_of_user_mets_id(user_id)
    count_of_mets = len(met_ids)
    met_id = met_ids[position]
    review_info = get_sqliterow_review(met_id, user_id)
    if review_info:
        edit_button = "Ред. отзыв"
    else:
        edit_button = "Доб. отзыв"
    if int(callback_data.get('edit')) == 1:
        await call.answer()
        await bot.edit_message_reply_markup(
            chat_id=call.from_user.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        await bot.send_message(
            call.from_user.id,
            "Состоялась ли твоя встреча?",
            reply_markup=review_yes_or_no()
        )
        await ReviewState.start.set()
        user_id = get_id_from_user_info_table(call.from_user.id)
        await state.update_data(user_id=user_id)
        await state.update_data(met_id=met_id)
    else:
        message_text = prepare_message(user_id, met_id, review_info)
        await bot.edit_message_text(message_text, call.from_user.id,
                                    call.message.message_id, parse_mode='HTML',
                                    reply_markup=inline_markup(count_of_mets,
                                                               position,
                                                               edit_button))


def inline_markup(count_of_mets, position, edit_button):
    markup = InlineKeyboardMarkup(row_width=3)
    if position < (count_of_mets - 1):
        markup.insert(InlineKeyboardButton(
            f"Пред.",
            callback_data=review_callbackdata.new(
                position=position+1,
                edit=0
            )))
    markup.insert(InlineKeyboardButton(
        f"{edit_button}",
        callback_data=review_callbackdata.new(
            position=position,
            edit=1
        )))
    if position > 0:
        markup.insert(InlineKeyboardButton(
            f"След.",
            callback_data=review_callbackdata.new(
                position=position-1,
                edit=0
            )))

    return markup


def prepare_message(user_id, met_id, review_info):
    met_info = get_sqliterow_about_met(met_id)
    date = date_from_db_to_message(met_info['date'])
    if met_info['first_user_id'] == user_id:
        pare_id = met_info['second_user_id']
    else:
        pare_id = met_info['first_user_id']
    pare_info = get_user_info_by_id(pare_id)
    if review_info:
        grade = review_info['grade']
        if grade == 0:
            grade_text = 'Встреча не состоялась.'
        else:
            grade_text = f"Оценка - {grade}."
        comment = review_info['comment']
        if comment == 'null':
            comment = 'Не указано'
        review = (
            f"    {grade_text}\n"
            f"    {comment}"
        )
    else:
        review = "Комментарий на встречу не был добавлен."

    message = (
        f"<b>Дата распределения</b> - {date}.\n"
        f"<b>Твоя пара</b> – <a href='tg://user?id={pare_info['teleg_id']}'>"
        f"{pare_info['name']}</a>\n\n"
        f"<b>Отзыв о встрече:</b>\n"
        f"{review}"

    )
    return message


def get_sqliterow_about_met(met_id):
    query = """SELECT * FROM met_info WHERE id = ?"""
    values = (met_id, )
    met_info = db_controller.row_factory(query, values).fetchone()
    return met_info


def get_sqliterow_review(met_id, user_id):
    query = """SELECT * FROM mets_reviews WHERE met_id = ? AND who_id = ?"""
    values = (met_id, user_id)
    review_info = db_controller.row_factory(query, values).fetchone()
    return review_info
