from typing import Annotated

from fastapi import Depends

from configuration.authentication import get_current_user
from dto.response.user_response import UserResponse
from enums.error_code import ErrorCode
from exception.app_exception import AppException


def require_roles(*roles):
    def checker(user: Annotated[UserResponse, Depends(get_current_user)]):
        if user.role not in roles:
            raise AppException(ErrorCode.UNAUTHORIZED)
        return user
    return checker
