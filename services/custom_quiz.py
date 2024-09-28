from aiogram.enums import ParseMode
from aiogram.fsm.state import StatesGroup, State

from database.db import async_session
from database.sql_alchemy import get_telegram_user


class Quiz(StatesGroup):
    name = State()
    description = State()
    answers = State()
    true_answers = State()
    photo = State()


async def add_quiz(user_id, state_quiz, msg) -> str:
    async with async_session() as session:
        usr = await get_telegram_user(session, user_id)
        if usr.is_admin:
            await msg.answer("**Введите имя викторины**:", parse_mod=ParseMode.MARKDOWN)
            await state_quiz.set_state(Quiz.name)
        return await msg.answer("Нет доступа к команде!")

