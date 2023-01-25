from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext

from bot_creation import bot
from states.connection import ConnectionState


async def get_number(msg: types.Message):
    print(await bot.get_chat(msg.chat.id))
    inline_kb = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)
    inline_kb.add(types.KeyboardButton("Get number", request_contact=True))
    await msg.answer("Press button 'Get number'", reply_markup=inline_kb)

async def initialize_connection(msg: types.Message, state: FSMContext):
    # await ConnectionState.phone.set()

    async with state.proxy() as data:
        data["phone"] = msg.contact.phone_number

    await msg.answer("Enter your login:")
    await ConnectionState.next()


async def ask_login(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["login"] = msg.text.strip()



def setup(dp: Dispatcher):
    dp.register_message_handler(get_number, commands=["start"])
    dp.register_message_handler(initialize_connection, content_types=types.ContentType.CONTACT)
    dp.register_message_handler(ask_login, state=ConnectionState.login)