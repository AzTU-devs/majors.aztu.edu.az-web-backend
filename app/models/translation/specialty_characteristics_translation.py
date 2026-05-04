from sqlalchemy import Column, String, Integer, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class SpecialtyCharacteristicsTranslation(Base):
    __tablename__ = "specialty_characteristics_translations"

    id = Column(Integer, primary_key=True, index=True)
    specialty_characteristic_id = Column(Integer, ForeignKey("specialty_characteristics.id"),nullable=False)
    language_code = Column(CHAR(2), nullable=False)  
    program_desc = Column(String, nullable=True)
    degree_requirements = Column(String, nullable=True)


    specialty_characteristics = relationship("SpecialtyCharacteristics", back_populates="translations")
