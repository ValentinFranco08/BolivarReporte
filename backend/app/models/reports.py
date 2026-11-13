from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..dao.database import Base
from .enums import AnimalReportType, PetHealthStatus, PetType, ReportPriority, ReportStatus


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # ej: "bache", "animal_perdido"
    area = Column(String, nullable=False) # ej: "Infraestructura", "Animales"
    description = Column(String)
    active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=True) # False si es una categoría candidata/sugerida por IA
    embedding_centroid = Column(Text, nullable=True) # Representación JSON de lista de 768 floats
    sample_count = Column(Integer, default=1) # Cantidad de muestras que componen el centroide
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    reports = relationship("Report", back_populates="category")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True) # Permitimos reportes anónimos inicialmente? Mejor no, pero lo dejamos nullable por si acaso.
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    address = Column(String, nullable=True)
    image_path = Column(String, nullable=False) # Path local por ahora
    status = Column(Enum(ReportStatus), default=ReportStatus.REPORTADO)
    priority = Column(Enum(ReportPriority), default=ReportPriority.MEDIUM)
    is_novel_category = Column(Boolean, default=False) # True si el reporte inauguró una problemática nueva
    embedding = Column(Text, nullable=True) # Vector multimodal / visual del reporte para matching

    # Campos especializados de Protección Animal y Alertas
    report_type = Column(Enum(AnimalReportType), default=AnimalReportType.PERDIDO, nullable=True)
    pet_type = Column(Enum(PetType), default=PetType.PERRO, nullable=True)
    pet_name = Column(String, nullable=True)
    pet_breed = Column(String, nullable=True)
    color_description = Column(String, nullable=True)
    health_status = Column(Enum(PetHealthStatus), default=PetHealthStatus.SANO, nullable=True)
    contact_name = Column(String, nullable=True)
    contact_phone = Column(String, nullable=True)
    is_resolved = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="reports")
    category = relationship("Category", back_populates="reports")
    prediction = relationship("AIPrediction", back_populates="report", uselist=False)
    additional_photos = relationship(
        "ReportPhoto", back_populates="report", cascade="all, delete-orphan", order_by="ReportPhoto.id", lazy="selectin",
    )


class ReportPhoto(Base):
    __tablename__ = "report_photos"

    id = Column(Integer, primary_key=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False)
    image_path = Column(String, nullable=False)
    embedding = Column(Text)
    __table_args__ = (UniqueConstraint("report_id", "image_path"),)

    report = relationship("Report", back_populates="additional_photos")
