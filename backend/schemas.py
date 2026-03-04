"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID

from models import UserRole, ReportStatus, Priority


# ============= User Schemas =============

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    role: UserRole
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone_number: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============= Report Schemas =============

class ReportImageResponse(BaseModel):
    id: UUID
    image_url: str
    image_order: int
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class ReportBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=200)
    description: str = Field(..., min_length=5)
    category: str = Field(..., min_length=1, max_length=50)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    priority: Optional[Priority] = Priority.MEDIUM


class ReportCreate(ReportBase):
    """Schema for creating a new report (without images initially)"""
    pass


class ReportResponse(ReportBase):
    id: UUID
    citizen_id: UUID
    status: ReportStatus
    assigned_officer_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_image_url: Optional[str] = None
    parent_report_id: Optional[UUID] = None
    images: List[ReportImageResponse] = []
    
    class Config:
        from_attributes = True


class ReportWithLinkInfo(ReportResponse):
    """Extended response when a report is linked to an existing one"""
    is_linked: bool = False
    linked_to_report_id: Optional[UUID] = None
    linked_reason: Optional[str] = None


# ============= Status Update Schemas =============

class StatusUpdate(BaseModel):
    new_status: ReportStatus
    comment: Optional[str] = None


class StatusHistoryResponse(BaseModel):
    id: UUID
    old_status: Optional[str]
    new_status: str
    comment: Optional[str]
    changed_at: datetime
    changed_by_user_id: UUID
    
    class Config:
        from_attributes = True


# ============= Comment Schemas =============

class CommentCreate(BaseModel):
    comment_text: str = Field(..., min_length=1)
    is_internal: bool = False


class CommentResponse(BaseModel):
    id: UUID
    user_id: UUID
    comment_text: str
    created_at: datetime
    is_internal: bool
    
    class Config:
        from_attributes = True


# ============= Authentication Schemas =============

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[UUID] = None
    scopes: List[str] = []
