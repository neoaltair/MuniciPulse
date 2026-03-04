"""
FastAPI main application with report creation and duplicate detection
"""
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import os
import shutil
from dotenv import load_dotenv
from uuid import UUID

from database import get_db, init_db
from models import User, Report, ReportImage, StatusHistory, Comment, UserRole, ReportStatus
from schemas import (
    UserCreate, UserResponse, UserLogin, Token,
    ReportCreate, ReportResponse, ReportWithLinkInfo,
    StatusUpdate, StatusHistoryResponse,
    CommentCreate, CommentResponse
)
from auth import (
    get_password_hash, authenticate_user, create_access_token,
    get_current_user, get_current_active_citizen, get_current_municipal_officer
)
from utils import (
    haversine_distance, generate_unique_filename,
    validate_coordinates, validate_image_file
)

load_dotenv()

# Configuration
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "./uploads")
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
DUPLICATE_RADIUS_METERS = float(os.getenv("DUPLICATE_RADIUS_METERS", "10"))

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="CivicFix API",
    description="Civic reporting platform with intelligent duplicate detection",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_origin_regex="https://.*\.ngrok-free\.app",  # Explicitly allow ngrok domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploaded files
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


# ============= Startup Event =============

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("✅ Database initialized")


# ============= Health Check =============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============= Authentication Endpoints =============

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (citizen or municipal officer)"""
    
    # Check if username already exists
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Check if email already exists (if provided)
    if user_data.email:
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user



@app.post("/auth/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get JWT access token with OAuth2 scopes"""
    
    user = authenticate_user(db, user_credentials.username, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token with scopes based on user role
    access_token = create_access_token(user)
    
    return {"access_token": access_token, "token_type": "bearer"}



@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user


# ============= Report Creation with Duplicate Detection =============

@app.post("/reports", response_model=ReportWithLinkInfo, status_code=status.HTTP_201_CREATED)
async def create_report(
    title: str = Form(...),
    description: str = Form(...),
    category: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    priority: str = Form("medium"),
    images: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_active_citizen),
    db: Session = Depends(get_db)
):
    """
    Create a new civic report with images.
    
    **Duplicate Detection Logic:**
    - Checks if any existing report is within 10 meters of the new location
    - If found, links the new report to the existing one instead of creating a duplicate
    - Returns information about the linking in the response
    """
    
    # Validate coordinates
    is_valid, error_msg = validate_coordinates(latitude, longitude)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )
    
    # Validate images
    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one image is required"
        )
    
    for image in images:
        is_valid, error_msg = validate_image_file(image.filename, image.content_type)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Check file size
        image.file.seek(0, 2)  # Seek to end
        file_size = image.file.tell()
        image.file.seek(0)  # Reset to beginning
        
        if file_size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image {image.filename} exceeds {MAX_FILE_SIZE_MB}MB limit"
            )
    
    # ============= DUPLICATE DETECTION =============
    # Find all existing reports to check for duplicates
    all_reports = db.query(Report).filter(
        Report.status.in_([ReportStatus.PENDING, ReportStatus.IN_PROGRESS])
    ).all()
    
    parent_report = None
    for existing_report in all_reports:
        distance = haversine_distance(
            latitude, longitude,
            existing_report.latitude, existing_report.longitude
        )
        
        if distance <= DUPLICATE_RADIUS_METERS:
            parent_report = existing_report
            break  # Found a duplicate, link to this one
    
    # Create new report
    new_report = Report(
        citizen_id=current_user.id,
        title=title,
        description=description,
        category=category,
        latitude=latitude,
        longitude=longitude,
        priority=priority,
        parent_report_id=parent_report.id if parent_report else None
    )
    
    db.add(new_report)
    db.flush()  # Get the report ID without committing
    
    # Save images
    saved_images = []
    for idx, image in enumerate(images):
        # Generate unique filename
        unique_filename = generate_unique_filename(image.filename)
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        
        # Create database record
        image_url = f"/uploads/{unique_filename}"
        report_image = ReportImage(
            report_id=new_report.id,
            image_url=image_url,
            image_order=idx,
            file_size_bytes=file_size,
            mime_type=image.content_type
        )
        
        db.add(report_image)
        saved_images.append(report_image)
    
    # Create initial status history entry
    status_entry = StatusHistory(
        report_id=new_report.id,
        changed_by_user_id=current_user.id,
        old_status=None,
        new_status=ReportStatus.PENDING.value,
        comment="Report created"
    )
    db.add(status_entry)
    
    db.commit()
    db.refresh(new_report)
    
    # Prepare response
    response = ReportWithLinkInfo(
        **{
            "id": new_report.id,
            "citizen_id": new_report.citizen_id,
            "title": new_report.title,
            "description": new_report.description,
            "category": new_report.category,
            "latitude": new_report.latitude,
            "longitude": new_report.longitude,
            "status": new_report.status,
            "assigned_officer_id": new_report.assigned_officer_id,
            "created_at": new_report.created_at,
            "updated_at": new_report.updated_at,
            "resolved_at": new_report.resolved_at,
            "priority": new_report.priority,
            "parent_report_id": new_report.parent_report_id,
            "images": saved_images,
            "is_linked": parent_report is not None,
            "linked_to_report_id": parent_report.id if parent_report else None,
            "linked_reason": f"Found existing report within {DUPLICATE_RADIUS_METERS}m radius" if parent_report else None
        }
    )
    
    return response


