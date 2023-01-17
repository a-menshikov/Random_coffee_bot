import logging

from data import config
from controllerBD import DatabaseManager
from logging.handlers import RotatingFileHandler
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler('my_logger.log', maxBytes=50000000,
                              backupCount=5)

logger.addHandler(handler)

formatter = logging.Formatter(
    fmt=('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s'),
    datefmt='%H:%M:%S'
)

handler.setFormatter(formatter)

bot = Bot(token=str(config.TOKEN))
dp = Dispatcher(bot, storage=MemoryStorage())

path = 'data/coffee_database.db'
db_controller = DatabaseManager(path, logger)
db_controller.create_tables()
