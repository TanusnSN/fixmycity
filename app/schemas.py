from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import Category, Priority, Role, Status


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=60)
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
    password: str = Field(min_length=6, max_length=72)


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    role: Role


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PhotoRead(BaseModel):
    id: int
    url: str


class StatusHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    old_status: Optional[Status] = None
    new_status: Status
    remarks: Optional[str] = None
    changed_at: datetime


class ComplaintRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: Category
    lat: float
    lng: float
    address: Optional[str] = None
    status: Status
    priority: Priority
    department_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    supporters_count: int = 0


class ComplaintDetail(ComplaintRead):
    photos: list[PhotoRead] = []
    timeline: list[StatusHistoryRead] = []


class PublicComplaint(BaseModel):
    """Safe for the public map: no citizen identity, no full description."""

    id: int
    title: str
    category: Category
    lat: float
    lng: float
    status: Status
    priority: Priority
    created_at: datetime
    supporters_count: int = 0


class ReopenRequest(BaseModel):
    reason: str = Field(min_length=5, max_length=500)


class DepartmentCreate(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: Optional[str] = Field(None, max_length=255)


class DepartmentRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None


class AdminComplaintUpdate(BaseModel):
    status: Optional[Status] = None
    category: Optional[Category] = None
    priority: Optional[Priority] = None
    department_id: Optional[int] = None
    remarks: Optional[str] = Field(None, max_length=500)
    auto_priority: Optional[bool] = None


class AdminComplaintRead(ComplaintRead):
    citizen_name: Optional[str] = None
    department_name: Optional[str] = None
    master_complaint_id: Optional[int] = None
    duplicates_count: int = 0
    is_overdue: bool = False
    priority_score: float = 0.0
    priority_manual: bool = False


class MergeRequest(BaseModel):
    master_id: int
    remarks: Optional[str] = Field(None, max_length=300)


class DuplicateCheckRequest(BaseModel):
    category: Category
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    title: str = Field(min_length=3, max_length=120)
    description: str = Field(min_length=3, max_length=2000)


class SimilarComplaint(BaseModel):
    id: int
    title: str
    status: Status
    distance_m: float
    text_similarity: float
    confidence: float
    level: str
    supporters_count: int = 0
