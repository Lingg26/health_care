from datetime import date, datetime
from typing import List
from typing import Optional

from pydantic import Field, BaseModel

from health import models
from health.schemas.base import BaseListResponse, BaseRequestListSchema


class OrdersInDB(BaseModel):
    id: int = Field()
    account_id: int = Field()
    receiving_location: str = Field()
    payments: Optional[str] = Field()
    state: Optional[int] = Field()
    total_price: int = Field()
    created_at: Optional[datetime]

class OrderDetailInDB(BaseModel):
    order_id: int = Field()
    product_id: int = Field()
    product_name: str = Field()
    quantity: int = Field()
    price: int = Field()
    image: Optional[str] = Field()
    unit: Optional[str] = Field()
    created_at: Optional[datetime]

class OrderDetailListResponseSchema(BaseModel):
    data: List[OrderDetailInDB]

class StatisticQuery(BaseRequestListSchema):
    state: Optional[int]
    start_date: Optional[date]
    end_date: Optional[date]

class OrderResponse(OrdersInDB):
    mail_address: Optional[str]
    items: List[OrderDetailInDB]

class OrdersListResponse(BaseListResponse):
    data: List[OrderResponse]



