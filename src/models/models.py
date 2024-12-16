from sqlalchemy import (
    Text,
    func,
    JSON,
    String,
    Integer,
    TIMESTAMP,
    BigInteger,
    ForeignKey,
)
from sqlalchemy.orm import mapped_column, relationship, Mapped

from src.models.base_class import Base


class InsuranceElt(Base):
    __tablename__ = 'insurance_elt'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    insurance_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('insurance.id'), nullable=False)
    calc_id: Mapped[int] = mapped_column(BigInteger, default=None, nullable=False)
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
    payments_period: Mapped[dict] = mapped_column(JSON, default=dict, nullable=True)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Связь с моделью Insurance
    insurance = relationship(
        "Insurance",
        back_populates="insurance_elts",
        single_parent = True,
    )


class Insurance(Base):
    __tablename__ = 'insurance'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    calc_reso_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True, default=None)
    calc_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True, default=None)
    quote_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True, default=None)
    police_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=True, default=None)
    created_at: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Связь с моделью InsuranceElt
    insurance_elts = relationship(
        "InsuranceElt",
        back_populates="insurance",
        cascade="all, delete-orphan"
    )


class Cars(Base):
    __tablename__ = 'cars'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    brand: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    model: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    modif: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    sk_brand: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    sk_model: Mapped[str] = mapped_column(Text, nullable=True, default=None)
    type: Mapped[str] = mapped_column(String(5), nullable=True, default=None)
