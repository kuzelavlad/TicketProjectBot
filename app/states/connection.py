from aiogram.dispatcher.filters.state import State, StatesGroup

class ConnectionState(StatesGroup):
    login = State()
    password = State()