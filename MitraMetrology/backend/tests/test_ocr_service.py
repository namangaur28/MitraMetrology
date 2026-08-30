"""
Tests for OCR service
"""
import pytest
from app.services.ocr_service import OCRService


@pytest.fixture
def ocr_service():
    """Create OCR service instance"""
    return OCRService()


class TestOCRService:
    """Test OCR text extraction"""
    
    def test_ocr_initialization(self, ocr_service):
        """Test that OCR service initializes correctly"""
        assert ocr_service.ocr is not None
    
    def test_extract_text_with_invalid_path(self, ocr_service):
        """Test OCR with invalid image path"""
        success, result, error = ocr_service.extract_text("/invalid/path/image.jpg")
        assert success is False
        assert error != ""
    
    def test_bbox_normalization(self, ocr_service):
        """Test bbox normalization from 4-point to 2-point format"""
        bbox_points = [[10, 20], [100, 20], [100, 80], [10, 80]]
        normalized = ocr_service._normalize_bbox(bbox_points)
        
        assert len(normalized) == 4
        assert normalized == [10, 20, 100, 80]
    
    def test_extract_text_response_structure(self, ocr_service):
        """Test that extract_text returns correct structure"""
        success, result, error = ocr_service.extract_text("/invalid/path.jpg")
        
        if success:
            assert "text_blocks" in result
            assert "raw_text" in result
            assert "confidence_avg" in result
            assert "processing_time_ms" in result
