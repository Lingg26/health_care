from typing import List

from pydantic import Field
from typing import Optional

from health import models
from health.schemas.base import BaseListResponse, BaseRequestListSchema


class NewsListResponse(BaseListResponse):
    data: List[models.News]

class NewsListQuerySchemas(BaseRequestListSchema):
    keyword: Optional[str] = Field()
