import os

import aiohttp
from aiogram import Router
from aiogram.filters import Command

from database.db import async_session
from database.sql_alchemy import get_random_admin

support_router = Router()


@support_router.message(Command("get_support"))
async def get_support(msg):
    async with async_session() as session:
        id_admin = await get_random_admin(session)

        await msg.reply(text=f"Если вы хотите получить помощь администрации, перейдите в личные сообщения этого "
                             f"администратора:\n@{id_admin}\n")
