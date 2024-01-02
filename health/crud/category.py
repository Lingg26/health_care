from sqlalchemy import func
from sqlalchemy.orm import Session

from health.models.category import Category as CategoryModel
from health.shared.core_type import DeleteFlag

from .base import CrudBase
from .. import models
from ..schemas.category import CategoryListQuerySchema


class Category(CrudBase):
    model = CategoryModel

    def get_all(self, db: Session) -> list[CategoryModel]:
        query = db.query(CategoryModel)
        return query.all()

    def get_filter_list(self, query_param: CategoryListQuerySchema) -> list:
        list_filter = []
        if query_param.category_name:
            list_filter.append(self.model.category_name.ilike(f"%{query_param.category_name}%"))
        if query_param.parent_category_id:
            list_filter.append(self.model.parent_category_id == query_param.parent_category_id)
        else:
            list_filter.append(self.model.parent_category_id == None)
        return list_filter

    def get_sub_category_and_count_product(self, db, list_parent_category_ids, parent_id):
        filter_list = []
        if list_parent_category_ids:
            filter_list.append(models.Products.category_id.in_(list_parent_category_ids))
        else:
            filter_list.append(models.Products.category_id == parent_id)
        if parent_id:
            filter_list.append(self.model.id == parent_id)
        categories = (
            db.query(self.model, func.count(models.Products.id).label("count_product"))
            .filter(*filter_list)
            .group_by(self.model.id)
            .all()
        )
        return categories



category_service = Category()