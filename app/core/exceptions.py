class AppException(Exception):
    def __init__(
        self,
        status_code: int,
        message: str,
    ):
        self.status_code = status_code
        self.message = message


class NotFoundException(AppException):
    def __init__(self, message: str):
        super().__init__(404, message)

class ConflictException(AppException):
    pass

class ValidationException(AppException):
    pass

class PostNotFoundError(Exception):
    pass

class PostOwnershipError(Exception):
    pass


class UserNotFoundError(Exception):
    pass

class ForbiddenException(AppException):
    def __init__(self, message: str):
        super().__init__(403, message)

class DatabaseException(Exception):
    def __init__(
        self,
        message: str = "Database operation failed",
    ):
        self.message = message
        super().__init__(message)
