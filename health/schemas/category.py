from typing import List
from typing import Optional

from pydantic import Field, BaseModel

from health import models
from health.schemas.base import BaseListResponse, BaseRequestListSchema


class CategoryListResponse(BaseListResponse):
    data: List[models.Category]


class CategoryListQuerySchema(BaseRequestListSchema):
    parent_category_id: Optional[int] =Field()
    category_name: Optional[str] = Field()

class CategoryInDB(BaseModel):
    category_name: str = Field()
    notes: Optional[str] = Field()
    image: Optional[str] = Field()
    parent_category_id: Optional[int] = Field()

class CategoryResponseSchema(CategoryInDB):
    sub_category: Optional[list] = Field()

class CategoryChildResponseSchema(CategoryInDB):
    parent_category: Optional[list] = Field()
