from typing import Optional, List

from sqlmodel import Field, SQLModel, Relationship

from health.shared.core_type import PaymentsFlag, StatusOrder
from health.shared.database import Base, TimestampMixin


class Orders(Base, TimestampMixin, table=True):
    __tablename__ = "orders"

    account_id: int = Field(nullable=False, foreign_key="account.id")
    receiving_location: str = Field(nullable=False)
    tel: Optional[str] = Field()
    payments: Optional[str] = Field(nullable=True)
    state: Optional[int] = Field(nullable=True)
    total_price: int = Field(nullable=False)
    is_paid: bool = Field(default=False)


class OrdersItem(Base, TimestampMixin, table=True):
    __tablename__ = "orders_item"

    order_id: int = Field(nullable=False, foreign_key="orders.id")
    product_id: int = Field(nullable=False, foreign_key="products.id")
    quantity: int = Field(nullable=False, default=1)

    product_order: "Products" = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"uselist": False}
    )

class OrderItemRegister(SQLModel):
    product_id: int = Field()
    quantity: int = Field()

class OrderRegister(SQLModel):
    account_id: Optional[int] = Field()
    receiving_location: str = Field()
    tel: Optional[str] = Field()
    payments: Optional[PaymentsFlag] = Field()
    total_price: int = Field()
    items: Optional[List[OrderItemRegister]]

class UpdateStatus(SQLModel):
    state: Optional[StatusOrder] = Field()

class PaymentVNpay(SQLModel):
    order_id: int = Field()
    total_price: int = Field(nullable=False)
    bank_code: str = Field()
    ipaddr: str = Field()
    language: str = Field()
    description: str = Field()

