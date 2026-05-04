from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class FacultyTranslations(Base):
    __tablename__ = "faculty_translations"
    __table_args__ = (
        UniqueConstraint("faculty_name"),
    )

    id = Column(Integer, primary_key=True, index=True)
    faculty_code = Column(String, ForeignKey("faculties.faculty_code", ondelete="CASCADE"), nullable=False)
    lang_code = Column(String(2), nullable=False)
    faculty_name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    faculty = relationship("Faculty", back_populates="translations")