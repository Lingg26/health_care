import json

from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

from health.models.products import Products as ProductsModel
from .base import CrudBase
from ..schemas.product import ProductRequestSchema


class Product(CrudBase):
    model = ProductsModel

    def get_all(self, db: Session) -> list[ProductsModel]:
        query = db.query(ProductsModel)
        return query.all()

    def get_filter_list(self, query_param: ProductRequestSchema) -> list:
        list_filter = []
        if query_param.sub_categories:
            list_filter.append(self.model.category_id.in_(query_param.sub_categories))
        if query_param.name:
            list_filter.append(self.model.name.ilike(f"%{query_param.name}%"))
        if query_param.min_price:
            list_filter.append(self.model.price >= query_param.min_price)
        if query_param.max_price:
            list_filter.append(self.model.price <= query_param.max_price)
        if query_param.origin:
            list_filter.append(self.model.origin.in_(query_param.origin))
        return list_filter

    def get_total_count_by_parent(self, list_id):
        pass

    def create(
        self,
        db: Session,
        data: Optional[BaseModel] = None,
        default_data: Dict[str, Any] = {},
    ) -> Optional[model]:
        if data and data.ingredient:
            data.ingredient = json.dumps(data.ingredient)
        return super().create(db, data, default_data)

product_service = Product()