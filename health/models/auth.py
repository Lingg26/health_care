from datetime import timedelta
from typing import Optional

from sqlmodel import Field, SQLModel

from health.core import security
from health.core.settings import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_MINUTES,
)


class AuthToken(SQLModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str

class LoginResponse(AuthToken):
    user_type: Optional[str]


class AuthTokenPayload(SQLModel):
    sub: Optional[str] = None
    token_type: Optional[str] = None


class RefeshTokenPayload(SQLModel):
    refresh_token: str = Field()


# Helper function to create auth tokens
def create_auth_tokens(account_id: str) -> AuthToken:
    """Generate access and refresh tokens for the given account ID"""
    access_token = security.create_access_token(
        subject=account_id,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = security.create_refresh_token(
        subject=account_id,
        expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
    )
    return AuthToken(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type='bearer',
    )
