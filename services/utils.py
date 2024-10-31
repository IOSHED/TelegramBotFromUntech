from aiogram.enums import ParseMode
from aiogram.types import Message

from database.db import async_session
from database.sql_alchemy import add_telegram_user


class UtilsController:
    @staticmethod
    async def handle_start(msg: Message):
        """Handles the /start command and adds the user to the database."""
        id_user = msg.from_user.id
        async with async_session() as session:
            await add_telegram_user(session, str(id_user))
        welcome_message = (
            "**Добро пожаловать\!**\n"
            "Я чат\-бот для `всероссийских юнармейских военно\-спортивных игр`\, "
            "который предоставляет актуальную информацию об этом мероприятии\."
        )
        await msg.answer(text=welcome_message, parse_mode=ParseMode.MARKDOWN_V2)

    @staticmethod
    async def handle_start_admin(msg: Message):
        """Handles the /start_admin command and verifies admin status."""
        id_user = msg.from_user.id
        admin_token = '445414454144541'

        if len(msg.text.split()) > 1 and msg.text.split()[1] == admin_token:
            async with async_session() as session:
                await add_telegram_user(session, str(id_user), is_admin=True)
            return await msg.reply(text="This is admin!!!")

        return await msg.reply(text="This is admin? Not!!!")
