from sqlalchemy import (
    Integer,
    String,
    TIMESTAMP,
    Text,
    func,
)
from sqlalchemy.orm import mapped_column, Mapped

from src.models.base_class import Base


class InsuranceElt(Base):
    __tablename__ = 'insurance_elt'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    insurance_id: Mapped[int] = mapped_column(Integer, nullable=False)
    insurance_name: Mapped[str] = mapped_column(Text, nullable=False)
    RequestId: Mapped[str] = mapped_column(String)
    SKCalcId: Mapped[int] = mapped_column(String, default=None, nullable=True)
    Message: Mapped[str] = mapped_column(Text, default=None, nullable=True)
    Error: Mapped[str] = mapped_column(Text, default=None, nullable=True)
    PremiumSum: Mapped[int] = mapped_column(Integer)
    KASKOSum: Mapped[int] = mapped_column(Integer)
    DOSum: Mapped[int] = mapped_column(Integer)
    GOSum: Mapped[int] = mapped_column(Integer)
    NSSum: Mapped[int] = mapped_column(Integer)
    GAPSum: Mapped[int] = mapped_column(Integer)
    TotalFranchise: Mapped[int] = mapped_column(Integer, default=None, nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)
