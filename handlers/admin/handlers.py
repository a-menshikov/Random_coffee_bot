from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotBlocked

from controllerBD.db_loader import db_session
from controllerBD.models import UserStatus
from controllerBD.services import get_user_count_from_db
from handlers.admin.admin_report import prepare_user_info, \
    prepare_report_message
from handlers.decorators import admin_handlers
from handlers.user.check_message import check_message, prepare_user_list, \
    send_message
from handlers.user.get_info_from_table import get_id_from_user_info_table
from keyboards.admin import admin_menu_button, admin_menu_markup, go_back, \
    inform, admin_cancel_markup, change_status, admin_change_status_markup, \
    take_part_button, do_not_take_part_button, algo_start, \
    send_message_to_all_button, cancel, admin_inform_markup, \
    inform_active_users, inform_bad_users
from loader import bot, dp, logger
from match_algoritm import MachingHelper
from states import AdminData


@dp.message_handler(text=go_back)
@admin_handlers
async def go_back(message: types.Message):
    """Возврат в меню админа."""
    await admin_menu(message)


@dp.message_handler(text=admin_menu_button)
@admin_handlers
async def admin_menu(message: types.Message):
    """Вывод меню администратора."""
    await bot.send_message(
        message.from_user.id,
        text="Выберите из доступных вариантов:",
        reply_markup=admin_menu_markup()
    )


@dp.message_handler(text=inform)
@admin_handlers
async def inform_message(message: types.Message):
    """Вывод отчета."""
    await bot.send_message(
        message.from_user.id,
        "Выберите из доступных вариантов:",
        reply_markup=admin_inform_markup()
    )

@dp.message_handler(text=inform_active_users)
@admin_handlers
async def inform_message_1(message: types.Message):
    """Вывод отчета."""
    users = get_user_count_from_db()
    await bot.send_message(
        message.from_user.id,
        f"Всего пользователей - {users['all_users']};\n\n"
        f"Активных пользователей - {users['active_users']}."
    )

@dp.message_handler(text=inform_bad_users)
@admin_handlers
async def inform_message_2(message: types.Message):
    bad_users = prepare_user_info()
    message_text = prepare_report_message(bad_users)
    await bot.send_message(
        message.from_user.id,
        f"{message_text}",
        parse_mode="HTML"
    )


@dp.message_handler(text=change_status)
@admin_handlers
async def change_status_message(message: types.Message):
    """Вывод отчета."""
    await bot.send_message(
        message.from_user.id,
        "Выберите вариант:",
        reply_markup=admin_change_status_markup()
    )


@dp.message_handler(text=take_part_button)
@admin_handlers
async def take_part_yes(message: types.Message):
    """Изменение статуса на принимать участие."""
    change_admin_status(message, 1)
    await bot.send_message(
        message.from_user.id,
        "Теперь вы участвуете в распределении."
    )


@dp.message_handler(text=do_not_take_part_button)
@admin_handlers
async def take_part_no(message: types.Message):
    """Изменение статуса на не принимать участие."""
    change_admin_status(message, 0)
    await bot.send_message(
        message.from_user.id,
        "Вы изменили статус и теперь не участвуете в распределении."
    )


@dp.message_handler(text=algo_start)
@admin_handlers
async def start_algoritm(message: types.Message):
    """Запуск алгоритма распределения"""
    await check_message()
    mc = MachingHelper()
    res = mc.start()
    await mc.send_and_write(res)


def change_admin_status(message: types.Message, status):
    user_id = get_id_from_user_info_table(message.from_user.id)
    db_session.query(UserStatus).filter(UserStatus.id == user_id). \
        update({'status': status})


@dp.message_handler(text=send_message_to_all_button)
@admin_handlers
async def request_message_to_all(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Введите сообщение которое будет отправлено всем пользователям",
        reply_markup=admin_cancel_markup()
    )
    await AdminData.message_send.set()


@dp.message_handler(state=AdminData.message_send,
                    content_types=types.ContentTypes.ANY)
async def get_message_and_send(message: types.Message, state=FSMContext):
    logger.info("Запуск отправки сообщений всем пользователям")
    user_list = prepare_user_list()
    if message.photo:
        message_answer = message.photo[-1].file_id
        message_caption = message.caption
        try:
            for user in user_list:
                await send_photo(
                    teleg_id=user,
                    photo=message_answer,
                    caption=message_caption
                )
                await sleep(0.05)
        except TypeError:
            logger.error("Список пользователей пуст")
        except Exception as er:
            logger.error(f"Ошибка отправки: {er}")
        finally:
            await bot.send_message(
                message.from_user.id,
                "Сообщения отправлены",
                reply_markup=admin_menu_markup()
            )
    elif message.content_type == 'text':
        message_answer = message.text
        if message_answer == cancel:
            await admin_menu(message)
        else:
            try:
                for user in user_list:
                    await send_message(
                        teleg_id=user,
                        text=message_answer,
                    )
                    await sleep(0.05)
            except TypeError:
                logger.error("Список пользователей пуст")
            except Exception as er:
                logger.error(f"Ошибка отправки: {er}")
            finally:
                await bot.send_message(
                    message.from_user.id,
                    "Сообщения отправлены",
                    reply_markup=admin_menu_markup()
                )
                logger.info("Сообщения пользователям доставлены.")
    else:
        await message.answer("Данный тип сообщения я обработать не могу",
                             reply_markup=admin_menu_markup())
    await state.finish()


async def send_photo(teleg_id, **kwargs):
    """Отправка проверочного сообщения и обработка исключений."""
    try:
        await bot.send_photo(teleg_id, **kwargs)
    except BotBlocked:
        logger.error(f"Невозможно доставить сообщение пользователю {teleg_id}."
                     f"Бот заблокирован.")
        await change_status(teleg_id)
    except Exception as error:
        logger.error(f"Невозможно доставить сообщение пользователю {teleg_id}."
                     f"{error}")
