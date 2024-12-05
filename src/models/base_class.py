from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import as_declarative
from sqlalchemy.ext.declarative import declared_attr


metadata = MetaData()


@as_declarative()
class Base:
    id: Any
    __name__: str
    metadata: MetaData

    @declared_attr
    def __tablename__(self) -> str:
        return self.__name__.lower()