# ============= Report Retrieval =============

@app.get("/reports", response_model=List[ReportResponse])
async def get_reports(
    status_filter: Optional[ReportStatus] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reports with optional filters"""
    
    query = db.query(Report)
    
    # Citizens can only see their own reports
    if current_user.role == UserRole.CITIZEN:
        query = query.filter(Report.citizen_id == current_user.id)
    
    # Apply filters
    if status_filter:
        query = query.filter(Report.status == status_filter)
    
    if category:
        query = query.filter(Report.category == category)
    
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    
    return reports


@app.get("/reports/public", response_model=List[ReportResponse])
async def get_public_reports(
    status_filter: Optional[ReportStatus] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all public reports from all users (accessible to all authenticated users)"""
    
    query = db.query(Report)
    
    # Apply filters
    if status_filter:
        query = query.filter(Report.status == status_filter)
    
    if category:
        query = query.filter(Report.category == category)
    
    reports = query.order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    
    return reports


@app.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report_by_id(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific report by ID"""
    
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Citizens can only view their own reports
    if current_user.role == UserRole.CITIZEN and report.citizen_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return report


# ============= Status Management (Municipal Officers Only) =============

@app.patch("/reports/{report_id}/status", response_model=ReportResponse)
async def update_report_status(
    report_id: UUID,
    new_status: str = Form(...),
    comment: Optional[str] = Form(None),
    resolved_image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_municipal_officer),
    db: Session = Depends(get_db)
):
    """
    Update report status (municipal officers only)
    
    When changing status to 'resolved', a resolved_image (after photo) is REQUIRED.
    Sends email notification to the citizen who reported it.
    """
    from email_service import send_report_resolved_notification, send_report_status_changed_notification
    
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Validate status value
    try:
        new_status_enum = ReportStatus(new_status.lower())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status: {new_status}. Must be one of: pending, in_progress, resolved, rejected"
        )
    
    # If resolving, require 'after' photo
    if new_status_enum == ReportStatus.RESOLVED and not resolved_image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Resolved image (after photo) is required when marking as resolved"
        )
    
    old_status = report.status
    report.status = new_status_enum
    report.updated_at = datetime.utcnow()
    
    # Handle resolved image upload
    if resolved_image:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/jpg", "image/webp"]
        if resolved_image.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Only JPEG, PNG, and WebP images are allowed"
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = "uploads/resolved"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_extension = resolved_image.filename.split(".")[-1]
        unique_filename = f"{report_id}_resolved_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            content = await resolved_image.read()
            f.write(content)
        
        # Store relative path in database
        report.resolved_image_url = f"/{file_path}"
    
    # If resolving, set resolved_at timestamp
    if new_status_enum == ReportStatus.RESOLVED:
        report.resolved_at = datetime.utcnow()
    
    # Assign officer if not already assigned
    if not report.assigned_officer_id:
        report.assigned_officer_id = current_user.id
    
    # Create status history entry
    status_entry = StatusHistory(
        report_id=report.id,
        changed_by_user_id=current_user.id,
        old_status=old_status.value,
        new_status=new_status_enum.value,
        comment=comment
    )
    db.add(status_entry)
    
    db.commit()
    db.refresh(report)
    
    # Send email notification to citizen
    try:
        citizen = db.query(User).filter(User.id == report.citizen_id).first()
        if citizen and citizen.email:
            officer_name = f"{current_user.first_name} {current_user.last_name}"
            citizen_name = f"{citizen.first_name} {citizen.last_name}"
            
            if new_status_enum == ReportStatus.RESOLVED:
                send_report_resolved_notification(
                    citizen_email=citizen.email,
                    citizen_name=citizen_name,
                    report_title=report.title,
                    report_id=str(report.id),
                    officer_name=officer_name,
                    comment=comment
                )
            else:
                send_report_status_changed_notification(
                    citizen_email=citizen.email,
                    citizen_name=citizen_name,
                    report_title=report.title,
                    new_status=new_status_enum.value,
                    officer_name=officer_name,
                    comment=comment
                )
    except Exception as e:
        # Log error but don't fail the request
        print(f"[EMAIL ERROR] Failed to send notification: {str(e)}")
    
    return report


@app.get("/reports/{report_id}/linked", response_model=List[ReportResponse])
async def get_linked_reports(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reports linked to a specific report (within 10m radius)"""
    
    report = db.query(Report).filter(Report.id == report_id).first()
    
    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    # Find all reports that have this report as their parent
    linked_reports = db.query(Report).filter(Report.parent_report_id == report_id).all()
    
    return linked_reports


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=os.getenv("DEBUG", "True").lower() == "true"
    )
