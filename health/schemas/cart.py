from typing import List
from typing import Optional

from pydantic import Field, BaseModel

from health import models
from health.schemas.base import BaseListResponse, BaseRequestListSchema

class ProductInDB(BaseModel):
    account_id: int = Field()
    product_id: int = Field()
    quantity: int = Field()
    is_active: bool = Field()

class ProductResponse(ProductInDB):
    product_name: Optional[str]
    total_price: Optional[int]
    product_image: Optional[str]
    unit: Optional[str]

class ProductListResponse(BaseListResponse):
    data: List[ProductResponse]
    total_price: int = Field()

class ProductListResponseSchema(BaseModel):
    data: List[ProductResponse]
    total_price: int = Field()
