from enum import Enum

from starlette import status


class ErrorCode(Enum):
    UNCATEGORIZED_ERROR = ('Uncategorized error', status.HTTP_500_INTERNAL_SERVER_ERROR)
    LOGIN_FAILED = ('Invalid username or password', status.HTTP_401_UNAUTHORIZED)
    UNAUTHENTICATED = ('Could not validate credentials', status.HTTP_401_UNAUTHORIZED)
    UNAUTHORIZED = ('Permission denied', status.HTTP_403_FORBIDDEN)
    INVALID_NAME = ('Invalid name', status.HTTP_400_BAD_REQUEST)
    INVALID_YEAR_OF_BIRTH = ('Invalid year of birth', status.HTTP_400_BAD_REQUEST)
    STUDENT_NOT_FOUND = ('Student not found', status.HTTP_404_NOT_FOUND)
    TOO_MANY_REQUESTS = ('Too many requests', status.HTTP_429_TOO_MANY_REQUESTS)

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
