class MartsorError(Exception):
    """Base exception for martsor."""


class APIError(MartsorError):
    """Raised when the Soroush Plus API returns an error."""

    def __init__(
        self,
        message,
        error_code=None,
        status_code=None,
        response=None,
        retry_after=None,
    ):
        super().__init__(message)

        self.error_code = error_code
        self.status_code = status_code
        self.response = response
        self.retry_after = retry_after