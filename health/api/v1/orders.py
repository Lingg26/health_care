from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse

from health import models
from health.core import settings
from health.crud import order_service, order_item_service, cart_service
from health.models import CategoryRegister, CategoryUpdate, OrderRegister, UpdateStatus, PaymentVNpay
from health.schemas.base import Paginate, BaseRequestListSchema
from health.schemas.orders import OrdersListResponse, OrderDetailListResponseSchema, OrderDetailInDB, StatisticQuery
from health.shared.core_type import UserType, DeleteFlag, PaymentsFlag
from health.shared.vnpay import vnpay
from health.tools.deps import get_current_authenticated_user, get_database_session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

router = APIRouter()
router.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@router.get(
    "/",
    summary="Get list orders",
    response_model=OrdersListResponse
)
async def get_list_order(
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
        query_params: StatisticQuery = Depends()
):
    if current_user.user_type == UserType.ADMIN:
        orders, paginate = order_service.all(db, query_param=query_params)
    else:
        orders, paginate = order_service.all(db, filter_by={"account_id": current_user.id}, query_param=query_params)
    return OrdersListResponse(data=orders, paginate=paginate)


@router.get(
    "/{order_id}",
    summary="get detail order",
    response_model=OrderDetailListResponseSchema
)
async def get_detail_order(
        order_id: int,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user)
):
    filter_list = []
    filter_list.append(models.OrdersItem.order_id == order_id)
    if current_user.user_type == UserType.USER:
        filter_list.append(models.Orders.account_id == current_user.id)
    order_items = (
        db.query(models.OrdersItem)
        .outerjoin(models.Orders, models.Orders.id == models.OrdersItem.order_id)
        .filter(*filter_list)
        .all()
    )
    response = []
    for item in order_items:
        data = OrderDetailInDB(**item.dict(), product_name=item.product_order.name,
                               price=item.product_order.price * item.quantity)
        response.append(data)
    return response


@router.post(
    "/",
    summary="create order",
)
async def create_order(
        data: OrderRegister,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
):
    if not data.account_id:
        data.account_id = current_user.id
    if data.payments == PaymentsFlag.VNPAY:
        data.__dict__['is_paid'] = True
    order_data = data.dict(exclude={"items"})
    new_order = order_service.create(db, default_data=order_data)
    for item in data.items:
        item = item.dict()
        item["order_id"] = new_order.id
        order_item_service.create(db, default_data=item)
        cart_service.update(db, filter_by={"account_id": new_order.account_id, "product_id": item["product_id"]},
                            default_data={"is_active": False})
    return new_order


@router.put(
    "/{order_id}/update_state",
    summary="update status order"
)
async def update_status(
        order_id: int,
        data: UpdateStatus = Depends(),
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
):
    order = order_service.get(db, filter_by={"id": order_id})
    if not order:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Order is not exist"
        )
    order.state = data.state
    db.commit()
    return order


@router.post(
    "/payment",
    summary="payment by VNPAY"
)
async def payment_vnpay(
        data: PaymentVNpay,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
):
    vnp = vnpay()
    vnp.requestData['vnp_Version'] = '2.1.0'
    vnp.requestData['vnp_Command'] = 'pay'
    vnp.requestData['vnp_TmnCode'] = settings.VNPAY_TMN_CODE
    vnp.requestData['vnp_Amount'] = data.total_price * 100
    vnp.requestData['vnp_CurrCode'] = 'VND'
    vnp.requestData['vnp_TxnRef'] = data.order_id
    vnp.requestData['vnp_OrderInfo'] = data.description
    vnp.requestData['vnp_OrderType'] = 270000

    vnp.requestData['vnp_Locale'] = data.language
    if data.bank_code and data.bank_code != "":
        vnp.requestData['vnp_BankCode'] = data.bank_code

    vnp.requestData['vnp_CreateDate'] = datetime.now().strftime('%Y%m%d%H%M%S')  # 20150410063022
    vnp.requestData['vnp_IpAddr'] = data.ipaddr
    vnp.requestData['vnp_ReturnUrl'] = settings.VNPAY_RETURN_URL
    vnpay_payment_url = vnp.get_payment_url(settings.VNPAY_PAYMENT_URL, settings.VNPAY_HASH_SECRET_KEY)
    print(vnpay_payment_url)
    return vnpay_payment_url


