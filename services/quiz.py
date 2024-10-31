from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from database.db import async_session
from database.sql_alchemy import get_latest_custom_quizzes, get_custom_quiz_by_name, add_custom_quiz


class AnswerQuiz(StatesGroup):
    quiz = State()
    name = State()


class Quiz(StatesGroup):
    name = State()
    description = State()
    answers = State()
    true_answers = State()
    photo = State()


class QuizController:

    @staticmethod
    async def get_quiz(message: Message):
        """Retrieves latest custom quizzes from the database."""
        async with async_session() as session:
            quizzes = await get_latest_custom_quizzes(session)
            for quiz in quizzes:
                await message.answer_photo(
                    photo=quiz.photo_id,
                    caption=f"{quiz.name}\n\n{quiz.description}\n",
                    parse_mode=ParseMode.MARKDOWN
                )

    @staticmethod
    async def get_quiz_by_name(message: Message, state: FSMContext):
        """Prompts the user for a quiz name and retrieves the quiz."""
        await message.answer("Введите название викторины:")
        await state.set_state(AnswerQuiz.name)

    @staticmethod
    async def find_quiz_by_name(message: Message, state: FSMContext):
        """Finds a quiz by its name and retrieves its details."""
        async with async_session() as session:
            quiz = await get_custom_quiz_by_name(session, message.text)
            if quiz:
                answers = "\n".join(quiz.answer)
                await message.answer_photo(
                    caption=f"{quiz.name}\n\n{quiz.description}\n\n{answers}\n",
                    parse_mode=ParseMode.MARKDOWN,
                    photo=quiz.photo_id
                )
                await message.answer(
                    "Введите один или несколько правильных ответов\.\nНапример:\n```\n1\, 2\n1\n```",
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                await state.update_data(t_answ=quiz.true_answer)
                await state.set_state(AnswerQuiz.quiz)
            else:
                await message.answer("Викторина не найдена.")

    @staticmethod
    async def check_quiz_answer(message: Message, state: FSMContext):
        """Checks the user's answers against the correct ones."""
        answer = list(map(int, message.text.split(', ')))
        data = await state.get_data()
        if str(answer) == str(data["t_answ"]):
            await message.answer(
                text="Молодец, всё верно!!!",
                parse_mode=ParseMode.MARKDOWN
            )
            await state.clear()
        else:
            await message.answer(
                text="Неверно, попробуй ещё...",
                parse_mode=ParseMode.MARKDOWN
            )

    @staticmethod
    async def create_new_quiz(message: Message, state: FSMContext):
        """Starts the process of creating a new quiz."""
        await message.answer(
            text="Введите **имя** для викторины\:",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await state.set_state(Quiz.name)

    @staticmethod
    async def set_quiz_name(message: Message, state: FSMContext):
        """Sets the name for the new quiz and asks for the description."""
        await state.update_data(name=message.text)
        await message.answer(
            text="Введите **описание** для викторины\:",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await state.set_state(Quiz.description)

    @staticmethod
    async def set_quiz_description(message: Message, state: FSMContext):
        """Sets the description for the newly created quiz."""
        await state.update_data(description=message.text)
        await message.answer(
            text="Введите варианты ответов\.\nНапример\:\n```\n1\. Что-то там\n2\. Что-то там дважды\n```",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await state.set_state(Quiz.answers)

    @staticmethod
    async def set_quiz_answers(message: Message, state: FSMContext):
        """Sets the answers for the new quiz."""
        await state.update_data(answers=message.text.split('\n'))
        await message.answer(
            text="Введите правильные ответы\.\nНапример\:\n```\n1\, 3\n2\n```",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await state.set_state(Quiz.true_answers)

    @staticmethod
    async def set_quiz_true_answers(message: Message, state: FSMContext):
        """Sets the correct answers and asks for a quiz cover photo."""
        await state.update_data(true_answers=list(map(int, message.text.replace(' ', '').split(','))))
        await message.answer(
            text="Загрузите фотографию для обложки викторины.",
            parse_mode=ParseMode.MARKDOWN
        )
        await state.set_state(Quiz.photo)

    @staticmethod
    async def set_quiz_photo(message: Message, state: FSMContext):
        photo = message.photo[-1].file_id
        data = await state.get_data()
        async with async_session() as session:
            quiz = await add_custom_quiz(session, data['name'], data['description'], data['answers'],
                                         data['true_answers'], message.from_user.id, photo)
            ans = ""
            for a in quiz.answer:
                ans += a + '\n'

            await message.answer_photo(
                caption=f"{quiz.name}\n\n{quiz.description}\n\n{ans}\n",
                parse_mode=ParseMode.MARKDOWN,
                photo=quiz.photo_id
            )
            await state.clear()
