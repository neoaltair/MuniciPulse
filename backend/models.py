"""
SQLAlchemy ORM models for CivicFix database
"""
from sqlalchemy import Column, String, Text, Integer, Float, DateTime, Boolean, ForeignKey, Enum, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from database import Base


class UserRole(str, enum.Enum):
    CITIZEN = "citizen"
    MUNICIPAL_OFFICER = "municipal_officer"


class ReportStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False, index=True)  # New primary login field
    email = Column(String(255), nullable=True, index=True)  # Optional, for notifications only
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone_number = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    submitted_reports = relationship("Report", back_populates="citizen", foreign_keys="Report.citizen_id")
    assigned_reports = relationship("Report", back_populates="assigned_officer", foreign_keys="Report.assigned_officer_id")
    comments = relationship("Comment", back_populates="user")
    status_changes = relationship("StatusHistory", back_populates="changed_by_user")



class Report(Base):
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    citizen_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    
    # GPS Coordinates
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    
    # Status tracking
    status = Column(Enum(ReportStatus), nullable=False, default=ReportStatus.PENDING, index=True)
    
    # Officer assignment
    assigned_officer_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime)
    
    # Priority
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    
    # Resolved image ('after' photo uploaded by officer when marking as resolved)
    resolved_image_url = Column(String(500))
    
    # Duplicate linking - if this report is linked to another
    parent_report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="SET NULL"))
    
    # Relationships
    citizen = relationship("User", back_populates="submitted_reports", foreign_keys=[citizen_id])
    assigned_officer = relationship("User", back_populates="assigned_reports", foreign_keys=[assigned_officer_id])
    images = relationship("ReportImage", back_populates="report", cascade="all, delete-orphan")
    status_history = relationship("StatusHistory", back_populates="report", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="report", cascade="all, delete-orphan")
    
    # Self-referential relationship for linked reports
    parent_report = relationship("Report", remote_side=[id], foreign_keys=[parent_report_id])
    
    # Constraints
    __table_args__ = (
        CheckConstraint('latitude >= -90 AND latitude <= 90', name='check_latitude'),
        CheckConstraint('longitude >= -180 AND longitude <= 180', name='check_longitude'),
    )


class ReportImage(Base):
    __tablename__ = "report_images"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    image_url = Column(String(500), nullable=False)
    image_order = Column(Integer, nullable=False, default=0)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    file_size_bytes = Column(Integer)
    mime_type = Column(String(50))
    
    # Relationship
    report = relationship("Report", back_populates="images")


class StatusHistory(Base):
    __tablename__ = "status_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    changed_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    old_status = Column(String(20))
    new_status = Column(String(20), nullable=False)
    comment = Column(Text)
    changed_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    report = relationship("Report", back_populates="status_history")
    changed_by_user = relationship("User", back_populates="status_changes")


class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=False)
    comment_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_internal = Column(Boolean, default=False)
    
    # Relationships
    report = relationship("Report", back_populates="comments")
    user = relationship("User", back_populates="comments")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    icon_name = Column(String(50))
    color_hex = Column(String(7))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
