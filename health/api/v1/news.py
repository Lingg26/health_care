from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from health import models
from health.crud import news_service
from health.models import NewsRegister, NewsUpdate
from health.schemas.news import NewsListResponse, NewsListQuerySchemas
from health.shared.core_type import UserType, DeleteFlag
from health.tools.deps import get_current_authenticated_user, get_database_session

router = APIRouter()


@router.get(
    "/",
    response_model=NewsListResponse,
    summary="Get list news"
)
async def get_list_news(
        db: Session = Depends(get_database_session),
        query_params: NewsListQuerySchemas = Depends()
):
    query_params.__dict__["is_deleted"] = DeleteFlag.IS_NOT_DELETED
    news, paginate = news_service.all(db, query_param=query_params)
    return NewsListResponse(data=news, paginate=paginate)


@router.get(
    "/{news_id}",
    response_model=models.News,
    summary="get news detail"
)
async def get_news_detail(
        news_id: int,
        db: Session = Depends(get_database_session),
):
    news = news_service.get(db, filter_by={"id": news_id})
    return news


@router.post(
    "/",
    response_model=models.News,
    summary="Create new news"
)
async def create_news(
        news_profile: NewsRegister,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
):
    if current_user.user_type == UserType.ADMIN:
        new_news = news_service.create(db, data=news_profile)
        return new_news
    else:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Account don't have permission"
        )


@router.put(
    "/{news_id}",
    response_model=models.News,
    summary="Update news information"
)
async def update_news(
        news_id: int,
        news_profile: NewsUpdate,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user),
):
    if current_user.user_type == UserType.ADMIN:
        new_news = news_service.update(db, filter_by={"id": news_id}, data=news_profile)
        return new_news
    else:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="Account don't have permission"
        )
