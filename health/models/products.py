from datetime import datetime
from typing import Optional, List

from fastapi import HTTPException, status
from pydantic import EmailStr, validator
from sqlmodel import Field, SQLModel, JSON, Relationship
from sqlalchemy import Column, Text

from health.shared.database import Base, TimestampMixin

class Products(Base, TimestampMixin, table=True):
    __tablename__ = 'products'

    name: str = Field(nullable=False)
    unit: str = Field(nullable=False)
    category_id: int = Field(nullable=False, foreign_key="category.id")
    price: int = Field(nullable=False)
    origin: Optional[str] = Field(nullable=True)
    producer: Optional[str] = Field(nullable=True)
    description: Optional[str] = Field(sa_column=Column(Text), nullable=True)
    image: str = Field(nullable=False)
    ingredient: Optional[str] = Field(sa_column=Column(JSON))
    use: Optional[str] = Field(sa_column=Column(Text))
    how_to_use: Optional[str] = Field(sa_column=Column(Text))
    side_effects: Optional[str] = Field(sa_column=Column(Text))
    note: Optional[str] = Field(sa_column=Column(Text))
    preserve: Optional[str] = Field()


    cart: List["Cart"] = Relationship(
        back_populates="product_cart",
        sa_relationship_kwargs={"uselist": True},
    )

    category: "Category" = Relationship(
        back_populates="product",
        sa_relationship_kwargs={"uselist": False}
    )

class ProductRegister(SQLModel):
    name: str = Field(nullable=False)
    unit: str = Field(nullable=False)
    category_id: int = Field(nullable=False)
    price: int = Field(nullable=False)
    origin: Optional[str] = Field()
    producer: Optional[str] = Field()
    description: Optional[str] = Field()
    image: str = Field(nullable=False)
    ingredient: Optional[dict] = Field(default=[])
    use: Optional[str] = Field()
    how_to_use: Optional[str] = Field()
    side_effects: Optional[str] = Field()
    note: Optional[str] = Field()
    preserve: Optional[str] = Field()



