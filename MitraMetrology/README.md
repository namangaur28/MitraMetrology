# SIH 2026 - Legal Metrology Compliance Checker

**AI-Assisted Compliance Verification System for Packaged Commodities**

This is a comprehensive solution for Smart India Hackathon 2026 (Problem Statement SIH26034) that helps enforcement officers quickly scan packaged commodities and get preliminary compliance assessments against Legal Metrology regulations.

## ⚠️ Important Disclaimer

**This is an AI-assisted preliminary assessment tool ONLY.**

- ❌ Cannot replace human expert verification by legal metrology officers
- ❌ All preliminary findings must be verified by authorized personnel
- ❌ Based on OCR extraction which may have limitations
- ❌ Legal compliance determination requires qualified review

Every result includes this disclaimer and requires human verification before any enforcement action.

---

## 🎯 Project Overview

### Problem Statement
"Software System to check compliance of Packaged Commodities under Legal Metrology (Packaged Commodities) Rules, 2011 by scanning products, images and labels."

### Solution
A web application where enforcement officers can:
1. **Upload** one or more images of packaged commodities
2. **Extract** mandatory declarations using OCR and AI
3. **Analyze** compliance with Legal Metrology rules
4. **Review** preliminary assessment with visual evidence

### Key Features
- 🔍 Advanced OCR text extraction (PaddleOCR)
- 📊 Automated field extraction (MRP, quantity, manufacturer, dates, etc.)
- ✅ Rules-based compliance checking
- 🖼️ Image preview with OCR region highlighting
- 📱 Multi-image support (up to 5 images per scan)
- 📸 Camera capture support
- 💾 PostgreSQL database for audit trail
- 🐳 Docker containerization for easy deployment

---

## 🏗️ Architecture

### Folder Structure

```
/
├── frontend/                          # React + TypeScript + Vite
│   ├── src/
│   │   ├── api/                       # API client
│   │   ├── components/                # React components
│   │   ├── contexts/                  # React Context (scan state)
│   │   ├── pages/                     # Page components
│   │   ├── index.css                  # Global styles
│   │   └── main.tsx                   # React entry point
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── index.html
│
├── backend/                           # Python FastAPI
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py              # API endpoints
│   │   ├── services/
│   │   │   ├── image_processor.py     # OpenCV image processing
│   │   │   ├── ocr_service.py         # PaddleOCR integration
│   │   │   ├── field_extractor.py     # Regex + keyword extraction
│   │   │   └── compliance_engine.py   # Rules-based compliance
│   │   ├── rules/
│   │   │   └── 2026/
│   │   │       └── packaged_commodities_rules.json
│   │   ├── models.py                  # SQLAlchemy models
│   │   ├── schemas.py                 # Pydantic schemas
│   │   ├── database.py                # Database connection
│   │   ├── config.py                  # Configuration
│   │   └── main.py                    # FastAPI app
│   ├── tests/
│   │   ├── test_ocr_service.py
│   │   ├── test_field_extractor.py
│   │   ├── test_compliance_engine.py
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── .env.example
│   └── conftest.py
│
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── nginx.conf
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 💻 Tech Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - HTTP client
- **Lucide React** - Icons

### Backend
- **Python 3.11** - Language
- **FastAPI** - Web framework
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation
- **PostgreSQL** - Database
- **OpenCV** - Image processing
- **PaddleOCR** - Text extraction
- **pytest** - Testing

### DevOps
- **Docker** - Containerization
- **Docker Compose** - Orchestration
- **Nginx** - Reverse proxy
- **PostgreSQL** - Data persistence

---

## 🚀 Installation & Setup

### Prerequisites
- Docker & Docker Compose (recommended)
- OR: Python 3.11+, Node.js 18+, PostgreSQL 15+

### Option 1: Docker (Recommended)

1. **Clone and navigate to project**
   ```bash
   cd /Users/namangaur/MitraMetrology
   ```

2. **Create environment file**
   ```bash
   cp .env.example .env
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Nginx: http://localhost

5. **View logs**
   ```bash
   docker-compose logs -f backend
   docker-compose logs -f frontend
   ```

6. **Stop services**
   ```bash
   docker-compose down
   ```

### Option 2: Local Development

#### Backend Setup

1. **Create Python virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file**
   ```bash
   cp .env.example .env
   ```

4. **Set database URL in .env**
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/sih_compliance_db
   ```

5. **Create PostgreSQL database**
   ```bash
   createdb sih_compliance_db
   ```

6. **Run database migrations**
   ```bash
   alembic upgrade head
   # Or use SQLAlchemy (tables created on app startup)
   ```

7. **Start backend server**
   ```bash
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

#### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**
   ```bash
   npm run dev
   ```

3. **Build for production**
   ```bash
   npm run build
   ```

---

## 📋 Environment Variables

### Backend (.env)
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/sih_compliance_db

# Environment
ENVIRONMENT=development
DEBUG=True

# FastAPI
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

