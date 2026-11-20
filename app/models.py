from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import NaiveDatetime
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    """Current UTC time, stored without a timezone."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Role(str, Enum):
    CITIZEN = "CITIZEN"
    ADMIN = "ADMIN"


class Category(str, Enum):
    ROAD = "ROAD"
    STREETLIGHT = "STREETLIGHT"
    WATER_LEAKAGE = "WATER_LEAKAGE"
    DRAINAGE = "DRAINAGE"
    OTHER = "OTHER"


class Status(str, Enum):
    SUBMITTED = "SUBMITTED"
    VERIFIED = "VERIFIED"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    REJECTED = "REJECTED"
    REOPENED = "REOPENED"
    WITHDRAWN = "WITHDRAWN"


class Priority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Department(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    hashed_password: str
    role: Role = Role.CITIZEN
    is_verified: bool = False
    phone: Optional[str] = Field(default=None, unique=True, index=True)
    is_blocked: bool = False
    blocked_reason: Optional[str] = None
    department_id: Optional[int] = Field(default=None, foreign_key="department.id")
    created_at: NaiveDatetime = Field(default_factory=utcnow)


class Complaint(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    category: Category
    lat: float
    lng: float
    address: Optional[str] = None
    status: Status = Status.SUBMITTED
    priority: Priority = Priority.LOW
    priority_score: float = 0.0
    priority_manual: bool = False
    citizen_id: int = Field(foreign_key="user.id", index=True)
    department_id: Optional[int] = Field(default=None, foreign_key="department.id")
    # If this complaint is a duplicate, it points to the "master" complaint
    master_complaint_id: Optional[int] = Field(default=None, foreign_key="complaint.id")
    created_at: NaiveDatetime = Field(default_factory=utcnow)
    updated_at: NaiveDatetime = Field(default_factory=utcnow)
    resolved_at: Optional[NaiveDatetime] = None


class ComplaintPhoto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    complaint_id: int = Field(foreign_key="complaint.id", index=True)
    file_path: str
    uploaded_at: NaiveDatetime = Field(default_factory=utcnow)


class StatusHistory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    complaint_id: int = Field(foreign_key="complaint.id", index=True)
    old_status: Optional[Status] = None
    new_status: Status
    remarks: Optional[str] = None
    changed_by: int = Field(foreign_key="user.id")
    changed_at: NaiveDatetime = Field(default_factory=utcnow)


class Supporter(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    complaint_id: int = Field(foreign_key="complaint.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    created_at: NaiveDatetime = Field(default_factory=utcnow)


class AuditLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id")
    action: str
    entity: str
    entity_id: Optional[int] = None
    details: Optional[str] = None
    created_at: NaiveDatetime = Field(default_factory=utcnow)

class EmailCode(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    purpose: str  # "verify" or "reset"
    code_hash: str
    expires_at: NaiveDatetime
    attempts: int = 0
    created_at: NaiveDatetime = Field(default_factory=utcnow)

class Notification(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    complaint_id: Optional[int] = Field(default=None, foreign_key="complaint.id")
    message: str
    is_read: bool = False
    created_at: NaiveDatetime = Field(default_factory=utcnow)