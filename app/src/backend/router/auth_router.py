from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request

from configuration.rate_limit import limiter
from dto.response.auth_response import AuthResponse
from service.auth_service import AuthService, get_auth_service

router = APIRouter(
    prefix='/api/auth',
    tags=['Authentication']
)


@router.post('/login', response_model=AuthResponse)
@limiter.limit('5/minute')
async def authenticate(
        request: Request,
        data: Annotated[OAuth2PasswordRequestForm, Depends()],
        auth_service: Annotated[AuthService, Depends(get_auth_service)]
):
    return await auth_service.authenticate(data)