### Frontend (.env)
```env
REACT_APP_API_URL=http://localhost:8000/api
```

---

## 🗄️ Database Setup

### Local PostgreSQL

1. **Install PostgreSQL** (if not already installed)
   ```bash
   # macOS
   brew install postgresql
   # Ubuntu
   sudo apt-get install postgresql
   ```

2. **Start PostgreSQL service**
   ```bash
   # macOS
   brew services start postgresql
   # Ubuntu
   sudo systemctl start postgresql
   ```

3. **Create database**
   ```bash
   createdb sih_compliance_db
   ```

4. **Run migrations** (if using Alembic)
   ```bash
   cd backend
   alembic upgrade head
   ```

### With Docker Compose
PostgreSQL starts automatically when you run `docker-compose up`.

---

## 🔗 API Documentation

### Base URL
- Development: `http://localhost:8000/api`
- Production: Configured via nginx

### Endpoints

#### 1. Create Scan Session
```
POST /api/scan
Response: { scan_id, created_at, images, compliance_result }
```

#### 2. Upload Image
```
POST /api/upload?scan_id={scan_id}
Body: multipart/form-data with file
Response: { scan_id, image_id, message }
```

#### 3. Extract Fields
```
POST /api/extract?scan_id={scan_id}
Response: { scan_id, message, extracted_fields }
```

#### 4. Check Compliance
```
POST /api/compliance/check?scan_id={scan_id}
Response: { result_id, compliance_checks, overall_status, summary, disclaimer }
```

#### 5. Get Scan Details
```
GET /api/scan/{scan_id}
Response: { scan_id, images, compliance_result }
```

#### 6. Health Check
```
GET /api/health
Response: { status, timestamp }
```

---

## 🧪 Testing

### Run All Tests
```bash
cd backend
pytest
```

### Run Specific Test File
```bash
pytest tests/test_field_extractor.py -v
pytest tests/test_compliance_engine.py -v
pytest tests/test_ocr_service.py -v
pytest tests/test_api.py -v
```

### Run with Coverage
```bash
pytest --cov=app tests/
```

### Test Categories
- **test_ocr_service.py**: OCR text extraction
- **test_field_extractor.py**: MRP, quantity, date, manufacturer extraction
- **test_compliance_engine.py**: Compliance rules evaluation
- **test_api.py**: API endpoint functionality

---

## 📖 How the System Works

### Step 1: Image Upload
- User uploads 1-5 product images
- System validates file type and size
- Images are processed:
  - Resized if necessary
  - Orientation corrected
  - Contrast enhanced
  - Noise reduced

### Step 2: OCR Processing
- PaddleOCR extracts text from images
- Returns text blocks with confidence scores
- Stores original and processed images

### Step 3: Field Extraction
- **Regex patterns** for structured fields (MRP, quantity, dates)
- **Keyword matching** for named fields (manufacturer, packer)
- **Text normalization** for robust matching
- Each field includes:
  - Extracted value
  - Confidence score
  - Source text
  - Bounding box coordinates

### Step 4: Compliance Checking
- Evaluated against rules in `2026/packaged_commodities_rules.json`
- Checks for mandatory declarations:
  - ✓ Product name/description
  - ✓ MRP (Maximum Retail Price)
  - ✓ Manufacturer/Distributor details
  - ✓ Net quantity/weight
  - ⚠️ Consumer care (optional)
  - ⚠️ Packer details (optional)
  - ⚠️ Importer details (optional)
  - ⚠️ Manufacturing/packing date (optional)

### Step 5: Results Presentation
- Visual display with extracted information
- Compliance status for each field
- Overall assessment (pass/flag/needs_review)
- **Prominent disclaimer** requiring human verification

---

## 📋 Compliance Rules

### Rules File Location
`backend/app/rules/2026/packaged_commodities_rules.json`

### Rule Structure
```json
{
  "rule_id": "mrp_present",
  "field": "mrp",
  "name": "Maximum Retail Price (MRP)",
  "description": "MRP must be clearly displayed on the package",
  "legal_reference": "Legal Metrology Rules 2011 - Schedule I",
  "mandatory": true,
  "check_type": "presence",
  "min_confidence": 0.5,
  "status_rules": {
    "present": "pass",
    "missing": "flag"
  }
}
```

### Status Legend
- **pass** ✓ - Field detected with acceptable confidence
- **flag** ✕ - Mandatory field missing
- **needs_review** ⚠️ - Optional field missing or low confidence

---

## 🔍 Field Extraction Details

### MRP Extraction
- Patterns: `MRP ₹50`, `Rs. 100`, `Price: ₹50`
- Regex patterns for currency symbols and amounts

### Net Quantity
- Patterns: `500ml`, `250gm`, `1kg`
- Supports: ml, gm, kg, l

### Date Extraction
- Patterns: `10/12/2024`, `15-06-2024`, `MFG Date: 10-12-2024`
- Identifies: Manufacturing, packing, import, expiry dates

