from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    DateTime,
    ForeignKey,
    CheckConstraint
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class SpecialtyTranslations(Base):
    __tablename__ = "specialty_translations"
    __table_args__ = (
        UniqueConstraint("specialty_name"),
        CheckConstraint("language_code IN ('en', 'az')")
    )

    id = Column(Integer, primary_key=True, index=True)
    specialty_code = Column(String, ForeignKey("specialties.specialty_code"), nullable=False, unique=True)
    language_code = Column(String, nullable=False)
    specialty_name = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    specialty = relationship("Specialty", back_populates="specialty_translations")