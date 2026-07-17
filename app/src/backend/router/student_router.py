from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.requests import Request

from configuration.authentication import get_current_user
from configuration.authorization import require_roles
from configuration.rate_limit import limiter
from dto.request.student_request import StudentRequest
from dto.response.api_response import ApiResponse
from dto.response.student_response import StudentResponse
from enums.role import Role
from service.student_service import StudentService, get_student_service

router = APIRouter(
    prefix='/api/students',
    tags=['Student']
)


@router.get('', response_model=ApiResponse[list[StudentResponse]])
async def get_all_students(
        student_service: Annotated[StudentService, Depends(get_student_service)],
        _=Depends(get_current_user)
):
    return await student_service.get_all_students()


@router.post('', response_model=ApiResponse[StudentResponse])
@limiter.limit('5/minute')
async def create_student(
        request: Request,
        data: StudentRequest,
        student_service: Annotated[StudentService, Depends(get_student_service)],
        _=Depends(require_roles(Role.ADMIN.value))
):
    return await student_service.create_student(data)


@router.put('/{student_id}', response_model=ApiResponse[StudentResponse])
async def update_student(
        student_id: int,
        data: StudentRequest,
        student_service: Annotated[StudentService, Depends(get_student_service)],
        _=Depends(require_roles(Role.ADMIN.value))
):
    return await student_service.update_student(student_id, data)


@router.delete('/{student_id}', response_model=ApiResponse)
async def delete_student(
        student_id: int,
        student_service: Annotated[StudentService, Depends(get_student_service)],
        _=Depends(require_roles(Role.ADMIN.value))
):
    return await student_service.delete_student(student_id)
