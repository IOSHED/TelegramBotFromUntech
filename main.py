import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from database.db import Base, engine
from routers.custom_event import event_router
from routers.quiz import quiz_router
from routers.support import support_router
from routers.utils import utils_router


async def main():
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    await create_tables()

    BOT_TOCKEN = os.environ.get("BOT_TOCKEN")
    bot = Bot(BOT_TOCKEN)
    storage_bot = MemoryStorage()
    print(await bot.get_me())
    dp = Dispatcher(storage=storage_bot)
    dp.include_routers(
        utils_router,
        quiz_router,
        event_router,
        support_router,
    )
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
