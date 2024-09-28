from datetime import datetime

from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from database.db import async_session
from database.sql_alchemy import get_telegram_user, add_custom_event, get_latest_custom_event, get_custom_event_by_name

event_router = Router()

def create_yandex_maps_link(points, scale=14):
    base_url = "https://yandex.ru/maps/?"
    ll = ','.join([f"{point['lon']},{point['lat']}" for point in points])
    pt = '~'.join([f"{point['lon']},{point['lat']},pm2dgl" for point in points])
    return f"{base_url}ll={ll}&pt={pt}&z={scale}"


@event_router.message(Command("get_events"))
async def get_events(message: Message,):
    async with async_session() as session:
        qs = await get_latest_custom_event(session)
        for event in qs:
            await message.answer_photo(
                caption=f"**{event.name}**\n\n{event.description}\n\nПосетите карту: {event.link_map}\n\n Мероприятие начнётся в {event.start_at}\n",
                parse_mode=ParseMode.MARKDOWN,
                photo=event.photo_id
            )


@event_router.message(Command("get_event_by_name"))
async def get_event_by_name(message: Message):
    async with async_session() as session:
        event = await get_custom_event_by_name(session, message.text.split(' ')[1])

        await message.answer_photo(
            caption=f"**{event.name}**\n\n{event.description}\n\nПосетите карту: {event.link_map}\n\n Мероприятие начнётся в {event.start_at}\n",
            parse_mode=ParseMode.MARKDOWN,
            photo=event.photo_id
        )


class CustomEvent(StatesGroup):
    name = State()
    description = State()
    link_map = State()
    start_at = State()
    photo = State()


@event_router.message(Command("create_new_event"))
async def create_new_event(message: Message, state: FSMContext):
    async with async_session() as session:
        usr = await get_telegram_user(session, message.from_user.id)
        if usr.is_admin:
            await message.answer(
                text="Введите **имя** для события:",
                parse_mode=ParseMode.MARKDOWN
            )
            # Устанавливаем пользователю состояние "выбирает название"
            await state.set_state(CustomEvent.name)


@event_router.message(CustomEvent.name, )
async def create_new_event_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        text="Введите **описание** для мероприятия:",
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(CustomEvent.description)

@event_router.message(CustomEvent.description, )
async def create_new_event_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        text="Вставьте ссылку на карту yandex (сгенерированную здесь:\nhttps://yandex.ru/map-constructor) для продвинутого использования.\nИли можете пойти простым путём, введя координаты (широта и долгота) точек. Например:\n```\n45.4553457 24.32451\n13.246523 25.3452423\n```",
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(CustomEvent.link_map)

@event_router.message(CustomEvent.link_map, )
async def create_new_event_link_map(message: Message, state: FSMContext):
    link_map = ""
    if "http" in message.text:
        link_map = message.text
    else:
        ds = []
        for d in message.text.split('\n'):
            lon, lat = d.split(' ')
            ds.append({'lon': lon, 'lat': lat})
        link_map = create_yandex_maps_link(ds)

    await state.update_data(link_map=link_map)
    await message.answer(
        text="Введите **время проведения** мероприятия.\nНапример:```\n19:00 28.09.2024\n```",
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(CustomEvent.start_at)

@event_router.message(CustomEvent.start_at)
async def create_new_event_true_start_at(message: Message, state: FSMContext):
    await state.update_data(start_at=datetime.strptime(message.text, "%H:%M %d.%m.%Y"))
    await message.answer(
        text="Загрузите **фотографию** для обложки мероприятия.",
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(CustomEvent.photo)


@event_router.message(CustomEvent.photo, F.photo)
async def create_new_event_photo(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    async with async_session() as session:
        event = await add_custom_event(session, data['start_at'], data['link_map'], data['description'], str(message.from_user.id), data['name'], str(photo))

        await message.answer_photo(
            caption=f"**{event.name}**\n\n{event.description}\n\nПосетите карту: {event.link_map}\n\n Мероприятие начнётся в {event.start_at}\n",
            parse_mode=ParseMode.MARKDOWN,
            photo=event.photo_id
        )
