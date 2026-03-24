"""Custom exceptions for safe and consistent API errors."""


class AppError(Exception):
    """Base application error with an HTTP status code and public message."""

    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ValidationError(AppError):
    """Raised when input validation fails."""

    def __init__(self, message: str = "Invalid input.") -> None:
        super().__init__(message=message, status_code=400)


class ConversionError(AppError):
    """Raised when conversion logic fails in an expected way."""

    def __init__(self, message: str = "File conversion failed.") -> None:
        super().__init__(message=message, status_code=422)
