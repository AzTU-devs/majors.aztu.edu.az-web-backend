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
    # Literature is attached to a subject (curricula_program.subject_code).
    subject_code = Column(String, nullable=True, index=True)
    # Legacy: kept nullable for backward compatibility.
    specialty_code = Column(Integer, nullable=True)
    url = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)