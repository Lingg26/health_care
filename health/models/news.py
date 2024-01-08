from typing import Optional

from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Text

from health.shared.database import Base, TimestampMixin


class News(Base, TimestampMixin, table=True):
    __tablename__ = 'news'

    title: str = Field(nullable=False)
    content: Optional[str] = Field(sa_column=Column(Text), nullable=True)
    image: Optional[str] = Field(nullable=True)
    describe: Optional[str] = Field(nullable=True)

class NewsRegister(SQLModel):
    title: str = Field(nullable=False)
    content: Optional[str] = Field(sa_column=Column(Text), nullable=True)
    image: Optional[str] = Field(nullable=True)
    describe: Optional[str] = Field()


class NewsUpdate(SQLModel):
    title: str = Field(nullable=False)
    content: Optional[str] = Field(sa_column=Column(Text), nullable=True)
    image: Optional[str] = Field(nullable=True)
    describe: Optional[str] = Field()
