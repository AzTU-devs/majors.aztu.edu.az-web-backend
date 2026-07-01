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
    # Academic year, free text like "2025-2026" (Akademik il)
    year = Column(String, nullable=False)
    hours_per_week = Column(Integer, nullable=False)
    # 1 - Əyani (Full-time), 2 - Qiyabi (Correspondence)
    form_of_education = Column(Integer, nullable=True)
    # 1 - Azerbaijani, 2 - English, 3 - Russian
    language_of_instruction = Column(Integer, nullable=True)
    # Free text, e.g. "a) 30 saat - mühazirə b) 15 saat - seminar"
    in_class_hours = Column(String, nullable=True)
    # Auditoriya kənar saatlar (out-of-classroom hours), free text
    out_of_class_hours = Column(String, nullable=True)
    # Comma-separated teaching method keys (lecture, seminar, lab, ...)
    teaching_methods = Column(String, nullable=True)
    # JSON array of {form, description, score, ftn}
    assessment = Column(String, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    specialty = relationship("Specialty", back_populates="curricula_programs")
    translations = relationship("CurriculaProgramTranslations", back_populates="curricula_program", cascade="all, delete-orphan")