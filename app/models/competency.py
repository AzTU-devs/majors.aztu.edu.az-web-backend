from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    ForeignKey    
)

from sqlalchemy.orm import relationship
from app.db.database import Base

class Competency(Base):
    __tablename__ = "competency"

    id = Column(Integer, primary_key=True, index=True)
    specialty_code = Column(String, ForeignKey("specialties.specialty_code"), nullable=False)
    competency_code = Column(String, nullable=False, unique=True)

    translations = relationship("CompetencyTranslation", back_populates="competency")
    specialty = relationship("Specialty", back_populates="competency")