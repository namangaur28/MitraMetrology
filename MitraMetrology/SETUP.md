# Quick Start Guide - SIH 2026 Compliance Checker

## Complete Project Structure

```
/Users/namangaur/MitraMetrology/
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.ts              # API client with all endpoints
│   │   │   └── index.ts
│   │   ├── components/
│   │   │   ├── ComplianceResults.tsx  # Compliance status display
│   │   │   ├── ImageUploader.tsx      # File upload component
│   │   │   └── index.ts
│   │   ├── contexts/
│   │   │   └── ScanContext.tsx        # Global scan state
│   │   ├── pages/
│   │   │   ├── Landing.tsx            # Home page
│   │   │   ├── Scan.tsx               # Upload page
│   │   │   ├── Results.tsx            # Results page
│   │   │   └── index.ts
│   │   ├── index.css
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── .gitignore
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes.py              # All API endpoints
│   │   │   └── __init__.py
│   │   ├── services/
│   │   │   ├── image_processor.py     # OpenCV processing
│   │   │   ├── ocr_service.py         # PaddleOCR
│   │   │   ├── field_extractor.py     # Regex + keyword extraction
│   │   │   ├── compliance_engine.py   # Rules evaluation
│   │   │   └── __init__.py
│   │   ├── rules/
│   │   │   ├── 2026/
│   │   │   │   ├── packaged_commodities_rules.json
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── models.py                  # Database models
│   │   ├── schemas.py                 # Pydantic schemas
│   │   ├── database.py                # Database setup
│   │   ├── config.py                  # Configuration
│   │   ├── main.py                    # FastAPI app
│   │   └── __init__.py
│   ├── tests/
│   │   ├── test_ocr_service.py
│   │   ├── test_field_extractor.py
│   │   ├── test_compliance_engine.py
│   │   ├── test_api.py
│   │   ├── __init__.py
│   │   └── conftest.py
│   ├── requirements.txt
│   ├── .env.example
│   ├── .gitignore
│   └── conftest.py
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── SETUP.md (this file)
```

---

## Quick Start with Docker (Recommended)

### 1. Prerequisites
- Docker and Docker Compose installed
- 8GB RAM minimum
- Internet connection (for PaddleOCR model download)

### 2. Setup Steps

```bash
# Navigate to project directory
cd /Users/namangaur/MitraMetrology

# Create environment file
cp .env.example .env

# Start all services
docker-compose up -d

# Wait for services to start (30-60 seconds)
sleep 60

# Check logs
docker-compose logs -f backend
```

### 3. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Reverse Proxy**: http://localhost

### 4. Verification

```bash
# Check all services running
docker-compose ps

# Test API health
curl http://localhost:8000/api/health

# Check database connection
docker-compose exec postgres psql -U user -d sih_compliance_db -c "SELECT 1;"
```

### 5. Stop Services

```bash
docker-compose down
```

---

## Local Development Setup

### Backend Setup

```bash
# Navigate to backend
cd /Users/namangaur/MitraMetrology/backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Setup PostgreSQL (if not using Docker)
createdb sih_compliance_db

# Run migrations (optional - tables auto-created)
# alembic upgrade head

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
# In new terminal, navigate to frontend
cd /Users/namangaur/MitraMetrology/frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# App available at http://localhost:5173
```

### Database Setup (Local PostgreSQL)

```bash
# Install PostgreSQL (macOS)
brew install postgresql

# Start service
brew services start postgresql

# Create database
createdb sih_compliance_db

# Connect to database
psql sih_compliance_db
```

---

## Running Tests

```bash
cd /Users/namangaur/MitraMetrology/backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_field_extractor.py -v

# Run with coverage
pytest --cov=app tests/

# Run tests with output
pytest -s tests/test_field_extractor.py
```

### Test Coverage

- **test_ocr_service.py** - OCR initialization and text extraction
- **test_field_extractor.py** - MRP, quantity, date, manufacturer extraction
- **test_compliance_engine.py** - Compliance rules and overall status
- **test_api.py** - API endpoints health and functionality

---

## Environment Variables

### Backend (.env in project root or backend/)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sih_compliance_db

# Environment
ENVIRONMENT=development
DEBUG=False

# API
API_HOST=0.0.0.0
API_PORT=8000

# File Upload
MAX_FILE_SIZE_MB=10
ALLOWED_IMAGE_EXTENSIONS=jpg,jpeg,png

# Image Processing
IMG_MAX_WIDTH=1920
IMG_MAX_HEIGHT=1080
IMG_QUALITY=85

# Logging
LOG_LEVEL=INFO
```

### Database Settings

For docker-compose, these are set in `.env`:

```env
DB_USER=user
DB_PASSWORD=password
DB_NAME=sih_compliance_db
```

---

## API Workflow Example

### 1. Create Scan Session
```bash
curl -X POST http://localhost:8000/api/scan
# Returns: { "scan_id": "...", "created_at": "...", "images": [], "compliance_result": null }
```

### 2. Upload Image
```bash
curl -X POST http://localhost:8000/api/upload?scan_id=YOUR_SCAN_ID \
  -F "file=@/path/to/image.jpg"
