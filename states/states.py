from aiogram.dispatcher.filters.state import StatesGroup, State


class UserData(StatesGroup):
    """Машина состояний"""
    name = State()
    birthday = State()
    about = State()
    gender = State()