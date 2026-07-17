from typing import Annotated

from fastapi import APIRouter, Depends

from configuration.authentication import get_current_user
from dto.response.user_response import UserResponse

router = APIRouter(
    prefix='/api/users',
    tags=['User']
)


@router.get('/me', response_model=UserResponse)
async def get_current_user(current_user: Annotated[UserResponse, Depends(get_current_user)]):
    return current_user
