from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    DateTime,
    ForeignKey
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class CurriculaProgramTranslations(Base):
    __tablename__ = "curricula_program_translations"
    
    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String, ForeignKey("curricula_program.subject_code"), nullable=False)
    language_code = Column(String(2), nullable=False)
    subject_name = Column(String, nullable=False)
    subject_description = Column(String)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    curricula_program = relationship("CurriculaProgram", back_populates="translations")