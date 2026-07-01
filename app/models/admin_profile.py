from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from app.db.database import Base


class AdminProfile(Base):
    """Profile details for an admin/dev account (auth.role == 1)."""

    __tablename__ = "admin_profile"
    __table_args__ = (
        UniqueConstraint("fin_kod"),
        UniqueConstraint("email"),
    )

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), ForeignKey("auth.fin_kod"), nullable=False, unique=True)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)
