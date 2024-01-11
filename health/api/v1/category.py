from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from health import models
from health.crud import category_service
from health.models import CategoryRegister, CategoryUpdate
from health.schemas.category import CategoryListResponse, CategoryListQuerySchema, CategoryResponseSchema
from health.shared.core_type import UserType, DeleteFlag
from health.tools.deps import get_current_authenticated_user, get_database_session

router = APIRouter()


def get_sub_categories(parent_categoty_id, list_category):
    response = []
    for category in list_category:
        if category.parent_category_id == parent_categoty_id:
            response.append(CategoryResponseSchema(**category.dict(), sub_category=get_sub_categories(category.id, list_category)))
    return response

@router.get(
    "/",
    summary="Get list parent category"
)
async def get_list_parent_category(
        db: Session = Depends(get_database_session),
        query_params: CategoryListQuerySchema = Depends()
):
    categories = db.query(models.Category).filter(models.Category.is_deleted == 0).all()
    response = []
    for category in categories:
        if not query_params.parent_category_id and not category.parent_category_id:
            response.append(CategoryResponseSchema(**category.dict(), sub_category=get_sub_categories(category.id, categories)))
        elif query_params.parent_category_id and category.parent_category_id == query_params.parent_category_id:
            response.append(CategoryResponseSchema(**category.dict(), sub_category=get_sub_categories(category.id, categories)))
    return response

# @router.get(
#     "/{category_id}",
#     response_model=List[models.Category],
#     summary="get sub category"
# )
# async def get_list_sub_category(
#         parent_category_id: int,
#         db: Session = Depends(get_database_session),
#         query_params: CategoryListQuerySchema = Depends()
# ):
#     query_params.__dict__["is_deleted"] = DeleteFlag.IS_NOT_DELETED
#     categories, paginate = category_service.all(db, query_param=query_params)
#     return CategoryListResponse(data=categories, paginate=paginate)


@router.post(
    "/",
    response_model=models.Category,
    summary="create category"
)
async def create_category(
        category_profile: CategoryRegister,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
):
    existing_category = category_service.get(db, filter_by={
        "category_name": category_profile.category_name,
        "parent_category_id": category_profile.parent_category_id,
        "is_deleted": DeleteFlag.IS_NOT_DELETED
    })
    if existing_category:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="Category name is already"
        )
    if current_user.user_type == UserType.ADMIN:
        new_category = category_service.create(db, data=category_profile)
        return new_category
    else:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Account don't have permission"
        )


@router.put(
    "/{category_id}",
    response_model=models.Category,
    summary="Update category information"
)
async def update_category(
        category_id: int,
        category_profile: CategoryUpdate,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
):
    if current_user.user_type == UserType.ADMIN:
        new_category = category_service.update(db,filter_by={"id":category_id}, data=category_profile)
        return new_category
    else:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Account don't have permission"
        )


@router.get(
    "/{category_id}",
    response_model=models.Category,
    summary="Get category information"
)
async def get_detail_category(
        category_id: int,
        db: Session = Depends(get_database_session),
):
    category = category_service.get(db, filter_by={"id": category_id})
    return category
