from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class SpecialtyCharacteristics(Base):
    __tablename__ = "specialty_characteristics"

    id = Column(Integer, primary_key=True, index=True)
    specialty_code = Column(String, ForeignKey("specialties.specialty_code"), nullable=False)

    translations = relationship("SpecialtyCharacteristicsTranslation", back_populates="specialty_characteristics")
    specialty = relationship("Specialty", back_populates="specialty_characteristics")
