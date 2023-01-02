import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('TG_TOKEN')
ADMIN_TG_ID = os.getenv('ADMIN_TG_ID')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=str(TOKEN))
dp = Dispatcher(bot, storage=MemoryStorage())