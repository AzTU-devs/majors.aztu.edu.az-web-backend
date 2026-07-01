from sqlalchemy import Column, String, Integer, DateTime, UniqueConstraint
from app.db.database import Base


class CloPloMatch(Base):
    __tablename__ = "clo_plo_match"
    __table_args__ = (UniqueConstraint("clo_code", "plo_code"),)

    id = Column(Integer, primary_key=True, index=True)
    clo_code = Column(String, nullable=False, index=True)
    plo_code = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
