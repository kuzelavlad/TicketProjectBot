from aiogram.dispatcher.filters import Text
from services.event_playground import event_service
from aiogram import Dispatcher, types
from utils.json_to_text import convert_to_text_ticket
from states.tier_state import EventState, CreateEventState
from aiogram.dispatcher import FSMContext
from bot_creation import bot

async def display_events(callback: types.CallbackQuery):
    page = int(callback.data.split("_")[-1])
    events_response = event_service.get_events(page)

    inline_kb = types.InlineKeyboardMarkup(row_width=1)

    for event in events_response["results"]:
        inline_kb.add(
            types.InlineKeyboardButton(f"{event['id']}. {event['title']}. {event['date']}",callback_data=f"get_event:{event['id']}")

        )

    pagination_buttons = []

    if events_response["previous"]:
        pagination_buttons.append(types.InlineKeyboardButton("⬅️", callback_data=f"get_events_{page - 1}"))
    if events_response["next"]:
        pagination_buttons.append(types.InlineKeyboardButton("➡️", callback_data=f"get_events_{page + 1}"))

    inline_kb.row(*pagination_buttons).row(types.InlineKeyboardButton("Return", callback_data="return"))

    await callback.message.edit_text("Edited", reply_markup=inline_kb)
    await callback.answer("Events fetched")


async def display_event(callback: types.CallbackQuery, state: FSMContext):
    event_id = int(callback.data.split(":")[-1])
    event = event_service.get_event(event_id)

    await state.set_state(EventState.event.state)
    await state.update_data(event, msg_id=callback.message.message_id)

    inline_kb = types.InlineKeyboardMarkup(row_width=1)
    inline_kb.add(types.InlineKeyboardButton("Change ticket count", callback_data="change_tickets"))
    inline_kb.add(types.InlineKeyboardButton("Return", callback_data="return"))

    msg_text = convert_to_text_ticket(event)

    await callback.message.edit_text(msg_text, reply_markup=inline_kb)
    await callback.answer("Event fetched")


async def ticket_change_callback(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(EventState.ticket.state)
    msg = await callback.message.answer("Type new amount")
    await state.update_data(msg_to_delete=msg.message_id, msg_id=callback.message.message_id)


async def change_tickets(msg: types.Message, state: FSMContext):
    tickets = int(msg.text.strip())
    data = await state.get_data()
    event = event_service.update_tick_amount(data["id"], {"ticket_count": tickets})
    msg_text = convert_to_text_ticket(event)
    await bot.edit_message_text(msg_text, msg.chat.id, data["msg_id"])
    await bot.delete_message(msg.chat.id, data["msg_to_delete"])
    await msg.delete()
    await state.finish()


async def add_event(callback: types.CallbackQuery, state: FSMContext):
    fields = [
        {"name": "title", "optional": False},
        {"name": "description", "optional": True},
        {"name": "date", "optional": True},
        {"name": "ticket_count", "optional": False},
    ]
    msg_ids_to_delete = []
    msg = "Enter Event Title:\n"
    msg_object = await callback.message.answer(msg)

    msg_ids_to_delete.append(msg_object.message_id)
    # msg_object = await callback.message.answer("\n".join(
    #     [f"{field['name']}:" if not field["optional"] else f"{field['name']} [optional]:" for field in fields])
    # )
    msg_ids_to_delete.append(msg_object.message_id)

    await state.update_data(msg_id=callback.message.message_id, msg_ids_to_delete=msg_ids_to_delete)
    await callback.answer("State changed")


    await state.set_state(CreateEventState.title.state)


async def add_title(msg: types.Message, state: FSMContext):
    await state.update_data(title=msg.text.strip())
    await CreateEventState.next()
    await msg.answer("Enter Ticket Amount")

async def add_tickets(msg: types.Message, state: FSMContext):
    await state.update_data(ticket_count=int(msg.text.strip()))
    data = await state.get_data()
    event = event_service.add_event(data)
    await state.finish()
    await msg.answer(convert_to_text_ticket(event))

async def add_event_data_field(msg: types.Message, state: FSMContext):
    await state.update_data(title="New title from state")
    await state.update_data(ticket_count=10)
    await state.set_state(EventState.add_event.state)

async def create_event(msg: types.Message, state: FSMContext):
    event_data = {}
    for line in msg.text.split("\n"):
        field, value = line.split(":")
        field = field.replace("[optional]", "").strip()
        event_data[field] = value.strip() or None

        # event = event_service.create_event(event_data)
        data = await state.get_data()
        event = event_service.create_event(data)
        msg_text = convert_to_text_ticket(event)
        await bot.edit_message_text(msg_text, msg.chat.id, data["msg_id"])
        for msg_id in data["msg_ids_to_delete"]:
            await bot.delete_message(msg.chat.id, msg_id)
        await msg.delete()
        await state.finish()





def setup(dp: Dispatcher):

    dp.register_callback_query_handler(display_events, Text(contains="get_events"))
    dp.register_callback_query_handler(display_event, Text(contains="get_event"))
    dp.register_callback_query_handler(ticket_change_callback, Text(equals="change_tickets"), state=EventState.event)
    dp.register_message_handler(change_tickets, state=EventState.ticket)
    dp.register_callback_query_handler(add_event, Text(contains="add_event"))
    dp.register_message_handler(add_title, state=CreateEventState.title)
    dp.register_message_handler(add_tickets, state=CreateEventState.ticket_count)
    dp.register_message_handler(create_event, state=EventState.create_event)
    dp.register_message_handler(add_event_data_field, state=EventState.blank_create_event)
