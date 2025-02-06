import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

import pytz
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.contrib.middlewares.logging import LoggingMiddleware

from controllerBD.add_info_to_db import add_gender_info
from controllerBD.models import create_tables
from data import config

timezone = pytz.timezone("Etc/GMT-3")


def timetz(*args):
    return datetime.now(timezone).timetuple()

def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

logger = get_module_logger("main_logger")

aiogram_logger = get_module_logger("aio_logger")

schedule_logger = get_module_logger("schedule")

logger.setLevel(logging.DEBUG)
aiogram_logger.setLevel(logging.DEBUG)
schedule_logger.setLevel(level=logging.DEBUG)

if not (os.path.isdir("logs")):
    os.mkdir("logs")

main_handler = RotatingFileHandler(
    "logs/my_logger.log",
    maxBytes=30000000,
    backupCount=5,
)
aiogram_handler = RotatingFileHandler(
    "logs/aiogram_logger.log",
    maxBytes=30000000,
    backupCount=2,
)
schedule_handler = RotatingFileHandler(
    "logs/schedule_logger.log",
    maxBytes=30000000,
    backupCount=2,
)


logger.addHandler(main_handler)
aiogram_logger.addHandler(aiogram_handler)
schedule_logger.addHandler(schedule_handler)

formatter = logging.Formatter(
    fmt=(
        "%(asctime)s.%(msecs)d %(levelname)s " "%(filename)s %(funcName)s %(message)s"
    ),
    datefmt="%d-%m-%Y %H:%M:%S",
)

formatter.converter = timetz

main_handler.setFormatter(formatter)
aiogram_handler.setFormatter(formatter)
schedule_handler.setFormatter(formatter)

bot = Bot(token=str(config.TOKEN))
dp = Dispatcher(bot, storage=MemoryStorage())

dp.middleware.setup(LoggingMiddleware(logger=aiogram_logger))


create_tables()
add_gender_info()
