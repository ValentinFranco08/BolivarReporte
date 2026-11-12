from sqlalchemy import Column, DateTime, Enum, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..dao.database import Base
from .enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.CITIZEN)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    reports = relationship("Report", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="reviewer")
    remum_records = relationship("RemumRecord", back_populates="user")
