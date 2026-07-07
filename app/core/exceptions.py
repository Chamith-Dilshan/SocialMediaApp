class AppException(Exception):
    def __init__(
        self,
        message: str,
        status_code: int = 400,
    ):
        self.message = message
        self.status_code = status_code


class NotFoundException(AppException):
    pass


class ConflictException(AppException):
    pass


class ValidationException(AppException):
    pass
