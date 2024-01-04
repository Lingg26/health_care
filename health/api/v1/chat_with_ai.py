from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from health import models
from health.crud import category_service
from health.models import CategoryRegister, CategoryUpdate, ChatLogsRegister
from health.schemas.category import CategoryListResponse, CategoryListQuerySchema
from health.shared.core_type import UserType, DeleteFlag
from health.tools.deps import get_current_authenticated_user, get_database_session

router = APIRouter()

@router.get(
    "/",
    summary="Get list chat with AI",
)
async def get_list_chat(
        account_id: int,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user)
):
    chats = (
        db.query(models.ChatLogs)
        .filter(models.ChatHistory.account_id == account_id)
        .order_by(models.ChatHistory.created_at.desc())
        .all()
    )
    return chats

@router.post(
    "/",
    summary="Send message"
)
async def send_message(
        body: ChatLogsRegister,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user)
):
    pass
