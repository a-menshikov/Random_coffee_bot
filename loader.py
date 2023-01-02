from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from data import config

bot = Bot(token="5542693067:AAGwMJoM5WgrwGWQQVJ20DpJERFUZSpHRFU", parse_mode=types.ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)