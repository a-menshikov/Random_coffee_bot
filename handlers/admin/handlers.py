from asyncio import sleep

from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.utils.exceptions import BotBlocked

from controllerBD.db_loader import Session
from controllerBD.models import UserStatus
from controllerBD.services import get_user_count_from_db, get_active_user_names_from_db
from handlers.admin.admin_report import prepare_report_message, prepare_user_info
from handlers.decorators import admin_handlers
from handlers.user.check_message import prepare_user_list, send_message
from handlers.user.get_info_from_table import get_id_from_user_info_table
from keyboards.admin import (
    admin_cancel_markup,
    admin_change_status_markup,
    admin_inform_markup,
    admin_menu_button,
    admin_menu_markup,
    admin_pair_generation_markup,
    cancel,
    change_pair_generation_date,
    change_status,
    do_not_take_part_button,
    force_pair_generation,
    go_back,
    inform,
    inform_active_users,
    inform_bad_users,
    pair_generation,
    renew_pair_generation,
    send_message_to_all_button,
    stop_pair_generation,
    take_part_button,
)
from loader import bot, logger
from match_algoritm.MatchingHelper import start_algoritm
from states import AdminData


@admin_handlers
async def go_back_message(message: types.Message):
    """Возврат в меню админа."""
    await admin_menu(message)


@admin_handlers
async def admin_menu(message: types.Message):
    """Вывод меню администратора."""
    await bot.send_message(
        message.from_user.id,
        text="Выберите из доступных вариантов:",
        reply_markup=admin_menu_markup(),
    )


@admin_handlers
async def inform_message(message: types.Message):
    """Вывод отчета."""
    await bot.send_message(
        message.from_user.id,
        "Выберите из доступных вариантов:",
        reply_markup=admin_inform_markup(),
    )


@admin_handlers
async def inform_message_1(message: types.Message):
    """Вывод сообщения со списком активных пользователей."""
    users_count = get_user_count_from_db()
    await bot.send_message(
        message.from_user.id,
        f"Всего пользователей - {users_count['all_users']};\n\n"
        f"Активных пользователей - {users_count['active_users']}.",
    )
    active_users = get_active_user_names_from_db()
    for user in active_users:
        await bot.send_message(
            message.from_user.id,
            f"Имя: {user['name']}\n"
            f"Телеграм: @{user['tg_username']}",
        )


@admin_handlers
async def inform_message_2(message: types.Message):
    """Получение сообщения о пользователях со штрафными балами."""
    bad_users = prepare_user_info()
    message_list = prepare_report_message(bad_users)
    if message_list[0] == "":
        await bot.send_message(message.from_user.id, "Отчёт пустой")
    else:
        for message_text in message_list:
            await bot.send_message(
                message.from_user.id, f"{message_text}", parse_mode="HTML"
            )


@admin_handlers
async def change_status_message(message: types.Message):
    """Вывод отчета."""
    await bot.send_message(
        message.from_user.id,
        "Выберите вариант:",
        reply_markup=admin_change_status_markup(),
    )


@admin_handlers
async def pairs_config_message(message: types.Message):
    """Вывод кнопок настроек генерации пар."""
    await bot.send_message(
        message.from_user.id,
        "Выберите вариант:",
        reply_markup=admin_pair_generation_markup(),
    )


@admin_handlers
async def stop_generation(message: types.Message):
    """Остановить генерацию пар."""
    await bot.send_message(
        message.from_user.id,
        "Данный функционал пока что не реализован :)",
        reply_markup=admin_pair_generation_markup(),
    )


@admin_handlers
async def renew_generation(message: types.Message):
    """Возобновить генерацию пар."""
    await bot.send_message(
        message.from_user.id,
        "Данный функционал пока что не реализован :)",
        reply_markup=admin_pair_generation_markup(),
    )


@admin_handlers
async def change_generation_date(message: types.Message):
    """Изменить день недели и время генерации пар."""
    await bot.send_message(
        message.from_user.id,
        "Данный функционал пока что не реализован :)",
        reply_markup=admin_pair_generation_markup(),
    )


@admin_handlers
async def generate_pairs(message: types.Message):
    """Сгенерировать пары вручную."""
    await start_algoritm()
    await bot.send_message(
        message.from_user.id,
        "Пары успешно сгенерированы!",
        reply_markup=admin_pair_generation_markup(),
    )


@admin_handlers
async def take_part_yes(message: types.Message):
    """Изменение статуса на принимать участие."""
    change_admin_status(message, 1)
    await bot.send_message(
        message.from_user.id, "Теперь вы участвуете в распределении."
    )


@admin_handlers
async def take_part_no(message: types.Message):
    """Изменение статуса на не принимать участие."""
    change_admin_status(message, 0)
    await bot.send_message(
        message.from_user.id,
        "Вы изменили статус и теперь не участвуете в распределении.",
    )


def change_admin_status(message: types.Message, status):
    with Session() as db_session:
        user_id = get_id_from_user_info_table(message.from_user.id)
        db_session.query(UserStatus).filter(UserStatus.id == user_id).update(
            {"status": status}
        )


@admin_handlers
async def request_message_to_all(message: types.Message):
    await bot.send_message(
        message.from_user.id,
        "Введите сообщение которое будет отправлено всем пользователям",
        reply_markup=admin_cancel_markup(),
    )
    await AdminData.message_send.set()


async def get_message_and_send(message: types.Message, state=FSMContext):
    logger.info("Запуск отправки сообщений всем пользователям")
    user_list = prepare_user_list()
    if message.photo:
        message_answer = message.photo[-1].file_id
        message_caption = message.caption
        try:
            for user in user_list:
                await send_photo(
                    teleg_id=user, photo=message_answer, caption=message_caption
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
                reply_markup=admin_menu_markup(),
            )
    elif message.content_type == "text":
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
                    reply_markup=admin_menu_markup(),
                )
                logger.info("Сообщения пользователям доставлены.")
    else:
        await message.answer(
            "Данный тип сообщения я обработать не могу",
            reply_markup=admin_menu_markup(),
        )
    await state.finish()


async def send_photo(teleg_id, **kwargs):
    """Отправка проверочного сообщения и обработка исключений."""
    try:
        await bot.send_photo(teleg_id, **kwargs)
    except BotBlocked:
        logger.error(
            f"Невозможно доставить сообщение пользователю {teleg_id}."
            f"Бот заблокирован."
        )
        await change_status(teleg_id)
    except Exception as error:
        logger.error(
            f"Невозможно доставить сообщение пользователю {teleg_id}." f"{error}"
        )


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(go_back_message, text=go_back)
    dp.register_message_handler(admin_menu, text=admin_menu_button)
    dp.register_message_handler(inform_message, text=inform)
    dp.register_message_handler(inform_message_1, text=inform_active_users)
    dp.register_message_handler(inform_message_2, text=inform_bad_users)
    dp.register_message_handler(change_status_message, text=change_status)
    dp.register_message_handler(pairs_config_message, text=pair_generation)
    dp.register_message_handler(take_part_yes, text=take_part_button)
    dp.register_message_handler(take_part_no, text=do_not_take_part_button)
    dp.register_message_handler(generate_pairs, text=force_pair_generation)
    dp.register_message_handler(stop_generation, text=stop_pair_generation)
    dp.register_message_handler(renew_generation, text=renew_pair_generation)
    dp.register_message_handler(
        change_generation_date, text=change_pair_generation_date
    )
    dp.register_message_handler(request_message_to_all, text=send_message_to_all_button)
    dp.register_message_handler(
        get_message_and_send,
        state=AdminData.message_send,
        content_types=types.ContentTypes.ANY,
    )
