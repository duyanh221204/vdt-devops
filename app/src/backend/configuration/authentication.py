import os
from datetime import timedelta, datetime, timezone
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from configuration.database import get_db
from dto.response.user_response import UserResponse
from enums.error_code import ErrorCode
from exception.app_exception import AppException
from model.user import User

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = os.getenv('ALGORITHM')

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/api/auth/login', auto_error=False)


def hash_password(plain_password: str) -> str:
    return bcrypt_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expired_delta: timedelta) -> str:
    to_encode = data.copy()
    expires = datetime.now(timezone.utc) + expired_delta
    to_encode.update({'exp': expires})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(
        token: Annotated[str | None, Depends(oauth2_bearer)],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> UserResponse:
    if not token:
        raise AppException(ErrorCode.UNAUTHENTICATED)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise AppException(ErrorCode.UNAUTHENTICATED)

    user_id: int | None = int(payload.get('sub'))
    if user_id is None:
        raise AppException(ErrorCode.UNAUTHENTICATED)

    user: User | None = (await db.execute(select(User).where(User.id == user_id))).scalar_one_or_none()
    if user is None:
        raise AppException(ErrorCode.UNAUTHENTICATED)

    return UserResponse(id=user_id, username=user.username, role=user.role)
