from typing import Optional, List

from pydantic import Field
from sqlmodel import SQLModel

from health.schemas.base import BaseListResponse, BaseRequestListSchema


class ProductRequestSchema(BaseRequestListSchema):
    category_id: Optional[int] = Field()
    name: Optional[str] = Field()
    min_price: Optional[int] = Field()
    max_price: Optional[int] = Field()
    origin: Optional[str] = Field()

class ProductResponseSchema(SQLModel):
    id: int = Field()
    name: str = Field()
    unit: str = Field()
    price: int = Field()
    description: Optional[str] = Field()
    image: str = Field()
    category_name: str = Field()

class ProductListRespnseSchema(BaseListResponse):
    data: List[ProductResponseSchema]
    categories: Optional[List]

