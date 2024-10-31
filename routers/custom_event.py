from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.custom_event import CustomEvent, CustomEventController

event_router = Router()


@event_router.message(Command("get_events"))
async def get_events(message: Message):
    await CustomEventController.get_events(message)


@event_router.message(Command("get_event_by_name"))
async def get_event_by_name(message: Message):
    await CustomEventController.get_event_by_name(message)


@event_router.message(Command("create_new_event"))
async def create_new_event(message: Message, state: FSMContext):
    await CustomEventController.create_new_event(message, state)


@event_router.message(CustomEvent.name)
async def create_new_event_name(message: Message, state: FSMContext):
    await CustomEventController.create_new_event_name(message, state)


@event_router.message(CustomEvent.description)
async def create_new_event_description(message: Message, state: FSMContext):
    await CustomEventController.create_new_event_description(message, state)


@event_router.message(CustomEvent.link_map)
async def create_new_event_link_map(message: Message, state: FSMContext):
    await CustomEventController.create_new_event_link_map(message, state)


@event_router.message(CustomEvent.start_at)
async def create_new_event_start_at(message: Message, state: FSMContext):
    await CustomEventController.create_new_event_start_at(message, state)


@event_router.message(CustomEvent.photo)
async def create_new_event_photo(message: Message, state: FSMContext):
    await CustomEventController.create_new_event_photo(message, state)
