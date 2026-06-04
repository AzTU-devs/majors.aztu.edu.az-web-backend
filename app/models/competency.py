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
    # 1 - Peşə Səriştələri (Job competency)
    # 2 - İxtisas Səriştələri (Specialty competency)
    competency_type = Column(Integer, nullable=False, server_default="2")

    translations = relationship("CompetencyTranslation", back_populates="competency")
    specialty = relationship("Specialty", back_populates="competency")