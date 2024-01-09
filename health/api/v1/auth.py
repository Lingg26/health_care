from datetime import timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from requests_oauthlib import OAuth2Session
from sqlalchemy.orm import Session
from oauthlib.oauth2 import WebApplicationClient
from jose import jwt

from health import crud, models
from health.core import security, settings
from health.crud import account_service
from health.shared import mail_sender
from health.shared.core_type import UserType
from health.tools.deps import get_current_authenticated_user, get_database_session
# from health.models.account import AccountRegisterWithGoogle, TokenRequest
from health.models.auth import create_auth_tokens
# from health.shared.core_type import DeviceType, OauthProvider
# from health.shared.file_operator import create_and_save_file
# from health.utils import generate_uuid
from health.core.settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES, PASSWORD_DEFAULT,
)
import requests
import os

router = APIRouter()


@router.get('/healthcheck')
async def check():
    raise HTTPException(status_code=status.HTTP_200_OK)

from email_validator import EmailNotValidError, validate_email
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from health.core import settings
@router.post('/register', response_model=models.AuthToken, summary="Create a new user account")
async def register_new_user(
    user_data: models.AccountRegister, session: Session = Depends(get_database_session)
) -> models.AuthToken:
    """Register a new user and return generated auth tokens."""
    if not user_data.password:
        user_data.password = PASSWORD_DEFAULT
    created_account = account_service.register(session, user_data)
    if user_data.user_type == UserType.ADMIN:
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_USERNAME,
            MAIL_FROM=settings.MAIL_USERNAME,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER="smtp.gmail.com",
            MAIL_TLS=True,
            MAIL_SSL=False
        )
        template = f"Your password: {created_account.password}"
        validation = validate_email(user_data.mail_address)
        validated_email = validation["email"]
        message = MessageSchema(
            subject="Welcome to Health Care",
            body=template,
            recipients=[validated_email],
            subtype="html",
        )
        fm = FastMail(conf)
        await fm.send_message(message)
    return create_auth_tokens(str(created_account.id))


# @router.post('/upload_file', summary='upload file when register')
# async def upload_file(
#     avatar_file: UploadFile = File(default=None),
#     db: Session = Depends(get_database_session),
# ):
#     file_name = f'{generate_uuid()}'
#     avt_name = create_and_save_file(file=avatar_file, file_name=file_name)['path']
#     return {'new_avatar': avt_name}


@router.post('/validate_email', summary='Validate email during registration')
def validate_email_for_registration(
    account_data: models.AccountEmailValidation,
    db: Session = Depends(get_database_session),
):
    """Check if the email address already exists."""
    existing_account = (
        db.query(models.Account)
        .filter(models.Account.mail_address == account_data.mail_address)
        .first()
    )
    if existing_account:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Email address already exists")
    return {
        'status': status.HTTP_200_OK,
        "message": "Validate Email OK",
    }


@router.post('/login', response_model=models.auth.LoginResponse, summary='User login')
async def login(payload: models.AccountLogin, db: Session = Depends(get_database_session)):
    """Authenticate user and return generated auth tokens."""
    authenticated_account = account_service.authenticate(db, payload)
    return {**create_auth_tokens(str(authenticated_account.id)).dict(), "user_type": authenticated_account.user_type}


@router.post(
    '/login_with_form',
    response_model=models.auth.AuthToken,
    summary='User login using form data',
)
async def login_with_form(
    payload: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_database_session),
):
    """Authenticate user using form data and return generated auth tokens."""
    authenticated_account = account_service.authenticate(
        db,
        payload=models.AccountLogin(mail_address=payload.username, password=payload.password),
    )
    return create_auth_tokens(str(authenticated_account.id))


@router.patch('/change_password', summary='Change password')
def change_user_password(
    payload: models.ChangePassword,
    db: Session = Depends(get_database_session),
    current_user: models.Account = Depends(get_current_authenticated_user),
):
    """Change the password for the authenticated user."""
    is_password_correct = security.verify_password(payload.old_password, current_user.password)
    if not is_password_correct:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is incorrect"
        )

    account_service.update(db, current_user.account_id, payload.new_password)
    return {'is_success': True, 'message': "Password changed successfully"}


def configure_oauth_settings():
    """Configure OAuth settings for Google registration."""
    return {
        'app_id': settings.GOOGLE_APP_ID,
        'app_secret': settings.GOOGLE_APP_SECRET,
        'token_url': settings.GOOGLE_TOKEN_URL,
        'scope': settings.GOOGLE_SCOPE,
        'profile_url': 'https://www.googleapis.com/oauth2/v1/userinfo',
    }


