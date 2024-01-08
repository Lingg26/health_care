from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from health import models
from health.crud import cart_service
from health.models import CartRegister, CartUpdateQuantity
from health.schemas.base import BaseRequestListSchema
from health.schemas.cart import ProductListResponse, ProductResponse, ProductListResponseSchema
from health.shared.core_type import UserType, DeleteFlag
from health.tools.deps import get_current_authenticated_user, get_database_session

router = APIRouter()


@router.get(
    "/",
    summary="Get list cart items",
    response_model=ProductListResponse
)
async def get_list_cart_item(
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
        query_params: BaseRequestListSchema = Depends()
):
    cart_items, paginate = cart_service.all(db, filter_by={"account_id": current_user.id, "is_active": True},
                                            query_param=query_params)
    response = []
    total_price = 0
    for item in cart_items:
        data = ProductResponse(**item.dict(), product_name=item.product.name,
                               total_price=item.product.price * item.quantity)
        total_price += data.total_price
        response.append(data)
    return ProductListResponse(data=response, paginate=paginate, total_price=total_price)


@router.post(
    "/",
    summary="Creat new cart item",
    response_model=ProductResponse
)
async def creat_cart_item(
        query_params: CartRegister,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
):
    existing_cart = cart_service.get(db, filter_by={"account_id": current_user.id,
                                                    "product_id": query_params.product_id,
                                                    "is_active": True})
    if existing_cart:
        existing_cart.quantity += query_params.quantity
        db.commit()
        return ProductResponse(**existing_cart.dict(), product_name=existing_cart.product.name,
                               total_price=existing_cart.product.price * existing_cart.quantity)
    else:
        query_params.__dict__["account_id"] = current_user.id
        new_cart = cart_service.create(db, data=query_params)
        return ProductResponse(**new_cart.dict(), product_name=new_cart.product.name,
                               total_price=new_cart.product.price * new_cart.quantity)

@router.put(
    "/",
    summary="Update quantity item",
    response_model=ProductListResponseSchema
)
async def update_quantity(
        carts: List[CartUpdateQuantity],
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
):
    response = []
    total_price = 0
    for cart in carts:
        existing_cart = cart_service.get(db, filter_by={"id": cart.cart_id, "is_active": True, "account_id": current_user.id})
        if not existing_cart:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND,
                detail=f"Cart {cart.cart_id} item is not found"
            )
        else:
            update_cart = cart_service.update(db, filter_by={"id": cart.cart_id}, data=cart)
            data = ProductResponse(**update_cart.dict(), product_name=update_cart.product.name,
                                   total_price=update_cart.product.price * update_cart.quantity)
            total_price += data.total_price
            response.append(data)
    return ProductListResponseSchema(data=response, total_price=total_price)


@router.delete(
    "/{cart_id}",
    summary="Update quantity item"
)
async def delete_cart(
        cart_id: int,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
):
    existing_cart = cart_service.get(db,
                                     filter_by={"id": cart_id, "is_active": True, "account_id": current_user.id})
    if not existing_cart:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail=f"Cart {cart_id} item is not found"
        )
    cart_service.delete(db, filter_by={"id": cart_id, "is_active": True, "account_id": current_user.id})
    return {
        'status': status.HTTP_200_OK,
        "message": "delete success",
    }
