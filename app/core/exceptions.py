class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundException(AppException):
    pass


class ConflictException(AppException):
    pass


class ValidationException(AppException):
    pass


class DatabaseException(AppException):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message=message, status_code=500)


class DatabaseException(AppException):
    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message=message, status_code=500)
