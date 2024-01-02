from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple, Union

from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import ValidationError

from health.core import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"


def _create_token(
    subject: Union[str, Any],
    token_type: str,
    expires_delta: timedelta = None,
    user_claims: Dict[str, Any] = None,
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    token_data = {
        'exp': expire,
        'sub': str(subject),
        'token_type': token_type,
    }
    if user_claims:
        token_data.update(user_claims)

    encoded_jwt = jwt.encode(token_data, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def _validate_token(token: str, token_type: str) -> Tuple[Dict[str, Any], Optional[str]]:
    payload = e = None
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get('token_type') != token_type:
            e = "Invalid token type"
    except (JWTError, ValidationError):
        e = "Could not validate credentials"
    except Exception as e:
        e = "Bad token"

    return payload, e


def create_access_token(
    subject: Union[str, Any],
    expires_delta: timedelta = None,
    user_claims: Dict[str, Any] = None,
) -> str:
    return _create_token(subject, 'access_token', expires_delta, user_claims)


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: timedelta = None,
    user_claims: Dict[str, Any] = None,
) -> str:
    return _create_token(subject, 'refresh_token', expires_delta, user_claims)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def validate_access_token(token: str) -> Tuple[Dict[str, Any], Optional[str]]:
    return _validate_token(token, 'access_token')


def validate_refresh_token(token: str) -> Tuple[Dict[str, Any], Optional[str]]:
    return _validate_token(token, 'refresh_token')
