from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import Dispatcher

from handlers.decorators import user_handlers
from keyboards.user import help_texts
from loader import bot

help_texts_messages = [
    (
        "Привет! Я твой собеседник на этой неделе. "
        "Как насчет сходить вместе выпить кофе на выходных?"
    ),
    "Здравствуйте! Когда у Вас есть время на этой неделе?",
    (
        "Привет! Бот пишет, что ты мой собеседник на эту неделю. "
        "Можем встретиться или созвониться. Тебе как удобно?"
    ),
    (
        "Добрый день! Ты мне выпал в боте. "
        "Скажи, когда тебе удобно будет созвониться?"
    ),
    (
        "Приветствую! Буду рад/а встретиться, но у меня немного "
        "загружена вторая половина недели. "
        "Может, у нас получится во вторник или среду?"
    ),
]


# @dp.message_handler(text=help_texts)
@user_handlers
async def send_help_texts(message: types.Message):
    """Отправка сообщений примеров."""
    await bot.send_message(
        message.from_user.id, "Ты можешь скопировать текст нажав на него."
    )
    for text in help_texts_messages:
        await sleep(0.05)
        await bot.send_message(
            message.from_user.id, f"<code>{text}</code>", parse_mode="HTML"
        )


def register_help_texts_handlers(dp: Dispatcher):
    dp.register_message_handler(send_help_texts, text=help_texts)