@router.get(
    "/payment_ipn",
    summary="get information payment"
)
async def get_payment(
        request: Request
):
    inputData = request.GET
    if inputData:
        vnp = vnpay()
        vnp.responseData = inputData.dict()
        order_id = inputData['vnp_TxnRef']
        amount = inputData['vnp_Amount']
        order_desc = inputData['vnp_OrderInfo']
        vnp_TransactionNo = inputData['vnp_TransactionNo']
        vnp_ResponseCode = inputData['vnp_ResponseCode']
        vnp_TmnCode = inputData['vnp_TmnCode']
        vnp_PayDate = inputData['vnp_PayDate']
        vnp_BankCode = inputData['vnp_BankCode']
        vnp_CardType = inputData['vnp_CardType']
        if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
            # Check & Update Order Status in your Database
            # Your code here
            firstTimeUpdate = True
            totalamount = True
            if totalamount:
                if firstTimeUpdate:
                    if vnp_ResponseCode == '00':
                        print('Payment Success. Your code implement here')
                    else:
                        print('Payment Error. Your code implement here')

                    # Return VNPAY: Merchant update success
                    result = {'RspCode': '00', 'Message': 'Confirm Success'}
                else:
                    # Already Update
                    result = {'RspCode': '02', 'Message': 'Order Already Update'}
            else:
                # invalid amount
                result = {'RspCode': '04', 'Message': 'invalid amount'}
        else:
            # Invalid Signature
            result = {'RspCode': '97', 'Message': 'Invalid Signature'}
    else:
        result = {'RspCode': '99', 'Message': 'Invalid request'}
    return


@router.get(
    "/payment_return"
)
async def payment_return(request: Request):
    data = request.query_params.items()
    response = {}
    for i in data:
        response[i[0]] = i[1]
    if vnpay.validate_response(response):
        return "Thành công"
    else:
        return "Thất bại"
    # inputData = request.GET
    # if inputData:
    #     vnp = vnpay()
    #     vnp.responseData = inputData.dict()
    #     order_id = inputData['vnp_TxnRef']
    #     amount = int(inputData['vnp_Amount']) / 100
    #     order_desc = inputData['vnp_OrderInfo']
    #     vnp_TransactionNo = inputData['vnp_TransactionNo']
    #     vnp_ResponseCode = inputData['vnp_ResponseCode']
    #     vnp_TmnCode = inputData['vnp_TmnCode']
    #     vnp_PayDate = inputData['vnp_PayDate']
    #     vnp_BankCode = inputData['vnp_BankCode']
    #     vnp_CardType = inputData['vnp_CardType']
    #     if vnp.validate_response(settings.VNPAY_HASH_SECRET_KEY):
    #         if vnp_ResponseCode == "00":
    #             return templates.TemplateResponse(request, "payment_return.html", {"title": "Kết quả thanh toán",
    #                                                                                "result": "Thành công",
    #                                                                                "order_id": order_id,
    #                                                                                "amount": amount,
    #                                                                                "order_desc": order_desc,
    #                                                                                "vnp_TransactionNo": vnp_TransactionNo,
    #                                                                                "vnp_ResponseCode": vnp_ResponseCode})
    #         else:
    #             return templates.TemplateResponse(request, "payment_return.html", {"title": "Kết quả thanh toán",
    #                                                                                "result": "Lỗi",
    #                                                                                "order_id": order_id,
    #                                                                                "amount": amount,
    #                                                                                "order_desc": order_desc,
    #                                                                                "vnp_TransactionNo": vnp_TransactionNo,
    #                                                                                "vnp_ResponseCode": vnp_ResponseCode})
    #     else:
    #         return templates.TemplateResponse(request, "payment_return.html",
    #                                           {"title": "Kết quả thanh toán", "result": "Lỗi", "order_id": order_id,
    #                                            "amount": amount,
    #                                            "order_desc": order_desc, "vnp_TransactionNo": vnp_TransactionNo,
    #                                            "vnp_ResponseCode": vnp_ResponseCode, "msg": "Sai checksum"})
    # else:
    #     return templates.TemplateResponse(request, "payment_return.html", {"title": "Kết quả thanh toán", "result": ""})
