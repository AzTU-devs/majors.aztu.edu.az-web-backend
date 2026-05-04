from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    ForeignKey
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class CafedraTranslations(Base):
    __tablename__ = "cafedra_translations"
    __table_args__ = {
        "extend_existing": True
    }

    id = Column(Integer, primary_key=True, index=True)
    cafedra_code = Column(String, ForeignKey("cafedras.cafedra_code", ondelete="CASCADE"), nullable=False)
    lang_code = Column(String(2), nullable=False)
    cafedra_name = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)

    cafedra = relationship("Cafedra", back_populates="translations")