# Returns: { "scan_id": "...", "image_id": "...", "message": "Image uploaded successfully" }
```

### 3. Extract Fields
```bash
curl -X POST http://localhost:8000/api/extract?scan_id=YOUR_SCAN_ID
# Returns: { "scan_id": "...", "extracted_fields": {...} }
```

### 4. Check Compliance
```bash
curl -X POST http://localhost:8000/api/compliance/check?scan_id=YOUR_SCAN_ID
# Returns: { "overall_status": "pass|flag|needs_review", "compliance_checks": [...] }
```

### 5. Get Results
```bash
curl http://localhost:8000/api/scan/YOUR_SCAN_ID
# Returns: Complete scan with images, OCR, fields, and compliance results
```

---

## File Size and Performance

- **Max Image Size**: 10MB
- **Max Images per Scan**: 5
- **Processing Time**: 30-120 seconds per scan (depends on image quality)
- **Database**: PostgreSQL 15+
- **Memory**: 2GB minimum for backend

---

## Troubleshooting

### Docker Won't Start

```bash
# Check Docker running
docker ps

# View detailed logs
docker-compose logs backend

# Rebuild images
docker-compose build --no-cache

# Remove and restart
docker-compose down -v
docker-compose up -d
```

### Database Connection Error

```bash
# Check PostgreSQL is running
docker-compose logs postgres

# Test connection
docker-compose exec postgres psql -U user -d sih_compliance_db -c "SELECT 1;"
```

### PaddleOCR Download Fails

```bash
# Ensure internet connection
# Logs will show download progress
docker-compose logs backend | grep -i paddle

# Manually download model (inside container)
docker-compose exec backend python -c "from paddleocr import PaddleOCR; PaddleOCR()"
```

### Frontend Can't Connect to Backend

```bash
# Check CORS is enabled (it is by default)
# Check backend URL in frontend/.env or docker-compose.yml
# Check network tab in browser dev tools

# Test backend health
curl http://localhost:8000/api/health
```

---

## Building for Production

### Build Frontend

```bash
cd frontend
npm run build
# Creates dist/ folder with optimized production build
```

### Production Docker Image

```bash
# Build production image
docker build -f docker/Dockerfile.backend -t sih-backend:latest .
docker build -f docker/Dockerfile.frontend -t sih-frontend:latest .

# Push to registry (optional)
docker tag sih-backend:latest myregistry.azurecr.io/sih-backend:latest
docker push myregistry.azurecr.io/sih-backend:latest
```

### Production Environment

```env
ENVIRONMENT=production
DEBUG=False
DATABASE_URL=postgresql://produser:STRONG_PASSWORD@prod-db-host:5432/sih_compliance_db
LOG_LEVEL=WARNING
```

---

## Development Workflow

### 1. Backend Development

```bash
# Terminal 1: Backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload

# Terminal 2: Tests
cd backend
pytest --watch  # requires pytest-watch
```

### 2. Frontend Development

```bash
# Terminal 3: Frontend
cd frontend
npm run dev
```

### 3. Making Changes

- Backend: Files auto-reload with `--reload`
- Frontend: Files auto-reload via Vite
- Tests: Run with `pytest` after changes

---

## Deployment Considerations

### Security Checklist
- [ ] Set DEBUG=False
- [ ] Use strong database password
- [ ] Enable HTTPS in nginx
- [ ] Set ALLOWED_HOSTS properly
- [ ] Use environment variables for secrets
- [ ] Set up SSL certificates
- [ ] Configure CORS properly for production domain
- [ ] Implement rate limiting

### Performance Checklist
- [ ] Enable database connection pooling
- [ ] Add Redis for caching (Phase 2)
- [ ] Use CDN for static assets
- [ ] Configure nginx caching headers
- [ ] Monitor database performance
- [ ] Set up logging and monitoring

### Backup & Recovery
- [ ] Regular PostgreSQL backups
- [ ] Backup uploaded images
- [ ] Document recovery procedures
- [ ] Test backup restoration

---

## Key Features Implemented (Phase 1)

✅ Image upload and validation
✅ OCR text extraction (PaddleOCR)
✅ Field extraction (regex + keyword matching)
✅ Compliance rules engine (versioned)
✅ Rules-based compliance checking
✅ Multi-image support (up to 5)
✅ Camera capture support
✅ Database persistence (PostgreSQL)
✅ RESTful API
✅ Professional UI (Landing, Scan, Results)
✅ Comprehensive testing
✅ Docker deployment
✅ Documentation

---

## Known Limitations (Phase 1)

- ❌ No user authentication
- ❌ No batch processing
- ❌ No report history
- ❌ English language only
- ❌ No audit trail / admin dashboard
- ❌ Single instance (no scaling)
- ❌ Manual verification required for all results

---

## Support Resources

1. **README.md** - Full documentation
2. **API Documentation** - http://localhost:8000/docs (auto-generated Swagger)
3. **Test Files** - Examples of how to use each service
4. **Code Comments** - Inline documentation

---

## Next Steps (Phase 2)

- User authentication and authorization
- Scan history and batch processing
- Advanced OCR with custom models
- Multi-language support
- Admin dashboard
- Blockchain audit trail

---

**Version**: 1.0.0 (Phase 1)  
**Last Updated**: August 26, 2026  
**Status**: Ready for Deployment
