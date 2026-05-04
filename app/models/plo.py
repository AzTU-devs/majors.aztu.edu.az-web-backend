from sqlalchemy import (
    Column,
    String, 
    Integer,
    ForeignKey,
)

from sqlalchemy.orm import relationship
from app.db.database import Base

class Plo(Base):
    __tablename__ = "plo"

    id = Column(Integer, primary_key=True, index=True)
    specialty_code = Column(String, ForeignKey("specialties.specialty_code"), nullable=False)
    plo_code = Column(String, nullable=False, unique=True)

    specialty = relationship("Specialty", back_populates="plos")
    translations = relationship("PloTranslation", back_populates="plo")