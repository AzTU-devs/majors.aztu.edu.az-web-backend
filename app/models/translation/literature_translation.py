from sqlalchemy import (
    Column, 
    String, 
    Integer, 
    ForeignKey,
    DateTime,
    VARCHAR   
)

from sqlalchemy.orm import relationship
from app.db.database import Base

class LiteratureTrans(Base):
    __tablename__ = "literature_translations"
    id = Column(Integer, primary_key=True, index=True)
    language_code = Column(VARCHAR(2), nullable=False)
    literature_code = Column(String, nullable=False)
    literature_name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)