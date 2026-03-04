# MuniciPulse - Civic Issue Reporting Platform

A full-stack application for citizens to report civic issues and municipal officers to manage and resolve them efficiently.

## 🌟 Features

### For Citizens
- 📝 Report civic issues with photos and GPS location
- 🗺️ Interactive map view of all reports
- 📊 Track your submitted reports
- ✉️ Email notifications when reports are resolved
- 📸 View before/after photos of resolved issues

### For Municipal Officers
- 📋 Dashboard with pending and in-progress reports
- 📍 Distance calculation from office location
- ✏️ Update report status with comments
- 📷 Upload "after" photos when resolving issues
- 📧 Automated email notifications to citizens

### Technical Features
- 🔐 OAuth2 authentication with role-based access
- 🗄️ PostgreSQL/PostGIS database
- 🐳 Docker containerization
- 🚀 FastAPI backend with Uvicorn
- ⚛️ React frontend with Nginx
- 📧 SMTP email integration

---

## 🚀 Quick Start with Docker

### Prerequisites
- Docker and Docker Compose installed
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd CivicFix

# Copy and configure environment variables
cp .env.example .env

# IMPORTANT: Edit .env and change:
# - POSTGRES_PASSWORD
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - SMTP settings (optional, for email notifications)

# Start all services
docker-compose up --build -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432

---

## 📋 Manual Setup (Without Docker)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your database credentials

# Initialize database
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# Create initial admin user (optional)
python seed_database.py

# Run server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Edit REACT_APP_API_URL if needed

# Start development server
npm start

# Or build for production
npm run build
npm install -g serve
serve -s build -p 3000
```

---

## 📁 Project Structure

```
CivicFix/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Database models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication logic
│   ├── database.py          # Database connection
│   ├── email_service.py     # Email notifications
│   ├── utils.py             # Utility functions
│   ├── requirements.txt     # Python dependencies
│   ├── Dockerfile          # Backend container
│   └── alembic/            # Database migrations
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/      # Reusable components
│   │   ├── pages/           # Page components
│   │   ├── utils/           # Utility functions
│   │   ├── App.jsx          # Main application
│   │   └── index.js         # Entry point
│   ├── package.json         # Node dependencies
│   ├── Dockerfile          # Frontend container
│   └── nginx.conf          # Nginx configuration
│
├── docker-compose.yml      # Docker orchestration
├── .env.example           # Environment template
└── README.md              # This file
```

---

## 🔧 Configuration

### Environment Variables

**Backend (.env in root):**
```bash
# Database
POSTGRES_DB=civicfix
POSTGRES_USER=civicfix_user
POSTGRES_PASSWORD=your-secure-password

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

**Frontend (.env in frontend/):**
```bash
REACT_APP_API_URL=http://localhost:8000
```

---

## 📊 Database Schema

- **users** - Citizens and municipal officers
- **reports** - Civic issue reports
- **report_images** - Photos uploaded with reports
- **status_history** - Audit trail of status changes
- **comments** - Comments on reports
- **categories** - Issue categories

---

## 🔐 Authentication

The application uses OAuth2 password flow with:
- **Scopes**: `citizen` and `officer`
- **JWT tokens** with configurable expiration
- **Role-based access control**

### Default Roles
- **Citizen**: Can create and view own reports
- **Municipal Officer**: Can view and update all reports

---

## 📧 Email Notifications

Configure SMTP settings in `.env` to enable:
- Status change notifications
- Special HTML template for resolved reports
- Includes officer comments and links to dashboard

**Gmail Setup:**
1. Enable 2-factor authentication
2. Generate App Password
3. Use App Password in `SMTP_PASSWORD`

---

## 🐳 Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild services
docker-compose up --build -d

# Database backup
docker-compose exec db pg_dump -U civicfix_user civicfix > backup.sql

# Access backend shell
docker-compose exec backend bash

# Run migrations
docker-compose exec backend alembic upgrade head
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e
```

---

## 📝 API Documentation

Interactive API documentation available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

**Authentication:**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login and get token
- `GET /auth/me` - Get current user

**Reports:**
- `POST /reports` - Create new report
- `GET /reports` - List all reports
- `GET /reports/{id}` - Get report details
- `PATCH /reports/{id}/status` - Update status (officers only)

---

## 🚀 Deployment

### Production Checklist

1. **Environment Variables**
   - Generate secure `SECRET_KEY`: `openssl rand -hex 32`
   - Use strong database password
   - Configure SMTP for email notifications
   - Set `ENVIRONMENT=production`

2. **Security**
   - Update CORS origins in `main.py`
   - Enable HTTPS with reverse proxy
   - Use SSL for database connections

3. **Database**
   - Regular backups
   - Enable connection pooling
   - Monitor query performance

4. **Monitoring**
   - Set up logging aggregation
   - Configure health checks
   - Monitor resource usage

See [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) for detailed deployment instructions.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🆘 Support

For issues or questions:
1. Check the [troubleshooting guide](DOCKER_DEPLOYMENT.md#troubleshooting)
2. Review API documentation
3. Check Docker logs

---

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Real-time notifications (WebSockets)
- [ ] Analytics dashboard
- [ ] Bulk report imports
- [ ] Multi-language support
- [ ] Integration with municipal systems

---

