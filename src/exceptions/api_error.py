"""
General base-case error for API class
"""


class APIError(Exception):
    """
    APIError is a ganeral error class for all API errors
    """

    def __init__(self, message: str, error_code: int = 400):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
