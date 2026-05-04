from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    DateTime,
    ForeignKey
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class Otp(Base):
    __tablename__ = "otp"
    __table_args__= (
        UniqueConstraint("fin_kod"),
    )

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), ForeignKey("auth.fin_kod"), nullable=False, unique=True)
    otp = Column(String(255), nullable=False)
    otp_expires_at = Column(DateTime, nullable=False)

    auth = relationship("Auth", back_populates="otp")