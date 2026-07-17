from typing import TypeVar, Generic, Any

from pydantic import BaseModel, model_serializer

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    status: int = 200
    message: str = ''
    data: T | None = None

    @model_serializer(mode='wrap')
    def serialize_model(self, handler: Any, **kwargs) -> dict[str, Any]:
        result = handler(self, **kwargs)
        if isinstance(result, dict):
            return {k: v for k, v in result.items() if v is not None}
        return result
