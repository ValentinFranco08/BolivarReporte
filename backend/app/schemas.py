from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from .models import ReportStatus, ReportPriority, UserRole, AnimalReportType, PetType, PetHealthStatus, RemumStatus, HealthEventType

# --- Categorías ---
class CategoryBase(BaseModel):
    name: str
    area: str
    description: Optional[str] = None
    active: bool = True
    is_verified: bool = True
    sample_count: int = 1

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class CategoryCreate(BaseModel):
    name: str
    area: str
    description: Optional[str] = None
    is_verified: bool = False

class CategoryApproveRequest(BaseModel):
    name: Optional[str] = None
    area: Optional[str] = None
    description: Optional[str] = None

class CategoryMergeRequest(BaseModel):
    source_category_id: int
    target_category_id: Optional[int] = None
    target_category_name: Optional[str] = None

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
    is_novel_category: Optional[bool] = False
    similarity_score: Optional[float] = None

class AIPredictionResponse(AIPredictionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# --- Reportes ---
class ReportBase(BaseModel):
    description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    address: Optional[str] = None
    report_type: Optional[AnimalReportType] = AnimalReportType.PERDIDO
    pet_type: Optional[PetType] = PetType.PERRO
    pet_name: Optional[str] = None
    pet_breed: Optional[str] = None
    color_description: Optional[str] = None
    health_status: Optional[PetHealthStatus] = PetHealthStatus.SANO
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    is_resolved: Optional[bool] = False

class ReportCreate(ReportBase):
    category_id: Optional[int] = None
    # image_path se genera en el backend, no viene en el schema

class ReportSubmission(ReportCreate):
    predicted_class: Optional[str] = "animal_perdido"
    confidence: Optional[float] = 1.0
    image_path: str
    corrected_class: Optional[str] = None
    is_novel_category: Optional[bool] = False
    suggested_area: Optional[str] = None
    embedding: Optional[List[float]] = None

class ReportResponse(ReportBase):
    id: int
    user_id: Optional[int] = None
    category_id: Optional[int] = None
    image_path: str
    status: ReportStatus
    priority: ReportPriority
    is_novel_category: bool = False
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    category: Optional[CategoryResponse] = None
    prediction: Optional[AIPredictionResponse] = None
    # user: Optional[UserResponse] = None # Omitimos detalles del usuario por privacidad

    class Config:
        from_attributes = True

class PetMatchCandidate(BaseModel):
    report: ReportResponse
    visual_similarity: float
    distance_km: float
    combined_score: float

class PetMatchResponse(BaseModel):
    matches: List[PetMatchCandidate]
    total_checked: int

class ReportUpdateStatus(BaseModel):
    status: ReportStatus
    priority: Optional[ReportPriority] = None
    is_resolved: Optional[bool] = None

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
        from_attributes = True

# --- REMUM ---
class HealthEventBase(BaseModel):
    event_type: HealthEventType
    date: datetime
    expiration_date: Optional[datetime] = None
    certificate_number: Optional[str] = None
    notes: Optional[str] = None

class HealthEventCreate(HealthEventBase):
    pass

class HealthEventResponse(HealthEventBase):
    id: int
    remum_record_id: int

    class Config:
        from_attributes = True

class GodparentBase(BaseModel):
    name: str
    task: str

class GodparentCreate(GodparentBase):
    pass

class GodparentResponse(GodparentBase):
    id: int
    remum_record_id: int

    class Config:
        from_attributes = True

class RemumBase(BaseModel):
    pet_name: str
    pet_type: Optional[PetType] = PetType.PERRO
    pet_breed: Optional[str] = None
    color_description: Optional[str] = None
    chip_number: Optional[str] = None
    is_community_pet: Optional[bool] = False
    address: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class RemumCreate(RemumBase):
    pass

class RemumResponse(RemumBase):
    id: int
    user_id: int
    image_path: Optional[str] = None
    qr_code_id: str
    status: RemumStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    health_events: List[HealthEventResponse] = []
    godparents: List[GodparentResponse] = []

    class Config:
        from_attributes = True
