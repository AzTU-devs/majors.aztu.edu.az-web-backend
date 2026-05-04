from sqlalchemy import (
    Column,
    Integer,
    String,
    UniqueConstraint,
    ForeignKey,
    DateTime
)
from app.db.database import Base
from sqlalchemy.orm import relationship

class User (Base):
    __tablename__ = "user"
    __table_args__ =(
        UniqueConstraint("fin_kod"),
        UniqueConstraint("email"),
    ) 

    id = Column(Integer, primary_key=True, index=True)
    fin_kod = Column(String(7), ForeignKey("auth.fin_kod"), nullable=False)
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    father_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    cafedra_code = Column(String, ForeignKey("cafedras.cafedra_code"), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime)

    auth_user = relationship("Auth", back_populates="user")
    cafedra = relationship("Cafedra", back_populates="user", uselist=False)