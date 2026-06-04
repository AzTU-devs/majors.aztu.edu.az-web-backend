from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime
)
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship


class Tlo(Base):
    __tablename__ = "Tlo"

    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String, nullable=False)
    # A TLO (topic learning outcome) belongs to a topic.
    topic_code = Column(String, nullable=False, index=True)
    tlo_code = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow())