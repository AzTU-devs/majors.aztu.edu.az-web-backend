from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    UniqueConstraint
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class Faculty(Base):
    __tablename__ = "faculties"
    __table_args__ = (
        UniqueConstraint("faculty_code"),
    )

    id = Column(Integer, primary_key=True, index=True)
    faculty_code = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    cafedras = relationship("Cafedra", back_populates="faculty")
    translations = relationship("FacultyTranslations", back_populates="faculty", cascade="all, delete-orphan")