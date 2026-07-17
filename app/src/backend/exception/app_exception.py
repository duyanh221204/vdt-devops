from enums.error_code import ErrorCode


class AppException(Exception):
    def __init__(self, error_code: ErrorCode):
        self.error_code = error_code
