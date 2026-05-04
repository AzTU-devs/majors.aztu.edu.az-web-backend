from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    CHAR, 
    Text, 
    ForeignKey
)
from sqlalchemy.orm import relationship
from app.db.database import Base

class GCOTranslation(Base):
    __tablename__ = "graduate_career_opportunities_translations"

    id = Column(Integer, primary_key=True, index=True)
    career_code = Column(String, ForeignKey("graduate_career_opportunities.career_code"), nullable=False)
    career_title = Column(String)
    language_code = Column(CHAR(2), nullable=False)
    career_content = Column(Text, nullable=False)

    career = relationship("GCO", back_populates="translations")
