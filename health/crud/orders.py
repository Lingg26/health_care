from health.crud.base import CrudBase
from health.models.oders import Orders as OrderModel, OrdersItem as OrdersItemModel
from sqlalchemy.orm import Session


class Orders(CrudBase):
    model = OrderModel

    def get_all(self, db: Session):
        query = db.query(self.model)
        return query.all()

class OrdersItem(CrudBase):
    model = OrdersItemModel

    def get_all(self, db: Session):
        query = db.query(self.model)
        return query.all()


order_service = Orders()
order_item_service = OrdersItem()