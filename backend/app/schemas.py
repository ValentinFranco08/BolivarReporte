from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import ReportStatus, ReportPriority, UserRole

# --- Categorías ---
class CategoryBase(BaseModel):
    name: str
    area: str
    description: Optional[str] = None
    active: bool = True

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# --- Usuarios ---
class UserBase(BaseModel):
    name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Predicciones de IA ---
class AIPredictionBase(BaseModel):
    predicted_class: str
    confidence: float
    model_version_id: int

class AIPredictionResponse(AIPredictionBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

# --- Reportes ---
class ReportBase(BaseModel):
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None

class ReportCreate(ReportBase):
    category_id: Optional[int] = None
    # image_path se genera en el backend, no viene en el schema

class ReportSubmission(ReportCreate):
    predicted_class: str
    confidence: float
    image_path: str
    corrected_class: Optional[str] = None

class ReportResponse(ReportBase):
    id: int
    user_id: Optional[int]
    category_id: Optional[int]
    image_path: str
    status: ReportStatus
    priority: ReportPriority
    created_at: datetime
    updated_at: Optional[datetime]
    
    category: Optional[CategoryResponse] = None
    prediction: Optional[AIPredictionResponse] = None
    # user: Optional[UserResponse] = None # Omitimos detalles del usuario por privacidad

    class Config:
        orm_mode = True
        from_attributes = True

class ReportUpdateStatus(BaseModel):
    status: ReportStatus
    priority: Optional[ReportPriority] = None

# --- Feedback ---
class FeedbackCreate(BaseModel):
    correct: bool
    correct_class: Optional[str] = None  # Requerido si correct=False

class FeedbackResponse(BaseModel):
    id: int
    prediction_id: int
    correct: bool
    correct_class: Optional[str]
    reviewed_by: int
    created_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True
