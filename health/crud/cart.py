from sqlalchemy.orm import Session

from health.models.cart import Cart as CartModel
from health.shared.core_type import DeleteFlag

from .base import CrudBase
from ..schemas.category import CategoryListQuerySchema


class Cart(CrudBase):
    model = CartModel

    def get_all(self, db: Session):
        query = db.query(CartModel)
        return query.all()


cart_service = Cart()