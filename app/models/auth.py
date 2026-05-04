from sqlalchemy import (
    Integer,
    String,
    Column,
    UniqueConstraint,
    Boolean,
    DateTime,
    ForeignKey
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class Auth(Base):
    __tablename__ = "auth"
    __table_args__= (
        UniqueConstraint("fin_kod"),
    )

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    role = Column(Integer, nullable=False)
    # 1 - admin / dev
    # 2 - kafedra mudiri
    approved = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    otp = relationship("Otp", back_populates="auth", uselist=False)
    user = relationship("User", back_populates="auth_user", uselist=False)