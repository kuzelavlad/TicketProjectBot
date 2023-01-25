from aiogram.dispatcher.filters.state import State, StatesGroup


class UserState(StatesGroup):
    user = State()
    tier = State()
    username = State()
    password = State()

class EventState(StatesGroup):
    event = State()
    ticket = State()
    blank_create_event = State()
    create_event = State()

class CreateEventState(StatesGroup):
    title = State()
    ticket_count = State()





