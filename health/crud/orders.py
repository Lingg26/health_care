from pydantic import BaseModel

from health.crud.base import CrudBase
from health.models.oders import Orders as OrderModel, OrdersItem as OrdersItemModel
from sqlalchemy.orm import Session


class Orders(CrudBase):
    model = OrderModel

    def get_all(self, db: Session):
        query = db.query(self.model)
        return query.all()

    def get_filter_list(self, query_param: BaseModel) -> list:
        list_filter = []
        if query_param.state:
            list_filter.append(self.model.state == query_param.state)
        if query_param.start_date:
            list_filter.append(self.model.created_at >= query_param.start_date)
        if query_param.end_date:
            list_filter.append(self.model.Orders.created_at <= query_param.end_date)
        return list_filter

class OrdersItem(CrudBase):
    model = OrdersItemModel

    def get_all(self, db: Session):
        query = db.query(self.model)
        return query.all()


order_service = Orders()
order_item_service = OrdersItem()