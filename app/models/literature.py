from sqlalchemy import (
    Column, 
    Integer, 
    DateTime,
    String   
)

from sqlalchemy.orm import relationship
from app.db.database import Base

class Literature(Base):
    __tablename__ = "literature"

    id = Column(Integer, primary_key=True, index=True)
    literature_code = Column(Integer, unique=True, nullable=False)
    specialty_code = Column(Integer, nullable=False)
    url = Column(String,nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)