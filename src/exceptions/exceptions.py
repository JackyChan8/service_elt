from fastapi import HTTPException


class MyHTTPException(HTTPException):
    """
        Exception overriding
    """
    def __init__(self, status_code: int, status: str, message: str):
        super().__init__(
            status_code=status_code,
            detail=message,
        )
        self.message = message
        self.status = status
