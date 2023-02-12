import logging
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from controllerBD import DatabaseManager
from data import config

logger = logging.getLogger(__name__)

aiogram_logger = logging.getLogger('aio_logger')

logger.setLevel(logging.INFO)
aiogram_logger.setLevel(logging.DEBUG)

main_handler = RotatingFileHandler('my_logger.log', maxBytes=50000000,
                                   backupCount=5)
aiogram_handler = RotatingFileHandler('aiogram_logger.log', maxBytes=50000000,
                                      backupCount=2)


logger.addHandler(main_handler)
aiogram_logger.addHandler(aiogram_handler)

formatter = logging.Formatter(
    fmt=('%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s'),
    datefmt='%H:%M:%S'
)

main_handler.setFormatter(formatter)
aiogram_handler.setFormatter(formatter)

bot = Bot(token=str(config.TOKEN))
dp = Dispatcher(bot, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware(logger=aiogram_logger))

path = 'data/coffee_database.db'
db_controller = DatabaseManager(path, logger)
db_controller.create_tables()
