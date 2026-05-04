from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from app.db.database import Base

class CurriculaProgram(Base):
    __tablename__ = "curricula_program"
    
    id = Column(Integer, primary_key=True, index=True)
    specialty_code = Column(String, ForeignKey("specialties.specialty_code"), nullable=False)
    subject_code = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    # 1 - autumn semester
    # 2 - spring semester
    status = Column(Integer, nullable=False)
    # 1 - selection
    # 2 - mandatory
    # 3 - other
    credit = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    hours_per_week = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    specialty = relationship("Specialty", back_populates="curricula_programs")
    translations = relationship("CurriculaProgramTranslations", back_populates="curricula_program", cascade="all, delete-orphan")