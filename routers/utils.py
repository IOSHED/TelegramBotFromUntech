from aiogram import Router
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

from database.db import async_session
from database.sql_alchemy import add_telegram_user

utils_router = Router()


@utils_router.message(CommandStart())
async def start(msg: Message):
    id_user = msg.from_user.id
    async with async_session() as session:
        await add_telegram_user(session, str(id_user))

    await msg.answer(text="**Добро пожаловать!**\n Я чат-бот для `всероссийских юнармейских военно-спортивных игр`, который предоставляет актуальную информацию об этом мероприятии.", parse_mode=ParseMode.MARKDOWN)

@utils_router.message(Command('start_admin'))
async def start_admin(msg: Message):
    id_user = msg.from_user.id
    if msg.text.split()[1] == '445414454144541':
        async with async_session() as session:
            await add_telegram_user(session, str(id_user), is_admin=True)
        return await msg.reply(text="This is admin!!!")
    return await msg.reply(text="This is admin? Not!!!")
