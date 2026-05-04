from sqlalchemy import (
    Column,
    String, 
    Integer,
    ForeignKey,
    UniqueConstraint,
    Text,
    CHAR
)

from app.db.database import Base
from sqlalchemy.orm import relationship

class PloTranslation(Base):
    __tablename__ = "plo_translations"
    __table_args__ = (
        UniqueConstraint("plo_code", "language_code"),
    )

    id = Column(Integer, primary_key=True, index=True)
    plo_code = Column(String, ForeignKey("plo.plo_code"), nullable=False)
    language_code = Column(CHAR(2), nullable=False)
    plo_content = Column(Text, nullable=False)

    plo = relationship("Plo", back_populates="translations")
