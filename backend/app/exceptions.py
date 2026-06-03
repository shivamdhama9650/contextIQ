"""Custom exception types for the backend API.

All domain‑specific errors should inherit from :class:`ServiceError` so that the
global error handler can convert them into a consistent JSON payload.
"""

class ServiceError(Exception):
    """Base class for service‑layer errors.

    Attributes
    ----------
    message: str
        Human‑readable description of the problem.
    status_code: int, optional
        HTTP status code to return (default 500).
    """

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
