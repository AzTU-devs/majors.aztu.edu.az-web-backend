from sqlalchemy import Column, String, Integer, DateTime, UniqueConstraint
from app.db.database import Base


class SubjectCompetencyMatch(Base):
    __tablename__ = "subject_competency_match"
    __table_args__ = (UniqueConstraint("subject_code", "competency_code"),)

    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String, nullable=False, index=True)
    competency_code = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
