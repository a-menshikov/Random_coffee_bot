from aiogram.dispatcher.filters.state import StatesGroup, State


class UserData(StatesGroup):
    """Машина состояний"""
    start = State()
    name = State()
    birthday = State()
    about = State()
    gender = State()
    end_registration = State()
    check_info = State()