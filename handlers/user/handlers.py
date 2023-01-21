from aiogram import types
from aiogram.dispatcher import FSMContext

from handlers.decorators import user_handlers
from handlers.user.get_info_from_table import (
    get_user_data_from_db,
    get_user_status_from_db,
    get_holidays_status_from_db
)
from keyboards.user import *
from loader import bot, dp, logger

from handlers.user.new_member import get_gender_from_db, start_registration


@dp.message_handler(text=[menu_message, back_to_menu])
@user_handlers
async def main_menu(message: types.Message):
    """Вывод меню"""
    await bot.send_message(
        message.from_user.id,
        text="Меню:",
        reply_markup=menu_markup()
    )


@dp.message_handler(text=my_profile_message)
@user_handlers
async def send_profile(message: types.Message):
    """Вывод данных о пользователе"""
    logger.info(f"Пользователь с TG_ID {message.from_user.id} "
                f"запросил информацию о себе")
    data = dict(get_user_data_from_db(message.from_user.id))
    if data['about'] == 'null':
        data['about'] = 'Не указано'
    gender_id = data['gender']
    gender_status = get_gender_from_db(gender_id)
    data['gender'] = gender_status
    birthday = data['birthday'].split('-')
    birthday.reverse()
    data['birthday'] = '-'.join(birthday)
    await bot.send_message(
        message.from_user.id,
        f"Имя: {data['name']};\n"
        f"Дата рождения: {data['birthday']};\n"
        f"О себе: {data['about']};\n"
        f"Пол: {data['gender']};",
        reply_markup=edit_profile_markup()
    )


@dp.message_handler(text=edit_profile_message)
@user_handlers
async def edit_profile(message: types.Message):
    """Перенаправление на повторную регистрацию"""
    logger.info(f"Пользователь с TG_ID {message.from_user.id} "
                f"отправлен на повторную регистрацию")
    await start_registration(message)


@dp.message_handler(text=about_bot_message)
async def about_bot_message(message: types.Message):
    """Вывод информации о боте"""
    logger.info(f"Пользователь с TG_ID {message.from_user.id} "
                f"запросил информацию о боте")
    await bot.send_message(
        message.from_user.id,
        """*Добро пожаловать в бот для нетворкинга\.*\n
С помощью бота проходят живые и онлайн встречи 1\-1 для студентов\
 и IT\-специалистов\. Каждую неделю по понедельникам великий рандом\
 подбирает пару\.  Вам нужно самостоятельно договориться о встрече\
 и созвониться\.  Можно встретиться лично, если вы в одном городе\.\n
Администратор @Loravel\n
__*FAQ*__\n
__*Как подбирается пара?*__\n
Пара выбирается рандомайзером каждый понедельник,\
 обычно это происходит утром\n
__*Где проходят встречи?*__\n
Обычно мы предлагаем проводить встречи в онлайне с помощью Zoom\.\
 Но если вы живете в одном городе и готовы встретиться вживую\
\− это будет очень круто\.\n
__*Обязательно ли идти на встречу?*__\n
Каждую неделю бот готов выдать тебе собеседника\. Перед\
 распределением пар можно отказаться \— если на предстоящей неделе\
 не складывается или нет настроения\. Для этого есть опция\
 "каникулы"\. Когда пара уже назначена, лучше не сливаться\. Если\
 не получается встретиться, напиши сообщение своему партнёру\.\
 Небольшое извинение всегда лучше, чем игнорирование\.\n
__*Сколько длится встреча?*__\n
Как договоритесь\. Обычно люди общаются 45−60 минут, а иногда\
 и 3 часов мало\n
__*Я могу отказаться от участия в боте?*__\n
Да, отказаться можно в любой момент\. Для этого достаточно просто\
 остановить бота\. Чтобы вернуться, нужно будет запустить\
 его снова\.\n
*Удачи\!\)*
""", parse_mode="MarkdownV2"
    )


@dp.message_handler(text=my_status_message)
@user_handlers
async def status_message(message: types.Message):
    """Вывод статуса участия в распределении"""
    logger.info(f"Пользователь с TG_ID {message.from_user.id} "
                f"запросил информацию о статусе участия")
    user_row = get_user_data_from_db(message.from_user.id)
    status_row = get_user_status_from_db(user_row['id'])
    if status_row['status'] == 1:
        status = "Вы участвуете в распределении пар на следующей неделе"
    else:
        holidays_row = get_holidays_status_from_db(user_row['id'])
        holidays_till = holidays_row['till_date'].split('-')
        holidays_till.reverse()
        holidays_till = '-'.join(holidays_till)
        status = (f"Вы на каникулах до {holidays_till}. "
                  f"В это время пара для встречи вам предложена не будет. "
                  f"После указанной даты статус 'Активен' "
                  f"будет восстановлен автоматически")
    await bot.send_message(message.from_user.id, text=status)
    logger.info(f"Пользователь с TG_ID {message.from_user.id} "
                f"получил информацию о статусе участия")
