from typing import List

import requests
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from health import models
from health.crud import account_service
from health.tools.deps import get_current_authenticated_user, get_database_session
# from health.schemas.response_data import AccountQuerySchema
# from health.shared.file_operator import (
#     validate_uploaded_file,
# )
import os

router = APIRouter()

@router.get(
    '/',
    response_model=models.Account,
    summary='get profile information',
)
async def get_user_profile(
    db: Session = Depends(get_database_session),
    current_user: models.Account = Depends(get_current_authenticated_user),
):
    # if current_user:
    #     account = account_service.get(db, filter_by={'id': current_user.id})
    #     return account
    return current_user


@router.patch(
    '/update_profile',
    response_model=models.Account,
    summary='Update profile information',
)
async def update_user_profile(
    profile_data: models.UpdateProfileAccount,
    db: Session = Depends(get_database_session),
    current_user: models.Account = Depends(get_current_authenticated_user),
) -> models.Account:
    """
    Update the profile information of the current user.
    """
    updated_account = account_service.update(
        db=db,
        filter_by={'id': current_user.id},
        data=profile_data,
    )
    return updated_account


# @router.patch('/upload_avatar', summary='Update user avatar')
# async def upload_user_avatar(
#     current_user: models.Account = Depends(get_current_authenticated_user),
#     avatar_file: UploadFile = File(default=None),
#     db: Session = Depends(get_database_session),
# ) -> dict:
#     """
#     Upload a new avatar for the current user.
#     """
#     validate_uploaded_file(avatar_file)
#     updated_account = account_service.upload_avatar(db, current_user, avatar_file)
#
#     return {'new_avatar': updated_account.upload_file_path}
#
