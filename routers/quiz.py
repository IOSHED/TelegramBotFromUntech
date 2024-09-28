from aiogram import Router, F
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from database.db import async_session
from database.sql_alchemy import add_custom_quiz, get_latest_custom_quizzes, get_custom_quiz_by_name

quiz_router = Router()


@quiz_router.message(Command("get_quiz"))
async def get_quiz(message: Message,):
    async with async_session() as session:
        qs = await get_latest_custom_quizzes(session)
        for quiz in qs:
            await message.answer_photo(photo=quiz.photo_id, caption=f"**{quiz.name}**\n\n{quiz.description}\n", parse_mode=ParseMode.MARKDOWN)


class AnswerQuiz(StatesGroup):
    quiz = State()
    name = State()

@quiz_router.message(Command("get_quiz_by_name"))
async def get_quiz_by_name(message: Message, state: FSMContext):
    await message.answer("Введите название викторины:")
    await state.set_state(AnswerQuiz.name)

@quiz_router.message(AnswerQuiz.name)
async def get_quiz_by_name_name(message: Message, state: FSMContext):
    async with async_session() as session:
        quiz = await get_custom_quiz_by_name(session, message.text)
        ans = ""
        for a in quiz.answer:
            ans += a + '\n'
        await message.answer_photo(
            caption=f"**{quiz.name}**\n\n{quiz.description}\n\n{ans}\n",
            parse_mode=ParseMode.MARKDOWN,
            photo=quiz.photo_id
        )
        await message.answer(
            "Введите один или несколько правильных ответов.\nНапример:\n```\n1, 3, 5\n```"
        )
        await state.update_data(t_answ=quiz.true_answer)
        await state.set_state(AnswerQuiz.quiz)

@quiz_router.message(AnswerQuiz.quiz,)
async def get_quiz_by_name_answer(message: Message, state: FSMContext):
    answer = list(map(int, message.text.split(', ')))
    data = await state.get_data()
    if str(answer) == str(data["t_answ"]):
        await message.answer(
            text="Молодец, всё верно!!!",
            parse_mode=ParseMode.MARKDOWN
        )
    else:
        await message.answer(
            text="Неверно, попробуй ещё...",
            parse_mode=ParseMode.MARKDOWN
        )


class Quiz(StatesGroup):
    name = State()
    description = State()
    answers = State()
    true_answers = State()
    photo = State()


@quiz_router.message(Command("create_new_quiz"))
async def create_new_quiz(message: Message, state: FSMContext):
    # async with async_session() as session:
    #     usr = await get_telegram_user(session, message.from_user.id)
    #     if usr.is_admin:
    await message.answer(
        text="Введите **имя** для викторины:",
        parse_mode=ParseMode.MARKDOWN
    )
    # Устанавливаем пользователю состояние "выбирает название"
    await state.set_state(Quiz.name)


@quiz_router.message(Quiz.name,)
async def create_new_quiz_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(
        text="Введите **описание** для викторины:",
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(Quiz.description)

@quiz_router.message(Quiz.description,)
async def create_new_quiz_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer(
        text="Введите **варианты ответов**.\nНапример:```\n1. Что-то там\n2. Что-то там дважды```",
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(Quiz.answers)

@quiz_router.message(Quiz.answers,)
async def create_new_quiz_answers(message: Message, state: FSMContext):
    await state.update_data(answers=message.text.split('\n'))
    await message.answer(
        text="Введите **правильные ответы**.\nНапример:```\n1, 2\n```",
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(Quiz.true_answers)

@quiz_router.message(Quiz.true_answers)
async def create_new_quiz_true_answers(message: Message, state: FSMContext):
    await state.update_data(true_answers=list(map(int, message.text.replace(' ', '').split(','))))
    await message.answer(
        text="Загрузите **фотографию** для обложки викторины.",
        parse_mode=ParseMode.MARKDOWN
    )
    await state.set_state(Quiz.photo)


@quiz_router.message(Quiz.photo, F.photo)
async def create_new_quiz_photo(message: Message, state: FSMContext):
    photo = message.photo[-1].file_id
    data = await state.get_data()
    async with async_session() as session:
        quiz = await add_custom_quiz(session, data['name'], data['description'], data['answers'], data['true_answers'], message.from_user.id, photo)
        ans = ""

        for a in quiz.answer:
            ans += a + '\n'

        await message.answer_photo(
            caption=f"**{quiz.name}**\n\n{quiz.description}\n\n{ans}\n",
            parse_mode=ParseMode.MARKDOWN,
            photo=quiz.photo_id
        )
