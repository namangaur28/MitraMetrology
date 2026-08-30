"""
Tests for field extraction service
"""
import pytest
from app.services.field_extractor import FieldExtractor, ExtractedField


@pytest.fixture
def field_extractor():
    """Create field extractor instance"""
    return FieldExtractor()


class TestMRPExtraction:
    """Test MRP/Price extraction"""
    
    def test_mrp_with_rupee_symbol(self, field_extractor):
        """Test MRP extraction with rupee symbol"""
        text_blocks = [
            {"text": "MRP ₹50", "confidence": 0.95, "bbox": [10, 10, 100, 30]},
            {"text": "Other text", "confidence": 0.8, "bbox": [10, 40, 100, 60]}
        ]
        
        result = field_extractor.extract_fields(text_blocks)
        mrp_field = result["mrp"]
        
        assert mrp_field.value is not None
        assert "50" in mrp_field.value or "₹" in mrp_field.value
        assert mrp_field.extraction_method == "regex"
    
    def test_mrp_extraction_with_currency(self, field_extractor):
        """Test MRP extraction with currency format"""
        text_blocks = [
            {"text": "Price: RS. 100", "confidence": 0.9, "bbox": [10, 10, 100, 30]}
        ]
        
        result = field_extractor.extract_fields(text_blocks)
        mrp_field = result["mrp"]
        
        assert mrp_field.value is not None
        assert "100" in mrp_field.value


class TestNetQuantityExtraction:
    """Test net quantity/weight extraction"""
    
    def test_quantity_with_ml(self, field_extractor):
        """Test quantity extraction in ml"""
        text_blocks = [
            {"text": "Net 500ml", "confidence": 0.92, "bbox": [10, 10, 100, 30]}
        ]
        
        result = field_extractor.extract_fields(text_blocks)
        qty_field = result["net_quantity"]
        
        assert qty_field.value is not None
        assert "500" in qty_field.value
    
    def test_quantity_with_gm(self, field_extractor):
        """Test quantity extraction in grams"""
        text_blocks = [
            {"text": "Weight: 250gm", "confidence": 0.88, "bbox": [10, 10, 100, 30]}
        ]
        
        result = field_extractor.extract_fields(text_blocks)
        qty_field = result["net_quantity"]
        
        assert qty_field.value is not None
        assert "250" in qty_field.value
    
    def test_quantity_with_kg(self, field_extractor):
        """Test quantity extraction in kilograms"""
        text_blocks = [
            {"text": "Net weight: 1kg", "confidence": 0.91, "bbox": [10, 10, 100, 30]}
        ]
        
        result = field_extractor.extract_fields(text_blocks)
        qty_field = result["net_quantity"]
        
        assert qty_field.value is not None
        assert "1" in qty_field.value


class TestDateExtraction:
    """Test date extraction"""
    
    def test_date_with_slashes(self, field_extractor):
        """Test date extraction with slash format"""
        text_blocks = [
            {"text": "MFG Date: 10/12/2024", "confidence": 0.89, "bbox": [10, 10, 100, 30]}
        ]
        
        result = field_extractor.extract_fields(text_blocks)
        date_field = result["date"]
        
        assert date_field.value is not None
        assert "10" in date_field.value or "12" in date_field.value or "2024" in date_field.value
    
    def test_date_with_hyphens(self, field_extractor):
        """Test date extraction with hyphen format"""
        text_blocks = [
            {"text": "Packed: 15-06-2024", "confidence": 0.87, "bbox": [10, 10, 100, 30]}
        ]
        
        result = field_extractor.extract_fields(text_blocks)
        date_field = result["date"]
        
        assert date_field.value is not None


class TestManufacturerExtraction:
    """Test manufacturer extraction"""
    
    def test_manufacturer_keyword_detection(self, field_extractor):
        """Test manufacturer extraction with keyword"""
        text_blocks = [
            {"text": "Manufacturer:", "confidence": 0.9, "bbox": [10, 10, 100, 30]},
            {"text": "ABC Foods Ltd", "confidence": 0.85, "bbox": [10, 40, 100, 60]}
        ]
        
        result = field_extractor.extract_fields(text_blocks)
        mfg_field = result["manufacturer"]
        
        # Manufacturer extraction works based on keyword detection
        assert mfg_field.extraction_method == "keyword"


class TestFieldExtractionGeneral:
    """General field extraction tests"""
    
    def test_extract_all_fields_returns_dict(self, field_extractor):
        """Test that extract_fields returns all fields"""
        text_blocks = [
            {"text": "Product Name", "confidence": 0.95, "bbox": [10, 10, 100, 30]},
            {"text": "MRP ₹100", "confidence": 0.9, "bbox": [10, 40, 100, 60]}
        ]
        
        result = field_extractor.extract_fields(text_blocks)
        
        assert isinstance(result, dict)
        assert "product_name" in result
        assert "manufacturer" in result
        assert "mrp" in result
        assert "net_quantity" in result
        assert "date" in result
    
    def test_extracted_field_to_dict(self, field_extractor):
        """Test ExtractedField to_dict conversion"""
        field = ExtractedField(
            field_name="test",
            value="test_value",
            confidence=0.95,
            source_text="test_text",
            bbox=[10, 10, 100, 30],
            extraction_method="regex"
        )
        
        field_dict = field.to_dict()
        
        assert field_dict["field_name"] == "test"
        assert field_dict["value"] == "test_value"
        assert field_dict["confidence"] == 0.95
