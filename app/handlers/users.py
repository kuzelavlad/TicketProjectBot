from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext

from constants import GLOBAL_DATA, NOT_FOUND_TIER
from services.event_playground import event_service
from states.tier_state import UserState
from utils.json_to_text import convert_to_text
from aiogram import Dispatcher, types

from bot_creation import bot


async def display_users(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[-1])
    users_response = event_service.get_users(page)

    inline_kb = types.InlineKeyboardMarkup(row_width=1)

    for user in users_response["results"]:
        inline_kb.add(
            types.InlineKeyboardButton(f"{user['id']}. {user['username']}", callback_data=f"get_user:{user['id']}")
        )

    pagination_buttons = []

    if users_response["previous"]:
        pagination_buttons.append(types.InlineKeyboardButton("⬅️", callback_data=f"get_users_{page - 1}"))
    if users_response["next"]:
        pagination_buttons.append(types.InlineKeyboardButton("➡️", callback_data=f"get_users_{page + 1}"))

    inline_kb.row(*pagination_buttons).row(types.InlineKeyboardButton("Return", callback_data="return"))

    await callback.message.edit_text("Edited", reply_markup=inline_kb)
    await callback.answer("Users fetched")


async def display_user(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(":")[-1])
    user = event_service.get_user(user_id)

    await state.set_state(UserState.user.state)
    await state.update_data(user, msg_id=callback.message.message_id)

    inline_kb = types.InlineKeyboardMarkup(row_width=1)
    inline_kb.add(types.InlineKeyboardButton("Change tier", callback_data="change_tier"))
    inline_kb.add(types.InlineKeyboardButton("Change username", callback_data="change_username"))
    inline_kb.add(types.InlineKeyboardButton("Change password", callback_data="change_password"))
    inline_kb.add(types.InlineKeyboardButton("Return", callback_data="return"))

    msg_text = convert_to_text(user)

    await callback.message.edit_text(msg_text, reply_markup=inline_kb)
    await callback.answer("User fetched")


async def choose_tier(callback: types.CallbackQuery, state: FSMContext):
    inline_kb = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, resize_keyboard=True)

    for human_tier in GLOBAL_DATA["tiers"]:
        inline_kb.add(types.KeyboardButton(human_tier))

    await state.set_state(UserState.tier.state)
    msg = await callback.message.answer("Choose Tier", reply_markup=inline_kb)
    await state.update_data(msg_to_delete=msg.message_id, msg_id=callback.message.message_id)


async def change_tier(msg: types.Message, state: FSMContext):
    new_tier = GLOBAL_DATA["tiers"].get(msg.text, NOT_FOUND_TIER)

    if new_tier == NOT_FOUND_TIER:
        await msg.reply("Choose normal tier")
        return

    data = await state.get_data()
    user = event_service.update_user(data["id"], {"tier": new_tier})

    msg_text = convert_to_text(user)

    await bot.edit_message_text(msg_text, msg.chat.id, data["msg_id"])
    await bot.delete_message(msg.chat.id, data["msg_to_delete"])
    await msg.delete()
    await state.finish()


async def username_change_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.username.state)
    msg = await callback.message.answer("Type new username")
    await state.update_data(msg_to_delete=msg.message_id, msg_id=callback.message.message_id)


async def change_username(msg: types.Message, state: FSMContext):
    username = msg.text.strip()
    data = await state.get_data()
    user = event_service.update_user(data["id"], {"username": username})
    msg_text = convert_to_text(user)
    await bot.edit_message_text(msg_text, msg.chat.id, data["msg_id"])
    await bot.delete_message(msg.chat.id, data["msg_to_delete"])
    await msg.delete()
    await state.finish()


async def password_change_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(UserState.password.state)
    msg = await callback.message.answer("Type new password")
    await state.update_data(msg_to_delete=msg.message_id, msg_id=callback.message.message_id)


async def change_password(msg: types.Message, state: FSMContext):
    password = msg.text.strip()
    data = await state.get_data()
    user = event_service.update_user(data["id"], {"password": password})
    msg_text = convert_to_text(user)
    await bot.edit_message_text(msg_text, msg.chat.id, data["msg_id"])
    await bot.delete_message(msg.chat.id, data["msg_to_delete"])
    await msg.delete()
    await state.finish()


def setup(dp: Dispatcher):
    dp.register_callback_query_handler(display_users, Text(contains="get_users"))
    dp.register_callback_query_handler(display_user, Text(contains="get_user"))
    dp.register_callback_query_handler(choose_tier, Text(equals="change_tier"), state=UserState.user)
    dp.register_message_handler(change_tier, state=UserState.tier)
    dp.register_callback_query_handler(username_change_callback, Text(equals="change_username"), state=UserState.user)
    dp.register_message_handler(change_username, state=UserState.username)
    dp.register_callback_query_handler(password_change_callback, Text(equals="change_password"), state=UserState.user)
    dp.register_message_handler(change_password, state=UserState.password)


