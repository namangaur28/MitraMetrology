"""
Tests for API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db

# Use in-memory SQLite for testing
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self):
        """Test /health endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestScanEndpoint:
    """Test scan creation endpoint"""
    
    def test_create_scan(self):
        """Test POST /api/scan"""
        response = client.post("/api/scan")
        assert response.status_code == 200
        data = response.json()
        assert "scan_id" in data
        assert "created_at" in data
        assert "images" in data
    
    def test_get_scan(self):
        """Test GET /api/scan/{scan_id}"""
        # First create a scan
        create_response = client.post("/api/scan")
        scan_id = create_response.json()["scan_id"]
        
        # Then retrieve it
        get_response = client.get(f"/api/scan/{scan_id}")
        assert get_response.status_code == 200
        data = get_response.json()
        assert data["scan_id"] == scan_id
    
    def test_get_nonexistent_scan(self):
        """Test GET /api/scan/{scan_id} for non-existent scan"""
        response = client.get("/api/scan/nonexistent-scan-id")
        assert response.status_code == 404


class TestUploadEndpoint:
    """Test image upload endpoint"""
    
    def test_upload_without_scan(self):
        """Test image upload without scan_id"""
        response = client.post("/api/upload")
        assert response.status_code in [400, 422]
    
    def test_upload_to_invalid_scan(self):
        """Test image upload to non-existent scan"""
        response = client.post(
            "/api/upload?scan_id=invalid-scan-id",
            files={"file": ("test.jpg", b"invalid content", "image/jpeg")}
        )
        assert response.status_code == 404


class TestApiRoot:
    """Test root API endpoint"""
    
    def test_root_endpoint(self):
        """Test GET /"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"


class TestExtractEndpoint:
    """Test field extraction endpoint"""
    
    def test_extract_without_images(self):
        """Test extraction without images in scan"""
        # Create scan
        create_response = client.post("/api/scan")
        scan_id = create_response.json()["scan_id"]
        
        # Try to extract fields
        response = client.post(f"/api/extract?scan_id={scan_id}")
        assert response.status_code in [400, 404, 200]


class TestComplianceEndpoint:
    """Test compliance checking endpoint"""
    
    def test_compliance_check_nonexistent_scan(self):
        """Test compliance check for non-existent scan"""
        response = client.post("/api/compliance/check?scan_id=invalid-scan-id")
        assert response.status_code == 404
    
    def test_compliance_check_empty_scan(self):
        """Test compliance check for empty scan"""
        # Create scan
        create_response = client.post("/api/scan")
        scan_id = create_response.json()["scan_id"]
        
        # Try to check compliance
        response = client.post(f"/api/compliance/check?scan_id={scan_id}")
        assert response.status_code == 200
        data = response.json()
        assert "compliance_checks" in data
        assert "overall_status" in data
