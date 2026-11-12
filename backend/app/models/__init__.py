"""Entidades registradas en SQLAlchemy y enumeraciones del modelo."""

from .enums import UserRole, ReportStatus, ReportPriority, AnimalReportType, PetType, PetHealthStatus, RemumStatus, HealthEventType
from .users import User
from .remum import RemumRecord, RemumHealthEvent, RemumGodparent
from .reports import Category, Report
from .predictions import ModelVersion, AIPrediction, Feedback

__all__ = [
    "UserRole",
    "ReportStatus",
    "ReportPriority",
    "AnimalReportType",
    "PetType",
    "PetHealthStatus",
    "RemumStatus",
    "HealthEventType",
    "User",
    "RemumRecord",
    "RemumHealthEvent",
    "RemumGodparent",
    "Category",
    "Report",
    "ModelVersion",
    "AIPrediction",
    "Feedback",
]
