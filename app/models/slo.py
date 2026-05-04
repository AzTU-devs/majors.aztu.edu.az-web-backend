# slo model
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from app.db.database import Base

class Slo(Base):
    __tablename__ = "slo"
    
    id = Column(Integer, primary_key=True, index=True)
    specialty_code = Column(String, ForeignKey("specialties.specialty_code"), nullable=False)
    slo_code = Column(String, nullable=False, unique=True)

    specialty = relationship("Specialty", back_populates="slos")
    translations = relationship("SloTranslation", back_populates="slo")





