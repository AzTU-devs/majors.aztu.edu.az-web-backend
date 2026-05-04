from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    ForeignKey    
)

from sqlalchemy.orm import relationship
from app.db.database import Base

class GCO(Base):
    __tablename__ = "graduate_career_opportunities"

    id = Column(Integer, primary_key=True, index=True)
    specialty_code = Column(String, ForeignKey("specialties.specialty_code"), nullable=False)
    career_code = Column(String, nullable=False, unique=True, index=True)

    translations = relationship("GCOTranslation", back_populates="career",)
    specialty = relationship("Specialty", back_populates="gco")