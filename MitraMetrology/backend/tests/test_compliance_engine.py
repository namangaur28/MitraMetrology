"""
Tests for compliance engine
"""
import pytest
from app.services.compliance_engine import ComplianceEngine


@pytest.fixture
def compliance_engine():
    """Create compliance engine instance"""
    return ComplianceEngine()


class TestComplianceCheck:
    """Test compliance checking functionality"""
    
    def test_mrp_pass_check(self, compliance_engine):
        """Test MRP compliance check - pass case"""
        extracted_fields = {
            "mrp": {
                "value": "₹100",
                "confidence": 0.95,
                "source_text": "MRP ₹100",
                "bbox": None
            }
        }
        
        result = compliance_engine.check_compliance(extracted_fields)
        
        assert result["rules_version"] == "2026"
        assert result["overall_status"] in ["pass", "flag", "needs_review"]
        assert len(result["compliance_checks"]) > 0
    
    def test_mrp_flag_check(self, compliance_engine):
        """Test MRP compliance check - flag case (missing)"""
        extracted_fields = {
            "mrp": {
                "value": None,
                "confidence": 0.0,
                "source_text": "",
                "bbox": None
            }
        }
        
        result = compliance_engine.check_compliance(extracted_fields)
        
        # Find MRP check result
        mrp_check = next((c for c in result["compliance_checks"] if c["field"] == "mrp"), None)
        assert mrp_check is not None
        assert mrp_check["status"] in ["flag", "needs_review"]
    
    def test_manufacturer_pass_check(self, compliance_engine):
        """Test manufacturer compliance check"""
        extracted_fields = {
            "manufacturer": {
                "value": "ABC Foods Ltd",
                "confidence": 0.85,
                "source_text": "Manufacturer: ABC Foods Ltd",
                "bbox": None
            }
        }
        
        result = compliance_engine.check_compliance(extracted_fields)
        
        assert result["overall_status"] in ["pass", "needs_review"]
    
    def test_net_quantity_pass_check(self, compliance_engine):
        """Test net quantity compliance check"""
        extracted_fields = {
            "net_quantity": {
                "value": "500ml",
                "confidence": 0.92,
                "source_text": "Net 500ml",
                "bbox": None
            }
        }
        
        result = compliance_engine.check_compliance(extracted_fields)
        
        # Check that net_quantity check exists
        qty_check = next((c for c in result["compliance_checks"] if c["field"] == "net_quantity"), None)
        assert qty_check is not None
        assert qty_check["status"] == "pass"


class TestComplianceOverallStatus:
    """Test overall compliance status determination"""
    
    def test_all_mandatory_fields_pass(self, compliance_engine):
        """Test when all mandatory fields are present"""
        extracted_fields = {
            "product_name": {"value": "Tea Bag", "confidence": 0.95, "source_text": "", "bbox": None},
            "manufacturer": {"value": "ABC", "confidence": 0.9, "source_text": "", "bbox": None},
            "net_quantity": {"value": "500ml", "confidence": 0.92, "source_text": "", "bbox": None},
            "mrp": {"value": "₹100", "confidence": 0.88, "source_text": "", "bbox": None},
        }
        
        result = compliance_engine.check_compliance(extracted_fields)
        
        assert result["overall_status"] == "pass"
    
    def test_mandatory_field_missing(self, compliance_engine):
        """Test when mandatory field is missing"""
        extracted_fields = {
            "product_name": {"value": None, "confidence": 0.0, "source_text": "", "bbox": None},
            "manufacturer": {"value": "ABC", "confidence": 0.9, "source_text": "", "bbox": None},
            "net_quantity": {"value": "500ml", "confidence": 0.92, "source_text": "", "bbox": None},
            "mrp": {"value": "₹100", "confidence": 0.88, "source_text": "", "bbox": None},
        }
        
        result = compliance_engine.check_compliance(extracted_fields)
        
        assert result["overall_status"] == "flag"
    
    def test_optional_field_missing(self, compliance_engine):
        """Test when optional field is missing"""
        extracted_fields = {
            "product_name": {"value": "Tea Bag", "confidence": 0.95, "source_text": "", "bbox": None},
            "manufacturer": {"value": "ABC", "confidence": 0.9, "source_text": "", "bbox": None},
            "net_quantity": {"value": "500ml", "confidence": 0.92, "source_text": "", "bbox": None},
            "mrp": {"value": "₹100", "confidence": 0.88, "source_text": "", "bbox": None},
            "consumer_care": {"value": None, "confidence": 0.0, "source_text": "", "bbox": None},
        }
        
        result = compliance_engine.check_compliance(extracted_fields)
        
        # Optional field missing should not make overall status "flag"
        assert result["overall_status"] in ["pass", "needs_review"]


class TestComplianceSummary:
    """Test compliance summary generation"""
    
    def test_summary_generation(self, compliance_engine):
        """Test that compliance summary is generated"""
        extracted_fields = {
            "product_name": {"value": "Tea", "confidence": 0.95, "source_text": "", "bbox": None},
            "mrp": {"value": "₹100", "confidence": 0.88, "source_text": "", "bbox": None},
        }
        
        result = compliance_engine.check_compliance(extracted_fields)
        
        assert result["summary"] != ""
        assert "AI-assisted preliminary assessment" in result["summary"]
    
    def test_disclaimer_presence(self, compliance_engine):
        """Test that disclaimer is included in result"""
        extracted_fields = {}
        
        result = compliance_engine.check_compliance(extracted_fields)
        
        assert "disclaimer" in result
        assert result["disclaimer"] != ""
