from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    UniqueConstraint,
    CHAR,
    Text
)
from sqlalchemy.orm import relationship
from app.db.database import Base

class SloTranslation(Base):
    __tablename__ = "slo_translations"
    __table_args__ = (
        UniqueConstraint("slo_code", "language_code"),
    )

    id = Column(Integer, primary_key=True, index=True)
    slo_code = Column(String, ForeignKey("slo.slo_code"), nullable=False)
    language_code = Column(CHAR(2), nullable=False)
    slo_content = Column(Text, nullable=False)

    slo = relationship("Slo", back_populates="translations")

