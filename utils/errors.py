class AppError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(AppError):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message, status_code)


class ModelUnavailableError(AppError):
    def __init__(self, message: str):
        super().__init__(message, 503)


class DatabaseError(AppError):
    def __init__(self, message: str):
        super().__init__(message, 500)
