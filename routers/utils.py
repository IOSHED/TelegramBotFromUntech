from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from services.utils import UtilsController

utils_router = Router()


@utils_router.message(CommandStart())
async def start(msg: Message):
    await UtilsController.handle_start(msg)


@utils_router.message(Command('start_admin'))
async def start_admin(msg: Message):
    await UtilsController.handle_start_admin(msg)
