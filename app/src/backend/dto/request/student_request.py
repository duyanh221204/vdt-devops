from pydantic import BaseModel, field_validator

from enums.error_code import ErrorCode


class StudentRequest(BaseModel):
    name: str
    year_of_birth: int

    @field_validator('name')
    @classmethod
    def validate_name(cls, value: str) -> str:
        if value is None or not value.strip():
            raise ValueError(ErrorCode.INVALID_NAME.name)
        return value

    @field_validator('year_of_birth')
    @classmethod
    def validate_year_of_birth(cls, value: int) -> int:
        if value is None or not 2000 <= value <= 2010:
            raise ValueError(ErrorCode.INVALID_YEAR_OF_BIRTH.name)
        return value
