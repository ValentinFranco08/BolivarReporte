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

class AnimalReportType(str, enum.Enum):
    PERDIDO = "perdido"
    ENCONTRADO = "encontrado"
    ALERTA_CEBO = "alerta_cebo"
    EN_TRANSITO = "en_transito"
    ADOPCION = "adopcion"

class PetType(str, enum.Enum):
    PERRO = "perro"
    GATO = "gato"
    OTRO = "otro"

class PetHealthStatus(str, enum.Enum):
    SANO = "sano"
    LASTIMADO = "lastimado"
    SINTOMAS_ENVENENAMIENTO = "sintomas_envenenamiento"
    CON_COLLAR = "con_collar"

class RemumStatus(str, enum.Enum):
    A_SALVO = "a_salvo"
    EXTRAVIADO = "extraviado"

class HealthEventType(str, enum.Enum):
    ANTIRRABICA = "antirrabica"
    CASTRACION = "castracion"
    DESPARASITACION = "desparasitacion"
    OTRO = "otro"

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
    used_for_retraining = Column(Boolean, default=False) # Marca si ya fue consumido en un ciclo de reentrenamiento
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    prediction = relationship("AIPrediction", back_populates="feedback")
    reviewer = relationship("User", back_populates="feedbacks")
