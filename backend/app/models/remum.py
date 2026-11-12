from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..dao.database import Base
from .enums import HealthEventType, PetType, RemumStatus


class RemumRecord(Base):
    __tablename__ = "remum_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_name = Column(String, nullable=False)
    pet_type = Column(Enum(PetType), default=PetType.PERRO)
    pet_breed = Column(String, nullable=True)
    color_description = Column(String, nullable=True)
    image_path = Column(String, nullable=True)
    chip_number = Column(String, nullable=True)
    qr_code_id = Column(String, unique=True, index=True, nullable=False)
    is_community_pet = Column(Boolean, default=False)
    status = Column(Enum(RemumStatus), default=RemumStatus.A_SALVO)
    address = Column(String, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="remum_records")
    health_events = relationship("RemumHealthEvent", back_populates="remum_record", cascade="all, delete-orphan")
    godparents = relationship("RemumGodparent", back_populates="remum_record", cascade="all, delete-orphan")


class RemumHealthEvent(Base):
    __tablename__ = "remum_health_events"

    id = Column(Integer, primary_key=True, index=True)
    remum_record_id = Column(Integer, ForeignKey("remum_records.id"), nullable=False)
    event_type = Column(Enum(HealthEventType), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    certificate_number = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    remum_record = relationship("RemumRecord", back_populates="health_events")


class RemumGodparent(Base):
    __tablename__ = "remum_godparents"

    id = Column(Integer, primary_key=True, index=True)
    remum_record_id = Column(Integer, ForeignKey("remum_records.id"), nullable=False)
    name = Column(String, nullable=False)
    task = Column(String, nullable=False)

    remum_record = relationship("RemumRecord", back_populates="godparents")
