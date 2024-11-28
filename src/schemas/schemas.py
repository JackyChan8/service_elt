from enum import Enum

from pydantic import BaseModel


class StatusResponseEnum(str, Enum):
    """
        Schema Response Sign In Status
    """
    PENDING: str = 'pending'
    SUCCESS: str = 'success'
    ERROR:   str = 'error'


class ResponseBase(BaseModel):
    """
        Base Schema Response
    """
    status: StatusResponseEnum = StatusResponseEnum.SUCCESS
    message: str
