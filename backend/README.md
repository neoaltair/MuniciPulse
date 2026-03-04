# CivicFix Backend API

FastAPI-based backend service for the CivicFix civic reporting platform with intelligent duplicate detection.

## Features

✅ **Duplicate Detection**: Automatically detects reports within 10-meter radius using Haversine formula  
✅ **Image Upload**: Multi-image support with validation  
✅ **Role-Based Access**: Separate permissions for Citizens and Municipal Officers  
✅ **JWT Authentication**: Secure token-based auth  
✅ **PostgreSQL Integration**: SQLAlchemy ORM with proper relationships  
✅ **RESTful API**: Complete CRUD operations  

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Database

Install PostgreSQL and create a database:

```sql
CREATE DATABASE civicfix;
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://your_user:your_password@localhost:5432/civicfix
SECRET_KEY=your-strong-secret-key-here
```

### 4. Run the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation at `http://localhost:8000/docs`

## API Endpoints

### Authentication

- `POST /auth/register` - Register new user (citizen or municipal officer)
- `POST /auth/login` - Login and get JWT token
- `GET /auth/me` - Get current user info

### Reports

- `POST /reports` - Create new report with images (citizens only)
  - **Includes automatic duplicate detection**
  - Links to existing report if found within 10m radius
- `GET /reports` - Get all reports (filtered by role)
- `GET /reports/{report_id}` - Get specific report
- `GET /reports/{report_id}/linked` - Get all linked duplicate reports
- `PATCH /reports/{report_id}/status` - Update status (officers only)

## Duplicate Detection Logic

When a citizen submits a new report:

1. Calculate distance from new location to all existing `PENDING` and `IN_PROGRESS` reports
2. If any report is within **10 meters**, link the new report to it via `parent_report_id`
3. Return response indicating the report was linked with reason

**Example Response (Linked Report):**
```json
{
  "id": "new-report-uuid",
  "title": "Pothole on Main Street",
  "latitude": 40.7128,
  "longitude": -74.0060,
  "parent_report_id": "existing-report-uuid",
  "is_linked": true,
  "linked_to_report_id": "existing-report-uuid",
  "linked_reason": "Found existing report within 10m radius"
}
```

## Project Structure

```
backend/
├── main.py              # FastAPI application & endpoints
├── models.py            # SQLAlchemy ORM models
├── schemas.py           # Pydantic request/response schemas
├── database.py          # Database connection & session
├── auth.py              # JWT authentication & authorization
├── utils.py             # Utility functions (Haversine, validation)
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── uploads/             # Image upload directory (auto-created)
```

## Testing the Duplicate Detection

### 1. Register a Citizen

```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "citizen@example.com",
    "password": "password123",
    "role": "citizen",
    "first_name": "John",
    "last_name": "Doe"
  }'
```

### 2. Login to Get Token

```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "citizen@example.com",
    "password": "password123"
  }'
```

### 3. Create First Report

```bash
curl -X POST "http://localhost:8000/reports" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Pothole on Main St" \
  -F "description=Large pothole causing traffic issues" \
  -F "category=pothole" \
  -F "latitude=40.7128" \
  -F "longitude=-74.0060" \
  -F "priority=high" \
  -F "images=@path/to/image1.jpg"
```

### 4. Create Second Report (Within 10m)

```bash
curl -X POST "http://localhost:8000/reports" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "title=Another pothole nearby" \
  -F "description=Same pothole different angle" \
  -F "category=pothole" \
  -F "latitude=40.71281" \  # ~1 meter away
  -F "longitude=-74.00601" \
  -F "priority=high" \
  -F "images=@path/to/image2.jpg"
```

**Expected Result**: Second report will be linked to the first via `parent_report_id`

## Database Schema

See `database_schema.md` for complete database design.

Key tables:
- `users` - Citizens and municipal officers
- `reports` - Main report table with GPS coordinates
- `report_images` - Multiple images per report
- `status_history` - Audit trail of status changes
- `comments` - Communication between citizens and officers

## Security Notes

🔒 **Password Hashing**: bcrypt with salt  
🔒 **JWT Tokens**: HS256 algorithm, 30-minute expiration  
🔒 **Role-Based Access**: Decorator-based authorization  
🔒 **File Validation**: MIME type and extension checking  
🔒 **File Size Limits**: Configurable via environment variable  

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `SECRET_KEY` | JWT secret key | Required |
| `ALGORITHM` | JWT algorithm | HS256 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token validity | 30 |
| `UPLOAD_DIR` | Image upload directory | ./uploads |
| `MAX_FILE_SIZE_MB` | Max image size | 10 |
| `DUPLICATE_RADIUS_METERS` | Duplicate detection radius | 10 |
| `DEBUG` | Debug mode | True |
| `HOST` | Server host | 0.0.0.0 |
| `PORT` | Server port | 8000 |

## License

MIT
