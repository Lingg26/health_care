import json

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import func, and_
from sqlalchemy.orm import Session

from health import models
from health.app.ws.utils import EventEmitter
from health.crud import chat_history_service
from health.models import ChatHistoryResgister
from health.schemas.chats import ChatHistoryResponseSchema
from health.shared.core_type import UserType
from health.tools.deps import get_current_authenticated_user, get_database_session

router = APIRouter()

@router.get(
    "/users",
    summary="Get list user"
)
async def get_list_user_chat(
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user)
):
    if current_user.user_type == UserType.ADMIN:
        sub_query = (
            db.query(
                models.ChatHistory.account_id.label("account_id"), func.max(models.ChatHistory.id).label("id")
            )
            .group_by(models.ChatHistory.account_id)
            .subquery()
        )
        accounts = (
            db.query(
                *models.Account.__table__.columns,
                func.json_object(
                    'id',
                    models.ChatHistory.id,
                    'created_at',
                    models.ChatHistory.created_at,
                    'sent_account_id',
                    models.ChatHistory.sent_account_id,
                    'account_id',
                    models.ChatHistory.account_id,
                    'status',
                    models.ChatHistory.status
                ).label('chat')
            )
            .outerjoin(models.ChatHistory, models.ChatHistory.account_id == models.Account.id)
            .join(sub_query, and_(sub_query.c.account_id == models.Account.id, sub_query.c.id == models.ChatHistory.id))
            .all()
        )
        response = []
        for account in accounts:
            data_copy = dict(account)
            if data_copy['chat']:
                chat = json.loads(data_copy['chat'])
            else:
                chat = {}
            if chat and chat['sent_account_id'] == chat['account_id'] and chat['status'] == 'sent':
                data_copy['is_read'] = False
            else:
                data_copy['is_read'] = True
            data_copy["chat_id"] = chat["id"]
            data_copy.pop('chat')
            response.append(data_copy)

        return {
            'data': response
        }
    else:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            detail="You don't have permission"
        )



@router.get(
    "/{account_id}",
    summary="get list chat history"
)
async def get_list_chat_hisroty(
        account_id: int,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user)
):
    chats = (
        db.query(models.ChatHistory)
        .filter(models.ChatHistory.account_id == account_id)
        .order_by(models.ChatHistory.created_at.desc())
        .all()
    )
    chat_history_service.update_status(db, account_id=account_id,
                                       admin_id=current_user.id if current_user.user_type == UserType.ADMIN else None)
    return chats


@router.post(
    "/send_message",
    summary="Send a message"
)
async def send_message(
        request: Request,
        body: ChatHistoryResgister,
        db: Session = Depends(get_database_session),
        current_user: models.Account = Depends(get_current_authenticated_user)
):
    if not body.account_id:
        body.account_id = current_user.id
    message = chat_history_service.create(
        db=db,
        default_data={
            'sent_account_id': current_user.id,
            'message': body.message,
            'account_id': body.account_id,
            'status': 'sent'
        }
    )

    # socketio
    message = ChatHistoryResponseSchema(**message.dict())
    emitter = EventEmitter(request=request)
    await emitter.send_chat_message(
        room=body.account_id,
        data=message
    )
    return message


