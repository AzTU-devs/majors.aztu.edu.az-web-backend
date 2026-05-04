from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class Cafedra(Base):
    __tablename__ = "cafedras"

    id = Column(Integer, primary_key=True, index=True)
    faculty_code = Column(String, ForeignKey("faculties.faculty_code"), nullable=False)
    cafedra_code = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    faculty = relationship("Faculty", back_populates="cafedras")
    specialties = relationship("Specialty", back_populates="cafedra")
    translations = relationship("CafedraTranslations", back_populates="cafedra", cascade="all, delete-orphan")
    user = relationship("User", back_populates="cafedra", uselist=False)