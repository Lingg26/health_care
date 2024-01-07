from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from health import models
from health.crud import order_service
from health.models import CategoryRegister, CategoryUpdate
from health.schemas.category import CategoryListResponse, CategoryListQuerySchema
from health.schemas.orders import StatisticQuery
from health.shared.core_type import UserType, DeleteFlag
from health.tools.deps import get_current_authenticated_user, get_database_session

router = APIRouter()

@router.get(
    '/',
    summary=" Thống kê doanh thu"
)
async def get_statistics(
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
        query_params: StatisticQuery = Depends()
):
    orders, paginate = order_service.all(db, query_param=query_params)
    total_price = 0
    for order in orders:
        total_price += order.total_price
    return {
        "total_pricce": total_price,
        "data": orders,
        "Paginate": paginate
    }