import logging

from aiogram import Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from constants import GLOBAL_DATA
from handlers.users import setup as user_handler_setup
from handlers.events import setup as events_handler_setup
from handlers.connection import setup as connection_handler_setup
from services.event_playground import event_service
from bot_creation import bot


logging.basicConfig(level=logging.INFO)

dp = Dispatcher(bot, storage=MemoryStorage())


async def startup(_):
    event_service.check_availability()
    GLOBAL_DATA["tiers"] = event_service.get_tiers()
    GLOBAL_DATA["tiers"].update({"Deactivate tier": None})

# @dp.message_handler(commands=["start"])
# async def start(msg: types.Message):
#     reply_kb = ReplyKeyboardMarkup()
#     button_connect = KeyboardButton("Connect")
#     reply_kb.add(button_connect)
#     await msg.reply("Please, connect", reply_markup=reply_kb)
#
@dp.message_handler(Text(contains="Connect",ignore_case=True))
async def connect(msg: types.Message):
    send_msg = f'Hello {msg.from_user.first_name}!\n Your ID:{msg.from_user.id}'
    await msg.reply(send_msg)

admin_set = {255127771}

@dp.message_handler(lambda msg: msg.from_user.id in admin_set, commands=["admin"])
async def get_admin_commands(msg: types.Message):
    inline_kb = types.InlineKeyboardMarkup(row_width=1)
    inline_kb.add(types.InlineKeyboardButton("Get users", callback_data="get_users_1"))
    inline_kb.add(types.InlineKeyboardButton("Get events", callback_data="get_events_1"))
    inline_kb.add(types.InlineKeyboardButton("Add event", callback_data="add_event_1"))

    await msg.reply("Choose admin action", reply_markup=inline_kb)


@dp.callback_query_handler(Text(contains="return"), state="*")
async def return_handler(callback: types.CallbackQuery, state: FSMContext):
    await get_admin_commands(callback.message)
    await state.finish()
    await callback.answer("Return pressed")\




connection_handler_setup(dp)
user_handler_setup(dp)
events_handler_setup(dp)


executor.start_polling(dp, skip_updates=True, on_startup=startup)

