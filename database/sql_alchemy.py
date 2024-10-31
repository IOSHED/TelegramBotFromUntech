import random
from datetime import datetime
from typing import List

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session

from database.models import TelegramUser, CustomQuiz, CustomEvent


async def get_random_admin(_session: AsyncSession) -> str:
    admins = ["IOSHid", "iosh1D"]
    random_admin = random.choice(admins)
    return random_admin


async def add_custom_event(session: Session, start_at: datetime, link_map: str, description: str, user_id: int,
                           name: str, photo: str) -> CustomEvent:
    new_event = CustomEvent(start_at=start_at, link_map=link_map, description=description, created=user_id, name=name,
                            photo_id=photo)
    session.add(new_event)
    await session.commit()
    await session.refresh(new_event)
    return new_event


def get_custom_event(session: Session, event_id: int) -> CustomEvent:
    event = session.get(CustomEvent, event_id)
    if event is None:
        raise NoResultFound(f"Event with id {event_id} not found.")
    return event


def delete_custom_event(session: Session, event_id: int) -> None:
    event = get_custom_event(session, event_id)
    session.delete(event)
    session.commit()


async def add_custom_quiz(session: Session, name: str, description: str, answers: List[str],
                          true_answer_indices: List[int], user_id: int, photo_id) -> CustomQuiz:
    new_quiz = CustomQuiz(name=name, description=description, answer=answers, true_answer=true_answer_indices,
                          created=str(user_id), photo_id=photo_id)
    session.add(new_quiz)
    await session.commit()
    await session.refresh(new_quiz)
    return new_quiz


async def get_custom_quiz(session: Session, quiz_id: int) -> CustomQuiz:
    quiz = await session.get(CustomQuiz, quiz_id)
    if quiz is None:
        raise NoResultFound(f"Quiz with id {quiz_id} not found.")
    return quiz


async def get_custom_quiz_by_name(session: AsyncSession, quiz_name: str) -> CustomQuiz:
    result = await session.execute(
        select(CustomQuiz).where(CustomQuiz.name == quiz_name)
    )
    quiz = result.scalars().first()
    if quiz is None:
        raise NoResultFound(f"Quiz with name '{quiz_name}' not found.")
    return quiz


async def get_custom_event_by_name(session: AsyncSession, event_name: str) -> CustomEvent:
    result = await session.execute(
        select(CustomEvent).where(CustomEvent.name == event_name)
    )
    event = result.scalars().first()
    if event is None:
        raise NoResultFound(f"Event with name '{event_name}' not found.")
    return event


async def get_latest_custom_quizzes(session: AsyncSession) -> list[CustomQuiz]:
    result = await session.execute(
        select(CustomQuiz)
        .order_by(CustomQuiz.id)
        .limit(5)
    )
    quizzes = result.scalars().all()
    return quizzes


async def get_latest_custom_event(session: AsyncSession) -> list[CustomEvent]:
    result = await session.execute(
        select(CustomEvent)
        .order_by(CustomEvent.start_at)
        .limit(5)
    )
    events = result.scalars().all()
    return events


def delete_custom_quiz(session: Session, quiz_id: int) -> None:
    quiz = get_custom_quiz(session, quiz_id)
    session.delete(quiz)
    session.commit()


async def add_telegram_user(session: Session, telegram_id: str, is_admin: bool = False) -> TelegramUser:
    existing_user = await session.execute(
        select(TelegramUser).where(TelegramUser.telegram_id == telegram_id)
    )
    user = existing_user.scalars().first()

    if user:
        if is_admin:
            user.is_admin = True
            await session.commit()
        return user
    else:
        new_user = TelegramUser(telegram_id=telegram_id, is_admin=is_admin)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user


async def get_telegram_user(session: Session, user_id: int) -> TelegramUser:
    user = await session.get(TelegramUser, {"telegram_id": str(user_id)})
    if user is None:
        raise NoResultFound(f"User with id {user_id} not found.")
    return user


def delete_telegram_user(session: Session, user_id: int) -> None:
    user = get_telegram_user(session, user_id)
    session.delete(user)
    session.commit()