# from google.oauth2 import id_token
# from google.auth import transport
#
#
# @router.post('/login_with_oauth/google')
# async def login_with_google(
#     request: Request,
#     body: TokenRequest,
#     db_session: Session = Depends(get_database_session),
# ):
#     try:
#         # Fetch OAuth token
#         client_id = (
#             settings.GOOGLE_IOS_APP_CLIENT_ID
#             if body.device_type == DeviceType.IOS
#             else settings.GOOGLE_ANDROID_APP_CLIENT_ID
#         )
#         profile_info = id_token.verify_oauth2_token(
#             body.token, transport.requests.Request(), client_id
#         )
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f'Failed to fetch token: {str(e)}',
#         ) from e
#
#     provider_account_id = profile_info['sub']
#
#     account = crud.account_service.authenticate_with_oauth(
#         db=db_session, provider_account_id=provider_account_id, provider=OauthProvider.GOOGLE
#     )
#
#     return create_auth_tokens(str(account.account_id))
#
#
# @router.post("/register_with_oauth/google")
# async def register_with_google(
#     request: Request,
#     account_data: AccountRegisterWithGoogle,
#     db_session: Session = Depends(get_database_session),
# ):
#     """
#     Register a new account with Google OAuth and return authentication tokens.
#
#     Parameters:
#     - request: Request object containing client request information.
#     - account_data: Account registration data from Google OAuth.
#     - db_session: Database session for account creation.
#
#     Returns:
#     Dictionary containing authentication tokens.
#     """
#
#     try:
#         # Fetch OAuth token
#         client_id = (
#             settings.GOOGLE_IOS_APP_CLIENT_ID
#             if account_data.device_type == DeviceType.IOS
#             else settings.GOOGLE_ANDROID_APP_CLIENT_ID
#         )
#         profile_info = id_token.verify_oauth2_token(
#             account_data.token, transport.requests.Request(), client_id
#         )
#
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail=f'Failed to fetch token: {str(e)}',
#         ) from e
#
#     provider_account_id = profile_info['sub']
#
#     if crud.account_service.check_exist_account(
#         db=db_session, provider_account_id=provider_account_id, provider=OauthProvider.GOOGLE
#     ):
#         raise HTTPException(
#             status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#             detail='This google account has already!',
#         )
#
#     # Update account data with profile ID
#     account_data.__dict__['provider_account_id'] = profile_info['sub']
#     account_data.__dict__['provider'] = OauthProvider.GOOGLE
#
#     # Create a new user account from OAuth data
#     new_account = crud.account_service.create_user_from_oauth(
#         db_session=db_session, oauth_data=account_data
#     )
#     res = requests.post(f"{ai_url}/add_user", json=convert_data_user(new_account))
#     if not res.json()['status']:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail='Update AI unsuccessful!!',
#         )
#
#     return create_auth_tokens(str(new_account.account_id))
#
# # Login Apple
# @router.post('/login_with_oauth/apple')
# async def login_with_apple(
#     # request: Request,
#     body: TokenRequest,
#     db_session: Session = Depends(get_database_session),
# ):
#     # Validator token
#     res = requests.get('https://appleid.apple.com/auth/keys')
#     jwks = res.json()
#     # Decode the token to obtain the header
#     header = jwt.get_unverified_header(body.token)
#     matching_key = None
#     for key in jwks["keys"]:
#         if key["kid"] == header["kid"]:
#             matching_key = key
#             break
#     if matching_key:
#         try:
#             decoded_token = jwt.decode(body.token, matching_key, algorithms=["RS256"], audience='com.zenintegration.aibusinessmatching')
#             provider_account_id = decoded_token['sub']
#
#             account = crud.account_service.authenticate_with_oauth(
#                 db=db_session, provider_account_id=provider_account_id, provider=OauthProvider.APPLE
#             )
#             return create_auth_tokens(str(account.account_id))
#         except jwt.JWTError as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f'Failed to fetch token: {str(e)}',
#             ) from e
#
#
# @router.post("/register_with_oauth/apple")
# async def register_with_apple(
#     request: Request,
#     account_data: AccountRegisterWithGoogle,
#     db_session: Session = Depends(get_database_session),
# ):
#     # Validator token
#     res = requests.get('https://appleid.apple.com/auth/keys')
#     jwks = res.json()
#     # Decode the token to obtain the header
#     header = jwt.get_unverified_header(account_data.token)
#     matching_key = None
#     for key in jwks["keys"]:
#         if key["kid"] == header["kid"]:
#             matching_key = key
#             break
#     if matching_key:
#         try:
#             decoded_token = jwt.decode(account_data.token, matching_key, algorithms=["RS256"],
#                                        audience='com.zenintegration.aibusinessmatching')
#             provider_account_id = decoded_token['sub']
#
#             if crud.account_service.check_exist_account(
#                     db=db_session, provider_account_id=provider_account_id, provider=OauthProvider.APPLE
#             ):
#                 raise HTTPException(
#                     status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#                     detail='This apple account has already!',
#                 )
#
#             # Update account data with profile ID
#             account_data.__dict__['provider_account_id'] = decoded_token['sub']
#             account_data.__dict__['provider'] = OauthProvider.APPLE
#
#             # Create a new user account from OAuth data
#             new_account = crud.account_service.create_user_from_oauth(
#                 db_session=db_session, oauth_data=account_data
#             )
#             res = requests.post(f"{ai_url}/add_user", json=convert_data_user(new_account))
#             if not res.json()['status']:
#                 raise HTTPException(
#                     status_code=status.HTTP_400_BAD_REQUEST,
#                     detail='Update AI unsuccessful!!',
#                 )
#             return create_auth_tokens(str(new_account.account_id))
#         except jwt.JWTError as e:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail=f'Failed to fetch token: {str(e)}',
#             ) from e


@router.post(
    '/refresh',
    response_model=models.auth.AuthToken,
    summary='Generate 1 access new token from refresh token',
)
def refresh_token(
    body: models.RefeshTokenPayload,
    db: Session = Depends(get_database_session),
):
    payload, e = security.validate_refresh_token(body.refresh_token)
    if e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

    try:
        account = account_service.get_by_id(
            db=db,
            id=payload.get('sub'),
            raise_exception=True,
            exception_detail='Account not found',
        )
        if account.is_deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='account not found')
        access_token = security.create_access_token(
            subject=account.id,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
    except Exception as e:
        error = e.__class__.__name__
        if error == 'MissingTokenError':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Please provide refresh token',
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    return models.auth.AuthToken(
        access_token=access_token, token_type='bearer', refresh_token=body.refresh_token
    )
