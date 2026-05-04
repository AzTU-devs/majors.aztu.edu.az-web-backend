from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime
)
from datetime import datetime
from app.db.database import Base
from sqlalchemy.orm import relationship


class TloTranslations(Base):
    __tablename__ = "tlo_translations"

    id = Column(Integer, primary_key=True, index=True)
    tlo_code = Column(String, nullable=False)
    language_code = Column(String(2), nullable=False)
    tlo_content = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.utcnow())