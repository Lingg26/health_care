from typing import List
from typing import Optional

from pydantic import Field

from health import models
from health.schemas.base import BaseListResponse, BaseRequestListSchema


class CategoryListResponse(BaseListResponse):
    data: List[models.Category]


class CategoryListQuerySchema(BaseRequestListSchema):
    parent_category_id: Optional[int] =Field()
    category_name: Optional[str] = Field()
