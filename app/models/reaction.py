from sqlalchemy import ForeignKey, String, Float, Column, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Reaction(Base):
    __tablename__ = "reactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    summary: Mapped[str] = mapped_column(String(255))
    confidence_score: Mapped[float] = mapped_column(Float)
    parser_version: Mapped[str] = mapped_column(String(50))

    # Structured fields for chemical reaction details
    reagents = Column(JSON, nullable=True, default=list)  # list of {name, quantity}
    solvents = Column(JSON, nullable=True, default=list)  # list of strings
    conditions = Column(
        JSON, nullable=True, default=dict
    )  # {temperature, time, atmosphere}
    yield_percentage = Column(Float, nullable=True)

    document = relationship("Document")
