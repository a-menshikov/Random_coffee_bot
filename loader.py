import logging
from data import config
from controllerBD import DatabaseManager
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(level=logging.INFO)



bot = Bot(token=str(config.TOKEN))
dp = Dispatcher(bot, storage=MemoryStorage())
path = 'C:/Users/User/Desktop/Programming/Data/random_coffee/data/coffee_database.db'
db_controller = DatabaseManager(path)
db_controller.create_tables()