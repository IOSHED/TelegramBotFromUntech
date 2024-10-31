from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from services.quiz import QuizController, AnswerQuiz, Quiz

quiz_router = Router()


@quiz_router.message(Command("get_quiz"))
async def get_quiz(message: Message):
    await QuizController.get_quiz(message)


@quiz_router.message(Command("get_quiz_by_name"))
async def get_quiz_by_name(message: Message, state: FSMContext):
    await QuizController.get_quiz_by_name(message, state)


@quiz_router.message(AnswerQuiz.name)
async def get_quiz_by_name_name(message: Message, state: FSMContext):
    await QuizController.find_quiz_by_name(message, state)


@quiz_router.message(AnswerQuiz.quiz)
async def get_quiz_by_name_answer(message: Message, state: FSMContext):
    await QuizController.check_quiz_answer(message, state)


@quiz_router.message(Command("create_new_quiz"))
async def create_new_quiz(message: Message, state: FSMContext):
    await QuizController.create_new_quiz(message, state)


@quiz_router.message(Quiz.name)
async def create_new_quiz_name(message: Message, state: FSMContext):
    await QuizController.set_quiz_name(message, state)


@quiz_router.message(Quiz.description)
async def create_new_quiz_description(message: Message, state: FSMContext):
    await QuizController.set_quiz_description(message, state)


@quiz_router.message(Quiz.answers)
async def create_new_quiz_answers(message: Message, state: FSMContext):
    await QuizController.set_quiz_answers(message, state)


@quiz_router.message(Quiz.true_answers)
async def create_new_quiz_true_answers(message: Message, state: FSMContext):
    await QuizController.set_quiz_true_answers(message, state)
