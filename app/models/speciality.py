from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    DateTime,
    ForeignKey
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class Specialty(Base):
    __tablename__ = "specialties"
    __table_args__ = (
        UniqueConstraint("specialty_code"),
    )

    id = Column(Integer, primary_key=True, index=True)
    cafedra_code = Column(String, ForeignKey("cafedras.cafedra_code"), nullable=False)
    specialty_code = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    cafedra = relationship("Cafedra", back_populates="specialties")
    specialty_translations = relationship("SpecialtyTranslations", back_populates="specialty", cascade="all, delete-orphan")
    plos = relationship("Plo", back_populates="specialty", cascade="all, delete-orphan")
    slos = relationship("Slo", back_populates="specialty", cascade="all, delete-orphan")
    gco = relationship("GCO", back_populates="specialty", cascade="all, delete-orphan")
    competency = relationship("Competency", back_populates="specialty", cascade="all, delete-orphan")
    specialty_characteristics = relationship("SpecialtyCharacteristics", back_populates="specialty", cascade="all, delete-orphan")
    curricula_programs = relationship("CurriculaProgram", back_populates="specialty", cascade="all, delete-orphan")