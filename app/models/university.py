from sqlalchemy import (
    Integer,
    String,
    UniqueConstraint,
    Column,
    DateTime,
    Boolean
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class University(Base):
    __tablename__ = "universities"
    __table_args__ = (
        UniqueConstraint("university_code"),
        UniqueConstraint("university_name"),
        UniqueConstraint("university_short_name"),
    )

    id = Column(Integer, index=True, primary_key=True)
    university_code = Column(String, nullable=False, unique=True)
    university_name = Column(String, nullable=False, unique=True)
    university_short_name = Column(String, nullable=False, unique=True)
    is_frozen = Column(Boolean, nullable=False, default=False)
    frozen_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=True)
    deleted_at = Column(DateTime, nullable=True)