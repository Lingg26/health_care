from typing import Optional

from sqlmodel import Field
from sqlalchemy import Column, Text

from health.shared.database import Base, TimestampMixin


class ChatLogs(Base, TimestampMixin, table=True):
    __tablename__ = 'chat_logs'

    question: str = Field(sa_column=Column(Text), nullable=False)
    ai_answer: str = Field(sa_column=Column(Text), nullable=False)
    account_id: int = Field(nullable=False, foreign_key='account.id')
    state: Optional[str] = Field(nullable=True)
