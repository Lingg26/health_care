from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from pydantic import EmailStr, validator
from sqlmodel import Field, SQLModel, JSON, Relationship
from sqlalchemy import Column, Text

from health.shared.database import Base, TimestampMixin


class Cart(Base, TimestampMixin, table=True):
    __tablename__ = "cart"

    account_id: int = Field(nullable=False, foreign_key="account.id")
    product_id: int = Field(nullable=False, foreign_key="products.id")
    quantity: int = Field(nullable=False, default=1)
    is_active: bool = Field(nullable=False, default=True)

    product_cart: "Products" = Relationship(
        back_populates="cart",
        sa_relationship_kwargs={"uselist": False}
    )

class CartRegister(SQLModel):
    product_id: int = Field()
    quantity: int = Field()

class CartUpdateQuantity(SQLModel):
    cart_id: int = Field()
    quantity: int = Field()




