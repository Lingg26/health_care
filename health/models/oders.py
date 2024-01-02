from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from pydantic import EmailStr, validator
from sqlmodel import Field, SQLModel, JSON
from sqlalchemy import Column, Text

from health.shared.database import Base, TimestampMixin


class Orders(Base, TimestampMixin, table=True):
    __tablename__ = "orders"

    account_id: int = Field(nullable=False, foreign_key="account.id")
    receiving_location: str = Field(nullable=False)
    payments: Optional[int] = Field(nullable=True, default=1)
    state: Optional[int] = Field(nullable=True, default=1)


class OrdersItem(Base, TimestampMixin, table=True):
    __tablename__ = "orders_item"

    order_id: int = Field(nullable=False, foreign_key="orders.id")
    product_id: int = Field(nullable=False, foreign_key="products.id")
    quantity: int = Field(nullable=False, default=1)

