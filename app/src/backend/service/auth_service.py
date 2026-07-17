import os
from datetime import timedelta
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from configuration.authentication import verify_password, create_access_token
from configuration.database import get_db
from dto.response.auth_response import AuthResponse
from enums.error_code import ErrorCode
from exception.app_exception import AppException
from model.user import User

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRED_MINUTES'))


def get_auth_service(db: Annotated[AsyncSession, Depends(get_db)]):
    return AuthService(db)


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, data: OAuth2PasswordRequestForm) -> AuthResponse:
        user: User | None = (await self.db.execute(select(User).where(User.username == data.username))).scalar_one_or_none()
        if user is None or not verify_password(data.password, user.hashed_password):
            raise AppException(ErrorCode.LOGIN_FAILED)

        access_token = create_access_token(
            data={'sub': str(user.id)},
            expired_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        return AuthResponse(access_token=access_token)
