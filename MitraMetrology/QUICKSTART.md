# Quick Start Guide - Run SIH 2026 Compliance Checker

## 🚀 Option 1: Docker (Recommended - Fastest)

### Prerequisites
- Docker and Docker Compose installed
- 8GB RAM available
- Internet connection

### Steps

```bash
# 1. Navigate to project
cd /Users/namangaur/MitraMetrology

# 2. Copy environment file
cp .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Wait for services to start (30-60 seconds)
sleep 45

# 5. Verify services are running
docker-compose ps
# Should see: postgres, backend, frontend, nginx - all "Up"

# 6. Access application
# Frontend:  http://localhost:3000
# API:       http://localhost:8000
# API Docs:  http://localhost:8000/docs
```

### Verify Everything Works

```bash
# Test backend health
curl http://localhost:8000/api/health
# Expected: {"status": "healthy", "timestamp": "..."}

# Test frontend loads
curl http://localhost:3000
# Expected: HTML response

# View logs if something fails
docker-compose logs backend    # Backend logs
docker-compose logs frontend   # Frontend logs
docker-compose logs postgres   # Database logs
```

### Stop Everything

```bash
docker-compose down
# Remove volumes too (clean database):
docker-compose down -v
```

---

## 💻 Option 2: Local Development (Detailed Setup)

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Git

### Backend Setup

```bash
# 1. Navigate to backend
cd /Users/namangaur/MitraMetrology/backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file
cp .env.example .env

# 5. Edit .env (optional, defaults work for local dev)
# DATABASE_URL=postgresql://user:password@localhost:5432/sih_compliance_db

# 6. Start backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected output: "Uvicorn running on http://0.0.0.0:8000"
```

### PostgreSQL Setup (macOS)

```bash
# Install PostgreSQL
brew install postgresql@15

# Start PostgreSQL service
brew services start postgresql@15

# Create database
createdb sih_compliance_db

# Verify connection
psql sih_compliance_db -c "SELECT 1;"
# Expected: 1 row with value "1"
```

### Frontend Setup (New Terminal)

```bash
# 1. Navigate to frontend
cd /Users/namangaur/MitraMetrology/frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev

# Expected: "Local: http://localhost:5173"
```

### Access Application

- Frontend: http://localhost:5173
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 🧪 Running Tests

### Backend Tests

```bash
# Navigate to backend
cd /Users/namangaur/MitraMetrology/backend

# Activate venv
source venv/bin/activate

# Run all tests
pytest

# Run specific test file
pytest tests/test_phase2_services.py -v

# Run with coverage
pytest --cov=app tests/

# Run specific test class
pytest tests/test_phase2_services.py::TestTextNormalizer -v

# Run specific test
pytest tests/test_phase2_services.py::TestTextNormalizer::test_price_normalization_rupee_symbol -v
```

### Expected Test Output

```
collected 30+ items

tests/test_ocr_service.py ....                    [  5%]
tests/test_field_extractor.py ..........          [ 35%]
tests/test_compliance_engine.py ........          [ 60%]
tests/test_api.py ..........                      [ 85%]
tests/test_phase2_services.py ....................[ 100%]

========================== 30+ passed in 2.34s ==========================
```

---

## 🔍 Test the API Manually

### Create a Scan Session

```bash
curl -X POST http://localhost:8000/api/scan
```

**Response:**
```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2026-08-26T13:21:00",
  "images": [],
  "compliance_result": null
}
```

### View API Documentation

Open browser to: **http://localhost:8000/docs**

You'll see Swagger UI with all endpoints to test interactively.

---

## 📚 Using the Web Interface

### 1. Landing Page

Open **http://localhost:3000**

You'll see:
- Project overview
- Features (4 cards)
- How-it-works (4 steps)
- Important disclaimer

Click **"Start Scanning"** button

### 2. Scan Page

You can:
- **Drag and drop** images (up to 5)
- **Click "Select Files"** to browse
- **Click "Camera"** to capture from webcam (if supported)
- Remove individual images
- Click **"Scan X Images"** button

Supported formats: JPG, PNG (max 10MB each)

### 3. Results Page

After scanning, you'll see:
- **Compliance Overview** with status badge
- **Field Status** - detected vs missing
- **Extracted Information** - all fields with confidence
- **Recommendations**
- **Export Report** - download as JSON

---

## 🛠️ Common Issues & Solutions

### Issue 1: Port Already in Use

```bash
# Port 3000 or 8000 already in use?
# Find and kill the process:

# For macOS/Linux:
lsof -i :3000  # Find process on port 3000
kill -9 <PID>   # Kill it

# For Docker, force recreate:
docker-compose down
docker-compose up -d --force-recreate
```

### Issue 2: PostgreSQL Connection Failed