### Manufacturer/Packer/Importer
- Keyword matching on labels
- Looks for subsequent text blocks
- Associated details and addresses

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check database connection
echo $DATABASE_URL

# Check logs
docker-compose logs backend

# Verify PostgreSQL is running
psql -U user -d sih_compliance_db -c "SELECT 1;"
```

### OCR Not Working
```bash
# PaddleOCR requires internet for first model download
# Ensure internet connection
# Check logs for download progress
```

### Frontend API Connection Issues
```bash
# Check CORS is enabled (it is by default)
# Verify backend URL in frontend config
# Check network tab in browser dev tools
```

### Image Upload Fails
```bash
# Check file size (max 10MB)
# Check permissions on uploads/ directory
# Verify allowed file types (jpg, jpeg, png)
```

---

## 📊 Database Schema

### Key Tables

**Scans**
- scan_id (UUID)
- user_id (FK to Users)
- created_at, updated_at

**Images**
- image_id (UUID)
- scan_id (FK)
- filename, file_path, file_size
- width, height (dimensions)

**OCRResults**
- ocr_id (UUID)
- image_id (FK)
- text_blocks (JSON - list of detected text with confidence & bbox)
- raw_text, confidence_avg
- processing_time_ms

**ExtractedFields**
- field_id (UUID)
- image_id (FK)
- field_name (product_name, mrp, manufacturer, etc.)
- extracted_value, confidence
- source_text, bounding_box
- extraction_method (regex, keyword, pattern)

**ComplianceResults**
- result_id (UUID)
- scan_id (FK)
- rules_version (e.g., "2026")
- compliance_checks (JSON - results for each rule)
- overall_status (pass, flag, needs_review)
- summary

---

## 📱 Frontend Pages

### Landing Page (`/`)
- Project overview
- Features showcase
- How-it-works section
- Important disclaimers
- Call-to-action to start scanning

### Scan Page (`/scan`)
- Image uploader with drag-drop
- Camera capture option
- Multiple file selection (up to 5)
- Upload and process button
- Loading state with progress

### Results Page (`/results/:id`)
- Compliance overview card
- Overall status badge
- Detailed field-by-field results
- Image gallery viewer
- Extracted fields display with confidence
- Export report option
- Instructions for verification

---

## 🔐 Security Considerations

- ✅ HTTPS ready (nginx can handle SSL)
- ✅ CORS configured for frontend
- ✅ SQL injection prevented (SQLAlchemy ORM)
- ✅ File upload validation (type, size)
- ✅ Environment variables for secrets
- ✅ Input validation via Pydantic

### For Production
1. Set `DEBUG=False`
2. Configure `ALLOWED_HOSTS` in nginx
3. Set up SSL certificates
4. Use strong database passwords
5. Enable HTTPS-only
6. Set up proper logging and monitoring

---

## 📈 Performance Considerations

### Optimization Strategies
1. **Image caching** - Processed images stored for fast retrieval
2. **OCR caching** - Results cached to avoid re-processing
3. **Database indexing** - Scan IDs and field names indexed
4. **Async processing** - File uploads handled asynchronously (can be enhanced)
5. **Image compression** - JPEG quality set to 85 (balance quality/size)

### Scalability
- Horizontal scaling possible with load balancer
- Database connection pooling via SQLAlchemy
- Static file serving via nginx
- Consider adding Redis for session/cache layer

---

## 🚦 Known Limitations

### Phase 1 Scope Limitations
1. **OCR Accuracy** - Depends on image quality; manually verify all extractions
2. **Field Extraction** - Regex-based; may not work for unusual label layouts
3. **Language Support** - English only in Phase 1
4. **No User Authentication** - Phase 2 feature
5. **No Batch Processing** - Phase 2 feature
6. **No Report History** - Phase 2/3 feature
7. **No Audit Trail** - Basic logging only

### Technical Limitations
- Single-instance deployment (Phase 2: distributed)
- No real-time notifications
- Limited to 5 images per scan
- OCR model requires internet for first download

---

## 🔄 Future Enhancements (Phase 2/3)

### Phase 2
- User authentication and authorization
- Scan history and filtering
- Batch compliance reports
- Advanced OCR with custom models
- Multi-language support (Hindi, regional languages)
- Admin dashboard
- Enforcement officer profiles

### Phase 3
- Mobile app
- Offline scanning capability
- Blockchain audit trail
- Integration with government databases
- Automated enforcement workflows
- Analytics and insights
- Legal reference documentation browser

---

## 📞 Support & Contact

For issues or questions:
1. Check this README first
2. Review troubleshooting section
3. Check API logs: `docker-compose logs backend`
4. Review test files for usage examples

---

## 📄 License

This project is built for Smart India Hackathon 2026.

---

## 🙏 Acknowledgments

- Legal Metrology Division, Government of India
- Smart India Hackathon 2026 organizers
- PaddleOCR community
- FastAPI and React communities

---

**Last Updated**: August 26, 2026  
**Version**: 1.0.0 (Phase 1)
