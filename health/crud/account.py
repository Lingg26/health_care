from typing import Optional

from fastapi import File, HTTPException, status
from sqlalchemy.orm import Session

from health import models
from health.core.security import verify_password
from health.models.account import Account
from health.models.account import Account as AccountModel
# from health.models.account import AccountRegisterWithGoogle
# from health.models.oauth_account import OauthAccount
# from health.shared.core_type import OauthProvider

# from ..shared.file_operator import create_and_save_file
# from ..utils import generate_uuid
from .base import CrudBase


class Account(CrudBase):
    model = AccountModel

    def get_all(self, db: Session) -> list[AccountModel]:
        query = db.query(AccountModel)
        return query.all()

    def register(self, db: Session, payload: models.AccountRegister):
        exist_account = db.query(self.model).filter(
            self.model.mail_address == payload.mail_address,
            self.model.password.isnot(None)
        ).first()
        if exist_account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='The account has already!',
            )
        new_account = self.create(db, payload)
        # new_account.check_avt(db)
        return new_account

    def authenticate(
        self,
        db: Session,
        payload: models.AccountLogin,
    ) -> Optional[AccountModel]:
        account = db.query(self.model).filter(
            models.Account.mail_address == payload.mail_address,
            models.Account.password.isnot(None),
        ).first()
        if not account:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Account does not exist',
            )

        if not verify_password(payload.password, account.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Email or pasword is incorrect',
            )
        return account

    # def authenticate_with_oauth(
    #     self, db: Session, provider_account_id: int, provider: str
    # ) -> Optional[AccountModel]:
    #     oauth_account = self.check_exist_account(
    #         db=db, provider_account_id=provider_account_id, provider=provider
    #     )
    #     if not oauth_account:
    #         raise HTTPException(
    #             status_code=status.HTTP_404_NOT_FOUND, detail='登録されていないメールアドレスです。'
    #         )
    #     account = self.get_by_id(
    #         db=db,
    #         id=oauth_account.user_id,
    #         raise_exception=True,
    #         exception_detail='登録されていないメールアドレスです。',
    #     )
    #     if account.is_deleted:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail='アカウントが削除されました。',
    #         )
    #     return account
    #
    # def check_exist_account(self, db: Session, provider_account_id, provider: OauthProvider.GOOGLE):
    #     oauth_account = (
    #         db.query(OauthAccount)
    #         .filter(
    #             OauthAccount.provider_user_id == provider_account_id,
    #             OauthAccount.provider == provider,
    #         )
    #         .first()
    #     )
    #     return oauth_account
    #
    # def create_user_from_oauth(
    #     self, db_session: Session, oauth_data: AccountRegisterWithGoogle
    # ) -> AccountModel:
    #     """
    #     Create or update a user account based on OAuth information.
    #
    #     Parameters:
    #     - db_session: Database session to execute queries.
    #     - oauth_data: Account registration data from Google OAuth.
    #
    #     Returns:
    #     An AccountModel object of the created or updated account.
    #     """
    #     # Create a new account if it doesn't exist
    #     existing_account = self.create(
    #         db_session,
    #         default_data=oauth_data.dict(
    #             exclude={'token', 'redirect_uri', 'provider_account_id', 'provider'}
    #         ),
    #     )
    #
    #     # Create a new OAuth account record if it doesn't exist
    #     oauth_account = OauthAccount(
    #         user_id=existing_account.account_id,
    #         provider=oauth_data.provider,
    #         provider_user_id=oauth_data.provider_account_id,
    #     )
    #
    #     # Update the user ID for the OAuth account
    #     oauth_account.user_id = existing_account.account_id
    #
    #     # Save the OAuth account data to the database
    #     db_session.add(oauth_account)
    #     db_session.flush()
    #     db_session.commit()
    #
    #     return existing_account
    #
    # def upload_avatar(self, db: Session, account: Account, avt_file: File):
    #     account = db.query(self.model).filter_by(account_id=account.account_id).first()
    #     if not account:
    #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='登録されていないメールアドレスです。')
    #     try:
    #         file_name = f'{generate_uuid()}'
    #         avt_name = create_and_save_file(file=avt_file, file_name=file_name)['path']
    #         account.upload_file_path = avt_name
    #         db.add(account)
    #         db.commit()
    #         db.refresh(account)
    #         return account
    #     except Exception:
    #         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="")


account_service = Account()
