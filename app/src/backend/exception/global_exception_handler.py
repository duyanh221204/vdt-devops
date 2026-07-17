from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from slowapi.errors import RateLimitExceeded
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from dto.response.api_response import ApiResponse
from enums.error_code import ErrorCode
from exception.app_exception import AppException


def add_exception_handlers(app: FastAPI):
    @app.exception_handler(AppException)
    async def app_exception_handler(_: Request, exc: AppException) -> JSONResponse:
        error = exc.error_code
        response = ApiResponse(
            status=error.status_code,
            message=error.message
        )
        return JSONResponse(
            status_code=error.status_code,
            content=response.model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
        msg = exc.errors()[0].get('msg', '')
        try:
            error = ErrorCode[msg.removeprefix('Value error, ')]
            status_code = error.status_code
            message = error.message
        except Exception:
            status_code = status.HTTP_400_BAD_REQUEST
            message = msg

        response = ApiResponse(
            status=status_code,
            message=message
        )
        return JSONResponse(
            status_code=status_code,
            content=response.model_dump()
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exception_handler(_: Request, __: RateLimitExceeded) -> JSONResponse:
        error = ErrorCode.TOO_MANY_REQUESTS
        response = ApiResponse(
            status=error.status_code,
            message=error.message
        )
        return JSONResponse(
            status_code=error.status_code,
            content=response.model_dump()
        )

    @app.exception_handler(Exception)
    async def uncategorized_exception_handler(_: Request, __: Exception) -> JSONResponse:
        error = ErrorCode.UNCATEGORIZED_ERROR
        response = ApiResponse(
            status=error.status_code,
            message=error.message
        )
        return JSONResponse(
            status_code=error.status_code,
            content=response.model_dump()
        )
