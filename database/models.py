from datetime import datetime
from typing import Annotated, List

from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.db import Base


class TelegramUser(Base):
    __tablename__ = "telegram_user"

    telegram_id: Mapped[str] = mapped_column(String, nullable=False, primary_key=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    events: Mapped[List["CustomEvent"]] = relationship("CustomEvent", back_populates="participants",
                                                       cascade="all, delete-orphan")
    participate_quiz: Mapped[List["CustomQuiz"]] = relationship("CustomQuiz", back_populates="participants",
                                                                cascade="all, delete-orphan")

class CustomEvent(Base):
    __tablename__ = "custom_event"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    start_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    name: Mapped[str] = mapped_column(String)
    link_map: Mapped[String] = mapped_column(String)
    description: Mapped[String] = mapped_column(String)
    created: Mapped[int] = mapped_column(ForeignKey("telegram_user.telegram_id", ondelete="CASCADE"))
    photo_id: Mapped[str] = mapped_column(String)

    participants: Mapped[List[TelegramUser]] = relationship("TelegramUser", back_populates="events")

class CustomQuiz(Base):
    __tablename__ = "custom_quiz"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String)
    created: Mapped[int] = mapped_column(ForeignKey("telegram_user.telegram_id", ondelete="CASCADE"))
    description: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[List[str]] = mapped_column(ARRAY(String))
    true_answer: Mapped[List[int]] = mapped_column(ARRAY(Integer))
    photo_id: Mapped[str] = mapped_column(String)

    participants: Mapped[List[TelegramUser]] = relationship("TelegramUser", back_populates="participate_quiz")
