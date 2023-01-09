import logging
from data import config
from controllerBD import DatabaseManager
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

logging.basicConfig(filename="main.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
bot = Bot(token=str(config.TOKEN))
dp = Dispatcher(bot, storage=MemoryStorage())
path = 'data/coffee_database.db'
db_controller = DatabaseManager(path)
db_controller.create_tables()