```bash
# Verify PostgreSQL is running
brew services list  # macOS

# If not running, start it
brew services start postgresql@15

# Check connection
psql sih_compliance_db
# If this fails, database doesn't exist yet:
createdb sih_compliance_db
```

### Issue 3: PaddleOCR Takes Too Long

First run downloads the OCR model (~200MB). This is normal.

```bash
# Monitor download in logs
docker-compose logs -f backend | grep -i paddle

# Or just wait - takes 2-5 minutes on first run
```

### Issue 4: Frontend Can't Connect to Backend

```bash
# Check backend is running
curl http://localhost:8000/api/health

# Check CORS (should already be enabled)
# Check frontend API URL in vite.config.ts
# Restart frontend: npm run dev
```

### Issue 5: Tests Fail

```bash
# Make sure you're in venv
source venv/bin/activate

# Install missing dependencies
pip install -r requirements.txt

# Clear pytest cache
pytest --cache-clear

# Run again
pytest
```

---

## 📊 Project Structure Reference

```
MitraMetrology/
├── backend/                 # Python FastAPI
│   ├── app/
│   │   ├── services/       # Phase 1 + Phase 2 services
│   │   ├── models.py       # Phase 1 database models
│   │   ├── models_phase2.py# Phase 2 models
│   │   ├── main.py         # FastAPI app
│   │   └── rules/          # Compliance rules (v1 + v2)
│   ├── tests/              # All tests (Phase 1 + Phase 2)
│   └── requirements.txt    # Dependencies
│
├── frontend/               # React + TypeScript
│   ├── src/
│   │   ├── pages/         # Landing, Scan, Results
│   │   ├── components/    # UI components
│   │   ├── api/           # API client
│   │   └── contexts/      # Global state
│   └── package.json       # Dependencies
│
├── docker/                # Docker configs
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docker-compose.yml     # Service orchestration
└── [Documentation]        # Guides and references
```

---

## 🔑 Key Commands Quick Reference

### Docker
```bash
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
docker-compose logs backend   # View backend logs
docker-compose ps            # List running services
docker-compose exec backend bash  # Access backend container
```

### Backend (Local)
```bash
source venv/bin/activate                           # Activate venv
python -m uvicorn app.main:app --reload --port 8000  # Start server
pytest                                             # Run tests
pytest -v tests/test_phase2_services.py           # Run Phase 2 tests
```

### Frontend (Local)
```bash
npm install                   # Install dependencies
npm run dev                   # Start dev server
npm run build                # Build for production
npm run lint                 # Run linter
```

### Database (Local)
```bash
psql sih_compliance_db       # Connect to database
createdb sih_compliance_db   # Create database
```

---

## 📖 Documentation Files

If you need more details:

| File | Content |
|------|---------|
| README.md | Project overview and architecture |
| SETUP.md | Detailed setup instructions |
| PHASE2_DOCUMENTATION.md | Phase 2 advanced features |
| PHASE2_COMPLETION_SUMMARY.md | Phase 2 implementation details |
| API_ENDPOINTS.md (if exists) | API documentation |
| QUICKSTART.md | This file! |

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] Docker: All services running (`docker-compose ps`)
- [ ] Backend: Responds to `/api/health`
- [ ] Frontend: Loads at http://localhost:3000
- [ ] Database: Can connect with `psql`
- [ ] Tests: All pass with `pytest`
- [ ] UI: Can navigate to Scan page
- [ ] API: Can see docs at http://localhost:8000/docs

---

## 🎯 First Run: Complete Walkthrough

### Using Docker (Recommended)

```bash
# Step 1: Start services
cd /Users/namangaur/MitraMetrology
cp .env.example .env
docker-compose up -d

# Step 2: Wait for startup
sleep 45

# Step 3: Open browser
# Frontend: http://localhost:3000
# Click "Start Scanning"

# Step 4: Upload a test image
# Drag and drop any JPG/PNG
# Click "Scan 1 Image"

# Step 5: Wait for results
# Takes 30-120 seconds first time (OCR model download)

# Step 6: View results
# See compliance overview and extracted fields

# Done! ✅
```

---

## 🆘 Need Help?

1. **Check logs first:**
   ```bash
   docker-compose logs backend
   ```

2. **Check documentation:**
   - README.md - Overview
   - SETUP.md - Detailed setup
   - PHASE2_DOCUMENTATION.md - Advanced features

3. **Run tests to verify setup:**
   ```bash
   pytest tests/
   ```

4. **Check if ports are free:**
   ```bash
   lsof -i :3000
   lsof -i :8000
   lsof -i :5432
   ```

---

**You're all set! Start with Option 1 (Docker) if unsure. It's the fastest way to get running.**

Questions? Check the documentation files or run `pytest` to verify everything works.
