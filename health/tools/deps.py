from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from health import crud
from health.core import security, settings
from health.shared.database import SessionLocal

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f'{settings.API_V1_STR}/oauth/login_with_form')


class DBSessionFactory:
    def __init__(self, auto_commit: bool = False, session=None):
        self.auto_commit = auto_commit
        self.session = session

    def __call__(self) -> Generator[Session, None, None]:
        db = self.session or SessionLocal()
        try:
            yield db
            if self.auto_commit:
                db.commit()
        except:
            db.rollback()
            raise
        finally:
            db.close()


get_database_session = DBSessionFactory()
get_database_session_auto_commit = DBSessionFactory(auto_commit=True)


def get_current_authenticated_user(
    db: Session = Depends(get_database_session),
    token: str = Depends(oauth2_scheme),
):
    payload, e = security.validate_access_token(
        token
        if type(token) == str
        else token['token']
        if type(token) == dict
        else token.credentials
    )
    if e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e)
    object_id = payload.get('sub')
    account = crud.account_service.get_by_id(db, object_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='account not found')
    if account.is_deleted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='account is deleted')
    return account


def get_current_active_user(
    current_user=Depends(get_current_authenticated_user),
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
