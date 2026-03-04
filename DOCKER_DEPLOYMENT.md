# CivicFix Docker Deployment Guide

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to project directory
cd CivicFix

# Copy environment file and configure
cp .env.example .env

# Edit .env with your settings
nano .env  # or use your preferred editor
```

### 2. Configure Environment Variables

**Required Changes in `.env`:**

```bash
# Change these for production!
POSTGRES_PASSWORD=your-secure-password-here
SECRET_KEY=generate-with-openssl-rand-hex-32

# Optional: Configure email
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 3. Build and Run

```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Check service status
docker-compose ps
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Database**: localhost:5432

---

## Services

### 🐘 PostgreSQL Database (with PostGIS)
- **Image**: postgis/postgis:15-3.3
- **Port**: 5432 (configurable)
- **Volume**: Persistent data storage
- **Health Check**: Automatic readiness check

### 🚀 FastAPI Backend
- **Runtime**: Python 3.11 + Uvicorn
- **Port**: 8000 (configurable)
- **Auto-migrations**: Runs Alembic on startup
- **Hot Reload**: Enabled in development

### ⚛️ React Frontend
- **Build**: Node.js 18
- **Server**: Nginx (Alpine)
- **Port**: 80 (mapped to 3000 on host)
- **Optimized**: Multi-stage build

---

## Environment Variables

### Database
```bash
POSTGRES_DB=civicfix
POSTGRES_USER=civicfix_user
POSTGRES_PASSWORD=changeme123
POSTGRES_PORT=5432
```

### Backend
```bash
BACKEND_PORT=8000
SECRET_KEY=your-secret-key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Email (Optional)
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
FROM_EMAIL=noreply@civicfix.local
```

### Frontend
```bash
FRONTEND_PORT=3000
FRONTEND_URL=http://localhost:3000
REACT_APP_API_URL=http://localhost:8000
```

---

## Docker Commands

### Start Services
```bash
# Start all services
docker-compose up -d

# Start specific service
docker-compose up -d backend

# View logs
docker-compose logs -f backend
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes (CAUTION: deletes database)
docker-compose down -v
```

### Rebuild Services
```bash
# Rebuild all
docker-compose up --build -d

# Rebuild specific service
docker-compose up --build -d frontend
```

### Database Operations
```bash
# Access PostgreSQL shell
docker-compose exec db psql -U civicfix_user -d civicfix

# Run database backup
docker-compose exec db pg_dump -U civicfix_user civicfix > backup.sql

# Restore database
docker-compose exec -T db psql -U civicfix_user civicfix < backup.sql
```

### Backend Operations
```bash
# Run migrations manually
docker-compose exec backend alembic upgrade head

# Create new migration
docker-compose exec backend alembic revision --autogenerate -m "description"

# Access backend shell
docker-compose exec backend /bin/bash
```

---

## Production Deployment

### 1. Security Hardening

**Update `.env` for production:**
```bash
# Generate secure secret key
SECRET_KEY=$(openssl rand -hex 32)

# Use strong database password
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# Set production environment
ENVIRONMENT=production

# Update frontend URL
FRONTEND_URL=https://yourdomain.com
REACT_APP_API_URL=https://api.yourdomain.com
```

### 2. Use Production Compose File

Create `docker-compose.prod.yml`:
```yaml
version: '3.8'

services:
  backend:
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
    environment:
      ENVIRONMENT: production
```

Run with:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 3. Add Reverse Proxy (Nginx)

```nginx
# /etc/nginx/sites-available/civicfix
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 4. Enable SSL with Let's Encrypt

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Generate certificate
certbot --nginx -d yourdomain.com
```

---

## Troubleshooting

### Database Connection Issues
```bash
# Check database is running
docker-compose ps db

# View database logs
docker-compose logs db

# Test connection
docker-compose exec backend ping db
```

### Backend Not Starting
```bash
# Check logs
docker-compose logs backend

# Common issues:
# 1. Database not ready → Wait for health check
# 2. Migration failed → Check Alembic logs
# 3. Port conflict → Change BACKEND_PORT in .env
```

### Frontend Build Failures
```bash
# Rebuild with no cache
docker-compose build --no-cache frontend

# Check Node version compatibility
# Ensure package.json is correct
```

### Volume Permissions
```bash
# Fix upload directory permissions
chmod -R 777 backend/uploads

# Or run with specific user
docker-compose exec -u root backend chown -R 1000:1000 /app/uploads
```

---

## Development Workflow

### Hot Reload
Both services support hot reload:
- **Backend**: Mount source as volume (already configured)
- **Frontend**: Run `npm start` locally instead of Docker

### Local Development Setup
```yaml
# docker-compose.override.yml (auto-loaded)
version: '3.8'

services:
  backend:
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    # Use local npm server instead
    command: npm start
    environment:
      - CHOKIDAR_USEPOLLING=true
```

---

## Monitoring

### Check Resource Usage
```bash
# View resource usage
docker stats

# View specific service
docker stats civicfix-backend
```

### Health Checks
```bash
# Database health
docker-compose exec db pg_isready -U civicfix_user

# Backend health
curl http://localhost:8000/health

# Frontend health
curl http://localhost:3000
```

---

## Maintenance

### Update Services
```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up --build -d
```

### Clean Up
```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Full cleanup
docker system prune -a --volumes
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│         Docker Compose Network          │
│                                         │
│  ┌──────────┐  ┌──────────┐  ┌───────┐ │
│  │PostgreSQL│  │ FastAPI  │  │ React │ │
│  │PostGIS   │←→│ Uvicorn  │←→│ Nginx │ │
│  │  :5432   │  │  :8000   │  │  :80  │ │
│  └──────────┘  └──────────┘  └───────┘ │
│       ↓              ↓           ↓      │
│  [Volume]       [Volume]     [Static]  │
└─────────────────────────────────────────┘
         ↓              ↓           ↓
    localhost:5432  localhost:8000  localhost:3000
```

---

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Verify `.env` configuration
3. Ensure ports are not in use
4. Review service health checks
