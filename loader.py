import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

import pytz
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from controllerBD.add_info_to_db import add_gender_info
from controllerBD.models import create_tables
from data import config

timezone = pytz.timezone('Etc/GMT-3')


def timetz(*args):
    return datetime.now(timezone).timetuple()


logger = logging.getLogger('main_logger')

aiogram_logger = logging.getLogger('aio_logger')

logger.setLevel(logging.INFO)
aiogram_logger.setLevel(logging.INFO)

main_handler = RotatingFileHandler('my_logger.log', maxBytes=30000000,
                                   backupCount=5)
aiogram_handler = RotatingFileHandler('aiogram_logger.log', maxBytes=30000000,
                                      backupCount=2)


logger.addHandler(main_handler)
aiogram_logger.addHandler(aiogram_handler)

formatter = logging.Formatter(
    fmt=('%(asctime)s.%(msecs)d %(levelname)s '
         '%(filename)s %(funcName)s %(message)s'),
    datefmt='%d-%m-%Y %H:%M:%S',
)

formatter.converter = timetz

main_handler.setFormatter(formatter)
aiogram_handler.setFormatter(formatter)

bot = Bot(token=str(config.TOKEN))
dp = Dispatcher(bot, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware(logger=aiogram_logger))


create_tables()
add_gender_info()
