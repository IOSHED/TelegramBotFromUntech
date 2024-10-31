from datetime import datetime

from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from database.db import async_session
from database.sql_alchemy import get_latest_custom_event, get_custom_event_by_name, get_telegram_user, add_custom_event


def create_yandex_maps_link(points, scale=14):
    base_url = "https://yandex.ru/maps/?"
    ll = ','.join([f"{point['lon']},{point['lat']}" for point in points])
    pt = '~'.join([f"{point['lon']},{point['lat']},pm2dgl" for point in points])
    return f"{base_url}ll={ll}&pt={pt}&z={scale}"


class CustomEvent(StatesGroup):
    name = State()
    description = State()
    link_map = State()
    start_at = State()
    photo = State()


class CustomEventController:
    @staticmethod
    async def get_events(message: Message):
        """Retrieves and sends the latest custom events."""
        async with async_session() as session:
            events = await get_latest_custom_event(session)
            for event in events:
                await message.answer_photo(
                    caption=f"{event.name}\n\n{event.description}\n\nПосетите карту: {event.link_map}\n\n Мероприятие "
                            f"начнётся в {event.start_at}\n",
                    parse_mode=ParseMode.MARKDOWN,
                    photo=event.photo_id
                )

    @staticmethod
    async def get_event_by_name(message: Message):
        """Retrieves a specific event by name and sends it."""
        async with async_session() as session:
            event_name = message.text.split(' ', 1)[1]
            event = await get_custom_event_by_name(session, event_name)
            if event:
                await message.answer_photo(
                    caption=f"{event.name}\n\n{event.description}\n\nПосетите карту: {event.link_map}\n\n Мероприятие "
                            f"начнётся в {event.start_at}\n",
                    parse_mode=ParseMode.MARKDOWN,
                    photo=event.photo_id
                )
            else:
                await message.answer("Событие не найдено.")

    @staticmethod
    async def create_new_event(message: Message, state: FSMContext):
        """Initiates the creation of a new event if the user is an admin."""
        async with async_session() as session:
            usr = await get_telegram_user(session, message.from_user.id)
            if usr.is_admin:
                await message.answer(
                    text="Введите **имя** для события\:",
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                await state.set_state(CustomEvent.name)
            else:
                await message.answer("У вас нет прав для создания события.")

    @staticmethod
    async def create_new_event_name(message: Message, state: FSMContext):
        """Saves the name of the new event."""
        await state.update_data(name=message.text)
        await message.answer(
            text="Введите **описание** для мероприятия\:",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await state.set_state(CustomEvent.description)

    @staticmethod
    async def create_new_event_description(message: Message, state: FSMContext):
        """Saves the description of the new event."""
        await state.update_data(description=message.text)
        await message.answer(
            text="Вставьте ссылку на карту Yandex \(сгенерированную здесь\:\nhttps://yandex.ru/map-constructor\) для "
                 "продвинутого использования\.\nИли можете ввести координаты \(широта и долгота\)\. "
                 "Например\:\n```\n45.4553457 24.32451\n13.246523 25.3452423\n```",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await state.set_state(CustomEvent.link_map)

    @staticmethod
    async def create_new_event_link_map(message: Message, state: FSMContext):
        """Processes the map link or coordinates provided by the user."""
        if "http" in message.text:
            link_map = message.text
        else:
            points = []
            for coord in message.text.strip().split('\n'):
                lon, lat = coord.split(' ')
                points.append({'lon': lon, 'lat': lat})
            link_map = create_yandex_maps_link(points)

        await state.update_data(link_map=link_map)
        await message.answer(
            text="Введите время проведения мероприятия.\nНапример:",
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(CustomEvent.start_at)

    @staticmethod
    async def create_new_event_start_at(message: Message, state: FSMContext):
        """Processes the start time for the new event."""
        try:
            start_at = datetime.strptime(message.text, '%H:%M %d.%m.%Y')
            await state.update_data(start_at=start_at)
            await message.answer("Загрузите фотографию для мероприятия.")
            await state.set_state(CustomEvent.photo)
        except ValueError:
            await message.answer("Неверный формат времени. Пожалуйста, используйте формат: ``19:00 28.09.2024``.")

    @staticmethod
    async def create_new_event_photo(message: Message, state: FSMContext):
        """Processes the uploaded photo and saves the event data."""
        user_data = await state.get_data()
        event_data = {
            "name": user_data.get("name"),
            "description": user_data.get("description"),
            "link_map": user_data.get("link_map"),
            "start_at": user_data.get("start_at"),
            "photo_id": message.photo[-1].file_id  # Get the highest resolution photo
        }

        async with async_session() as session:
            await add_custom_event(session, **event_data)

        await message.answer("Событие успешно создано!")
        await state.clear()
