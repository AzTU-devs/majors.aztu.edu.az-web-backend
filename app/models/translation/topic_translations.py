from sqlalchemy import (
    Integer,
    String,
    Column,
    DateTime
)
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship

class TopicTranslations(Base):
    __tablename__ = "topic_translations"

    id = Column(Integer, primary_key=True, index=True)
    topic_code = Column(String, nullable=False)
    topic_name = Column(String, nullable=False)
    topic_description = Column(String)
    topic_result = Column(String)
    language_code = Column(String(2), nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow())