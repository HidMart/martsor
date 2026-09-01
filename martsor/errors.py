class MartsorError(Exception):
    """Base exception for martsor."""


class APIError(MartsorError):
    """Raised when the API returns an error."""

    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response