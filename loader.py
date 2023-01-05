import logging
from data import config

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)

bot = Bot(token=str(config.TOKEN))
dp = Dispatcher(bot, storage=MemoryStorage())