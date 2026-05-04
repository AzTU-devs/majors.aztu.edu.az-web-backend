from sqlalchemy import (
    Integer,
    String,
    UniqueConstraint,
    Column,
    DateTime,
    Boolean
)
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

class Topic(Base):
    __tablename__ = "topic"

    id = Column(Integer, primary_key=True, index=True)
    subject_code = Column(String, nullable=False)
    topic_code = Column(String, nullable=False)
    topic_url = Column(String, nullable=False)
    topic_type = Column(Integer, nullable=False)
    # 1 - muhazire
    # 2 - mesgele
    # 3 - laboratoriya
    # 4 - serbest is
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow())