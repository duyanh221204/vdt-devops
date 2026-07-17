from typing import Annotated

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from configuration.database import get_db
from dto.request.student_request import StudentRequest
from dto.response.api_response import ApiResponse
from dto.response.student_response import StudentResponse
from enums.error_code import ErrorCode
from exception.app_exception import AppException
from model.student import Student


def get_student_service(db: Annotated[AsyncSession, Depends(get_db)]):
    return StudentService(db)


class StudentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_students(self) -> ApiResponse[list[StudentResponse]]:
        students = (await self.db.execute(select(Student))).scalars().all()
        return ApiResponse(
            message='Retrieve all students successfully',
            data=[StudentResponse.model_validate(student) for student in students]
        )

    async def create_student(self, data: StudentRequest) -> ApiResponse[StudentResponse]:
        student = Student(**data.model_dump())
        self.db.add(student)
        await self.db.commit()
        await self.db.refresh(student)

        return ApiResponse(
            message='Create student successfully',
            data=StudentResponse.model_validate(student)
        )

    async def update_student(self, student_id: int, data: StudentRequest) -> ApiResponse[StudentResponse]:
        student = (await self.db.execute(select(Student).where(Student.id == student_id))).scalar_one_or_none()
        if student is None:
            raise AppException(ErrorCode.STUDENT_NOT_FOUND)

        for key, value in data.model_dump().items():
            setattr(student, key, value)
        await self.db.commit()
        await self.db.refresh(student)

        return ApiResponse(
            message='Update student successfully',
            data=StudentResponse.model_validate(student)
        )

    async def delete_student(self, student_id: int) -> ApiResponse[None]:
        student = (await self.db.execute(select(Student).where(Student.id == student_id))).scalar_one_or_none()
        if student is None:
            raise AppException(ErrorCode.STUDENT_NOT_FOUND)

        await self.db.delete(student)
        await self.db.commit()

        return ApiResponse(message='Delete student successfully')
