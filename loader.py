import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from controllerBD import DatabaseManager
from data import config

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

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

dp.middleware.setup(LoggingMiddleware(logger=logger))

path = 'data/coffee_database.db'
db_controller = DatabaseManager(path, logger)
db_controller.create_tables()
