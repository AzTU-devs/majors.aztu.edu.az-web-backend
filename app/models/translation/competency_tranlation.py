from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    ForeignKey,
    Text,
    CHAR
)

from sqlalchemy.orm import relationship
from app.db.database import Base


class CompetencyTranslation(Base):
    __tablename__ = "competency_translation"

    id = Column(Integer, primary_key=True, index=True)
    competency_code = Column(String, ForeignKey("competency.competency_code"), nullable=False)
    language_code = Column(CHAR(2), nullable=False)
    competency_content = Column(Text, nullable=False)

    competency = relationship("Competency", back_populates="translations")
