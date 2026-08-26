from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from .database import Base

class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    ADMIN = "admin"

class ReportStatus(str, enum.Enum):
    REPORTADO = "reportado"
    CLASIFICADO = "clasificado"
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    RESUELTO = "resuelto"
    RECHAZADO = "rechazado"
    DUPLICADO = "duplicado"
    REQUIERE_INFORMACION = "requiere_informacion"

class ReportPriority(str, enum.Enum):
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"
    CRITICAL = "critica"

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

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False) # ej: "bache", "animal_perdido"
    area = Column(String, nullable=False) # ej: "Infraestructura", "Animales"
    description = Column(String)
    active = Column(Boolean, default=True)
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
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="reports")
    category = relationship("Category", back_populates="reports")
    prediction = relationship("AIPrediction", back_populates="report", uselist=False)

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False) # ej: "multimodal-v1"
    version = Column(String, nullable=False)
    architecture = Column(String) # ej: "ViT + RoBERTa + Cross-Attention"
    dataset_version = Column(String) # ej: "573_synthetic"
    macro_f1 = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    predictions = relationship("AIPrediction", back_populates="model_version")

class AIPrediction(Base):
    __tablename__ = "ai_predictions"

    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), unique=True)
    model_version_id = Column(Integer, ForeignKey("model_versions.id"))
    predicted_class = Column(String, nullable=False) # nombre de la categoria predicha
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    report = relationship("Report", back_populates="prediction")
    model_version = relationship("ModelVersion", back_populates="predictions")
    feedback = relationship("Feedback", back_populates="prediction", uselist=False)

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(Integer, ForeignKey("ai_predictions.id"), unique=True)
    correct = Column(Boolean, nullable=False)
    correct_class = Column(String, nullable=True) # Si correct == False, cuál era la clase real
    reviewed_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    prediction = relationship("AIPrediction", back_populates="feedback")
    reviewer = relationship("User", back_populates="feedbacks")
