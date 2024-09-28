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

        # Здесь вы сможете использовать метод getChat, чтобы получить данные о администраторе
        # response = await get_chat_info(id_admin)

        # admin_contact = f"tg://user?id={id_admin}"  # Ссылка на пользователя

        await msg.reply(text=f"Если вы хотите получить помощь администрации, перейдите в личные сообщения этого администратора:\n@{id_admin}\n")


async def get_chat_info(chat_id):
    url = f"https://api.telegram.org/bot{os.environ.get('BOT_TOCKEN')}/getChat?chat_id={chat_id}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
