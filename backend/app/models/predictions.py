from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..dao.database import Base


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
