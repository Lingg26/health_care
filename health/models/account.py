import re
from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from pydantic import EmailStr, validator
from sqlmodel import Field, SQLModel
from sqlalchemy import Column, Text

from health.core.security import get_password_hash
from health.shared.core_type import UserType
from health.shared.database import Base, TimestampMixin


class Account(Base, TimestampMixin, table=True):
    __tablename__ = 'account'

    account_name: str = Field(nullable=False)
    birthday: datetime = Field(nullable=False)
    tel: str = Field(nullable=False)
    mail_address: EmailStr = Field(nullable=False)
    notes: Optional[str] = Field(sa_column=Column(Text), nullable=True)
    upload_file_path: Optional[str] = Field(nullable=True)
    password: Optional[str] = Field()
    user_type: str = Field(nullable=False)


def is_strong_password(password: str) -> bool:
    pattern = r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$"
    return bool(re.match(pattern, password))


def _validate_and_hash_password(value):
    if not is_strong_password(value):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail='''Password should contain at least 8 characters, including uppercase,'''
                   ''' lowercase letters and numbers''',
        )
    return get_password_hash(value)


class AccountLogin(SQLModel):
    mail_address: EmailStr = Field()
    password: str = Field()


class AccountRegister(SQLModel):
    account_name: str = Field()
    birthday: datetime = Field()
    tel: str = Field()
    mail_address: EmailStr = Field()
    password: str = Field()
    notes: Optional[str] = Field(nullable=True)
    user_type: str = Field(nullable=False)

    @validator('password')
    def validate_and_hash_password(cls, value):
        return _validate_and_hash_password(value)

    @validator("mail_address")
    def validate_mail_address(cls, value):
        try:
            # Create an instance of the EmailStr field
            EmailStr(value)
        except ValueError:
            raise ValueError("Invalid email address")
        return value


class AccountEmailValidation(SQLModel):
    mail_address: EmailStr = Field()


class ChangePassword(SQLModel):
    old_password: str = Field()
    new_password: str = Field()

    @validator('new_password')
    def validate_and_hash_password(cls, value):
        return _validate_and_hash_password(value)


class RefeshTokenPayload(SQLModel):
    refresh_token: str = Field()

class UpdateProfileAccount(SQLModel):
    account_name: str = Field()
    birthday: datetime = Field()
    tel: str = Field()
    notes: Optional[str] = Field(nullable=True)

