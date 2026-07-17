from pydantic import BaseModel, ConfigDict


class StudentResponse(BaseModel):
    id: int
    name: str
    year_of_birth: int

    model_config = ConfigDict(from_attributes=True)
