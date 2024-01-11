from typing import List
from sqlalchemy import or_

from health import models

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from health.crud import product_service, category_service
from health.models import ProductRegister, Category
from health.schemas.category import CategoryResponseSchema, CategoryChildResponseSchema
from health.schemas.product import ProductRequestSchema, ProductListRespnseSchema, ProductResponseSchema, \
    ProductDetailSchema
from health.shared.core_type import UserType
from health.shared.file_operator import create_and_save_file, validate_uploaded_file
from health.tools.deps import get_current_authenticated_user, get_database_session
from health.utils import generate_uuid

router = APIRouter()

def get_breadcrumb(category_id, list_category):
    response = []
    for category in list_category:
        if category.id == category_id:
            response.append(CategoryChildResponseSchema(**category.dict(), parent_category=get_breadcrumb(category.parent_category_id, list_category)))
    return response


@router.get(
    "/",
    summary="Get list product",
    response_model=ProductListRespnseSchema,
)
async def get_list_product(
        db: Session = Depends(get_database_session),
        query_params: ProductRequestSchema = Depends()
):
    categories_response = []
    sub_category = []
    if query_params.category_id:
        categories = db.query(Category).filter(
            or_(
                Category.parent_category_id == query_params.category_id
            )
        ).all()
    else:
        categories = db.query(Category).filter().all()
    if categories:
        categories_id = [category.id for category in categories]
        for id in categories_id:
            sub_categories = db.query(Category).filter(Category.parent_category_id == id)
            if not sub_categories:
                categories_count = category_service.get_sub_category_and_count_product(db, [], id)
                sub_category.append(id)
            else:
                sub_categories_id = [category.id for category in sub_categories]
                categories_count = category_service.get_sub_category_and_count_product(db, sub_categories_id, id)
                sub_category.extend(sub_categories_id)
            if categories_count:
                categories_response.append(categories_count)
    else:
        categories_count = category_service.get_sub_category_and_count_product(db, [], query_params.category_id)
        sub_category.append(query_params.category_id)
        if categories_count:
            categories_response.append(categories_count)

    query_params.__dict__["sub_categories"] = sub_category
    products, paginate = product_service.all(db, query_param=query_params)
    response = []
    for product in products:
        data = ProductResponseSchema(**product.dict(), category_name=product.category.category_name)
        response.append(data)
    return ProductListRespnseSchema(data=response, paginate=paginate, categories=categories_response)


@router.get(
    "/{product_id}",
    summary="get product detail",
)
async def get_product_detail(
        product_id: int,
        db: Session = Depends(get_database_session)
):
    product = product_service.get(db, filter_by={"id": product_id})
    categories, _ = category_service.all(db)
    data = ProductDetailSchema(**product.dict(), breadcrumb=get_breadcrumb(product.category_id, categories))
    return data


@router.post(
    "/",
    summary="create a new product",
    response_model=models.Products
)
async def create_product(
        product_profile: ProductRegister,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
):
    if current_user.user_type == UserType.ADMIN:
        new_product = product_service.create(db, data=product_profile)
        return new_product
    else:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Account don't have permission"
        )

@router.patch('/upload_image', summary='Update image product')
async def upload_user_avatar(
    current_user: models.Account = Depends(get_current_authenticated_user),
    image: UploadFile = File(default=None),
    db: Session = Depends(get_database_session),
) -> dict:
    """
    Upload a new avatar for the current user.
    """
    validate_uploaded_file(image)
    file_name = f'{generate_uuid()}'
    avt_name = create_and_save_file(file=image, file_name=file_name)['path']

    return {'image_path': avt_name}
