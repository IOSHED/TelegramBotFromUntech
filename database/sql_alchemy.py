from datetime import datetime
from typing import List

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from database.models import TelegramUser, CustomQuiz, CustomEvent

import random
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


async def get_random_admin(session: AsyncSession) -> str:
    # Запрос на получение всех администраторов
    # result = await session.execute(
    #     select(TelegramUser).where(TelegramUser.is_admin.is_(True))
    # )
    # admins = result.scalars().all()  # Извлечение всех администраторов
    #
    # if not admins:
    #     raise NoResultFound("No admin found.")
    admins = ["IOSHid", "iosh1D"]

    # Выбор случайного администратора
    random_admin = random.choice(admins)

    return random_admin  # Возвращаем telegram_id администратора


# Функция для добавления нового события
async def add_custom_event(session: Session, start_at: datetime, link_map: str, description: str, user_id: int, name: str, photo: str) -> CustomEvent:
    new_event = CustomEvent(start_at=start_at, link_map=link_map, description=description, created=user_id, name=name, photo_id=photo)
    session.add(new_event)
    await session.commit()
    await session.refresh(new_event)
    return new_event

# Функция для получения события по ID
def get_custom_event(session: Session, event_id: int) -> CustomEvent:
    event = session.get(CustomEvent, event_id)
    if event is None:
        raise NoResultFound(f"Event with id {event_id} not found.")
    return event

# Функция для удаления события по ID
def delete_custom_event(session: Session, event_id: int) -> None:
    event = get_custom_event(session, event_id)
    session.delete(event)
    session.commit()

# Функция для добавления нового опроса
async def add_custom_quiz(session: Session, name: str, description: str, answers: List[str], true_answer_indices: List[int], user_id: int, photo_id) -> CustomQuiz:
    new_quiz = CustomQuiz(name=name, description=description, answer=answers, true_answer=true_answer_indices, created=str(user_id), photo_id=photo_id)
    session.add(new_quiz)
    await session.commit()
    await session.refresh(new_quiz)
    return new_quiz

# Функция для получения опроса по ID
async def get_custom_quiz(session: Session, quiz_id: int) -> CustomQuiz:
    quiz = await session.get(CustomQuiz, quiz_id)
    if quiz is None:
        raise NoResultFound(f"Quiz with id {quiz_id} not found.")
    return quiz

async def get_custom_quiz_by_name(session: AsyncSession, quiz_name: str) -> CustomQuiz:
    result = await session.execute(
        select(CustomQuiz).where(CustomQuiz.name == quiz_name)
    )
    quiz = result.scalars().first()  # Извлекает первый результат, если он есть
    if quiz is None:
        raise NoResultFound(f"Quiz with name '{quiz_name}' not found.")
    return quiz

async def get_custom_event_by_name(session: AsyncSession, event_name: str) -> CustomEvent:
    result = await session.execute(
        select(CustomEvent).where(CustomEvent.name == event_name)
    )
    event = result.scalars().first()  # Извлекает первый результат, если он есть
    if event is None:
        raise NoResultFound(f"Event with name '{event_name}' not found.")
    return event


async def get_latest_custom_quizzes(session: AsyncSession) -> list[CustomQuiz]:
    # Запрос на получение последних 5 созданных CustomQuiz
    result = await session.execute(
        select(CustomQuiz)
        .order_by(CustomQuiz.id)  # Сортировка по дате создания в порядке убывания
        .limit(5)
    )
    quizzes = result.scalars().all()  # Извлечение результатов
    return quizzes

async def get_latest_custom_event(session: AsyncSession) -> list[CustomEvent]:
    result = await session.execute(
        select(CustomEvent)
        .order_by(CustomEvent.start_at)
        .limit(5)
    )
    events = result.scalars().all()  # Извлечение результатов
    return events

# Функция для удаления опроса по ID
def delete_custom_quiz(session: Session, quiz_id: int) -> None:
    quiz = get_custom_quiz(session, quiz_id)
    session.delete(quiz)
    session.commit()

# Функция для добавления нового пользователя
async def add_telegram_user(session: Session, telegram_id: str, is_admin: bool = False) -> TelegramUser:
    # Проверяем, существует ли пользователь с таким telegram_id
    existing_user = await session.execute(
        select(TelegramUser).where(TelegramUser.telegram_id == telegram_id)
    )
    user = existing_user.scalars().first()

    if user:
        # Если пользователь уже существует и новый is_admin = True, обновляем is_admin
        if is_admin:
            user.is_admin = True
            await session.commit()  # Сохраняем изменения
        return user
    else:
        # Если пользователя нет, добавляем нового
        new_user = TelegramUser(telegram_id=telegram_id, is_admin=is_admin)
        session.add(new_user)
        await session.commit()  # Используйте await
        await session.refresh(new_user)  # Используйте await
        return new_user

# Функция для получения пользователя по ID
async def get_telegram_user(session: Session, user_id: int) -> TelegramUser:
    user = await session.get(TelegramUser, {"telegram_id": str(user_id)})
    if user is None:
        raise NoResultFound(f"User with id {user_id} not found.")
    return user

# Функция для удаления пользователя по ID
def delete_telegram_user(session: Session, user_id: int) -> None:
    user = get_telegram_user(session, user_id)
    session.delete(user)
    session.commit()
