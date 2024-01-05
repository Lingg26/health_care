from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Text

from health.shared.database import Base, TimestampMixin


class Category(Base, TimestampMixin, table=True):
    __tablename__ = 'category'

    category_name: str = Field(nullable=False)
    notes: Optional[str] = Field(sa_column=Column(Text), nullable=True)
    image: Optional[str] = Field(nullable=True)
    parent_category_id: Optional[int] = Field(nullable=True)

    product: List["Products"] = Relationship(
        back_populates="category",
        sa_relationship_kwargs={"uselist": True},
    )


class CategoryRegister(SQLModel):
    category_name: str = Field(nullable=False)
    parent_category_id: Optional[int] = Field(nullable=True)
    notes: Optional[str] = Field(nullable=True)
    image: Optional[str] = Field()


class CategoryUpdate(SQLModel):
    category_name: str = Field(nullable=False)
    parent_category_id: Optional[int] = Field(nullable=True)
    notes: Optional[str] = Field( nullable=True)
    image: Optional[str] = Field()
