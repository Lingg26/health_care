from sqlalchemy.orm import Session

from health.models.news import News as NewsModel
from health.shared.core_type import DeleteFlag

from .base import CrudBase


class News(CrudBase):
    model = NewsModel
    def get_all(self, db: Session) -> list[NewsModel]:
        query = db.query(NewsModel)
        return query.all()


news_service = News()