"""
Phase 2 comprehensive tests for advanced compliance features
Tests for normalization, conflict detection, scoring, and explainability
"""
import pytest
from app.services.text_normalizer import TextNormalizer, NormalizedPrice, NormalizedQuantity
from app.services.field_extractor_v2 import FieldExtractorV2
from app.services.conflict_detector import ConflictDetector
from app.services.compliance_scorer import ComplianceScorer
from app.services.explainability_engine import ExplainabilityEngine


class TestTextNormalizer:
    """Test text normalization"""
    
    @pytest.fixture
    def normalizer(self):
        return TextNormalizer()
    
    def test_price_normalization_rupee_symbol(self, normalizer):
        """Test MRP normalization with rupee symbol"""
        price = normalizer.extract_and_normalize_price("MRP ₹50")
        assert price is not None
        assert price.value == 50
        assert price.currency == "INR"
        assert str(price) == "₹50.00"
    
    def test_price_normalization_rs_format(self, normalizer):
        """Test MRP normalization with Rs. format"""
        price = normalizer.extract_and_normalize_price("Rs. 100.50")
        assert price is not None
        assert price.value == 100.50
        assert "100" in str(price)
    
    def test_quantity_normalization_ml(self, normalizer):
        """Test quantity normalization in ml"""
        qty = normalizer.extract_and_normalize_quantity("Net 500ml")
        assert qty is not None
        assert qty.value == 500
        assert qty.unit == "ml"
    
    def test_quantity_normalization_gm(self, normalizer):
        """Test quantity normalization in grams"""
        qty = normalizer.extract_and_normalize_quantity("250gm")
        assert qty is not None
        assert qty.value == 250
        assert qty.unit == "g"
    
    def test_quantity_normalization_kg(self, normalizer):
        """Test quantity normalization in kg"""
        qty = normalizer.extract_and_normalize_quantity("1.5 kg")
        assert qty is not None
        assert qty.value == 1.5
        assert qty.unit == "kg"
    
    def test_quantity_comparison(self, normalizer):
        """Test quantity value comparison"""
        qty1 = normalizer.extract_and_normalize_quantity("1000g")
        qty2 = normalizer.extract_and_normalize_quantity("1kg")
        
        assert qty1 is not None and qty2 is not None
        assert normalizer.compare_quantities(qty1, qty2)
    
    def test_date_normalization(self, normalizer):
        """Test date extraction and normalization"""
        date = normalizer.extract_and_normalize_date("MFG Date: 10/12/2024")
        assert date is not None
        assert date.day == 10
        assert date.month == 12
        assert date.year == 2024
    
    def test_language_mix_detection(self, normalizer):
        """Test Hindi/English mix detection"""
        result = normalizer.detect_language_mix("नाम Name")
        assert result["mixed"] == True
        assert result["has_hindi"] == True
        assert result["has_english"] == True
    
    def test_manufacturer_name_normalization(self, normalizer):
        """Test manufacturer name normalization"""
        normalized = normalizer.normalize_manufacturer_name("ABC Foods Ltd.")
        assert "Ltd" not in normalized
        assert "ABC" in normalized


class TestFieldExtractorV2:
    """Test advanced field extraction"""
    
    @pytest.fixture
    def extractor(self):
        return FieldExtractorV2()
    
    def test_mrp_extraction_with_normalization(self, extractor):
        """Test MRP extraction with price normalization"""
        text_blocks = [
            {"text": "MRP ₹50", "confidence": 0.95, "bbox": [10, 10, 100, 30]}
        ]
        
        result = extractor.extract_fields(text_blocks)
        mrp_field = result["mrp"]
        
        assert mrp_field.raw_value is not None
        assert mrp_field.normalized_value is not None
        assert mrp_field.normalization_applied == True
        assert mrp_field.normalization_type == "price"
    
    def test_quantity_extraction_with_normalization(self, extractor):
        """Test quantity extraction with normalization"""
        text_blocks = [
            {"text": "Net 500ml", "confidence": 0.92, "bbox": [10, 10, 100, 30]}
        ]
        
        result = extractor.extract_fields(text_blocks)
        qty_field = result["net_quantity"]
        
        assert qty_field.normalization_applied == True
        assert qty_field.normalization_type == "quantity"
    
    def test_language_detection_in_field(self, extractor):
        """Test language mix detection in extracted fields"""
        text_blocks = [
            {"text": "निर्माता Manufacturer ABC", "confidence": 0.8, "bbox": [10, 10, 100, 30]}
        ]
        
        result = extractor.extract_fields(text_blocks)
        mfg_field = result["manufacturer"]
        
        assert mfg_field.language_mix is not None
        assert mfg_field.language_mix["mixed"] == True


class TestConflictDetector:
    """Test multi-image conflict detection"""
    
    @pytest.fixture
    def detector(self):
        return ConflictDetector()
    
    def test_consistent_fields_across_images(self, detector):
        """Test detection of consistent fields"""
        multi_image_fields = {
            "image_1": {
                "mrp": {"value": "₹100", "confidence": 0.95},
                "net_quantity": {"value": "500ml", "confidence": 0.92}
            },
            "image_2": {
                "mrp": {"value": "₹100", "confidence": 0.93},
                "net_quantity": {"value": "500ml", "confidence": 0.90}
            }
        }
        
        result = detector.detect_conflicts(multi_image_fields)
        assert result["has_conflicts"] == False
    
    def test_conflicting_mrp_across_images(self, detector):
        """Test detection of MRP conflicts"""
        multi_image_fields = {
            "image_1": {
                "mrp": {"value": "₹100", "confidence": 0.95}
            },
            "image_2": {
                "mrp": {"value": "₹150", "confidence": 0.93}
            }
        }
        
        result = detector.detect_conflicts(multi_image_fields)
        assert result["has_conflicts"] == True
        assert len(result["conflicts"]) > 0
        assert result["conflicts"][0]["resolution"] == "conflicting"
    
    def test_format_variation_not_conflict(self, detector):
        """Test that format variations aren't flagged as conflicts"""
        multi_image_fields = {
            "image_1": {
                "mrp": {"value": "₹50", "confidence": 0.95}
            },
            "image_2": {
                "mrp": {"value": "Rs. 50", "confidence": 0.93}
            }
        }
        
        result = detector.detect_conflicts(multi_image_fields)
        # Should detect as consistent or format variation
        if len(result["conflicts"]) > 0:
            assert result["conflicts"][0]["conflict_type"] in ["value_match", "format_inconsistency"]
    
    def test_duplicate_detection(self, detector):
        """Test duplicate image detection"""
        image_ocr = {
            "image_1": "MRP ₹100 Net weight 500ml Manufacturer ABC",
            "image_2": "MRP ₹100 Net weight 500ml Manufacturer ABC"
        }
        
        result = detector.detect_duplicate_images(image_ocr)
        assert result["has_duplicates"] == True


class TestComplianceScorer:
    """Test compliance scoring"""
    
    @pytest.fixture
    def scorer(self):
        return ComplianceScorer()
    
    def test_score_with_all_mandatory_fields(self, scorer):
        """Test scoring when all mandatory fields detected"""
        findings = [
            {"status": "detected", "field_name": "product_name", "severity": "low"},
            {"status": "detected", "field_name": "manufacturer", "severity": "low"},
            {"status": "detected", "field_name": "net_quantity", "severity": "low"},
            {"status": "detected", "field_name": "mrp", "severity": "low"}
        ]
        
        readability = {"average_readability_score": 85}
        conflicts = {"has_conflicts": False}
        
        result = scorer.calculate_score(findings, readability, conflicts)
        
        assert result["overall_score"] >= 70  # Should score well
        assert result["is_preliminary"] == True
        assert result["is_legal_determination"] == False
    
    def test_score_with_missing_fields(self, scorer):
        """Test scoring with missing mandatory fields"""
        findings = [
            {"status": "detected", "field_name": "product_name", "severity": "low"},
            {"status": "potential_violation", "field_name": "manufacturer", "severity": "critical"}
        ]
        
        readability = {"average_readability_score": 70}
        conflicts = {"has_conflicts": True, "inconsistent_fields": ["mrp"]}
        
        result = scorer.calculate_score(findings, readability, conflicts)
        
        assert result["overall_score"] < 70  # Should score lower
        assert "potential_violation" in result["interpretation"].lower() or result["overall_score"] < 50


class TestExplainabilityEngine:
    """Test explainability engine"""
    
    @pytest.fixture
    def engine(self):
        return ExplainabilityEngine()
    
    def test_missing_field_finding(self, engine):
        """Test generation of missing field finding"""
        finding = engine.generate_missing_field_finding(
            field_name="mrp",
            rule_id="LM-002",
            severity="critical",
            searched_images=["img1", "img2"],
            search_confidence=0.3
        )
        
        assert finding.what_detected is not None
        assert finding.why_flagged is not None
        assert finding.rule_reference is not None
        assert finding.status == "potential_violation"
    
    def test_detected_field_finding(self, engine):
        """Test generation of detected field finding"""
        finding = engine.generate_detected_finding(
            field_name="mrp",
            value="₹100",
            rule_id="LM-002",
            image_id="img1",
            bbox=[10, 10, 100, 30],
            ocr_confidence=0.95,
            normalized_value="₹100.00"
        )
        
        assert finding.what_detected is not None
        assert finding.status == "detected"
        assert len(finding.where_in_image) == 1
    
    def test_conflict_finding(self, engine):
        """Test generation of conflict finding"""
        conflicts = {
            "conflicting_values": {"image_1": "₹100", "image_2": "₹150"},
            "confidence": {"image_1": 0.95, "image_2": 0.93},
            "conflict_score": 50
        }
        
        finding = engine.generate_conflict_finding("mrp", conflicts)
        
        assert finding.status == "needs_review"
        assert finding.rule_id == "LM-010"
        assert len(finding.where_in_image) == 2
    
    def test_summary_report(self, engine):
        """Test summary report generation"""
        findings = [
            engine.generate_detected_field_finding("mrp", "₹100", "LM-002", "img1", [10,10,100,30], 0.95),
            engine.generate_missing_field_finding("manufacturer", "LM-004", "critical", ["img1"], 0.2)
        ]
        
        summary = engine.generate_summary_report(findings)
        
        assert summary["total_findings"] == 2
        assert "by_severity" in summary
        assert "by_status" in summary
        assert len(summary["recommendations"]) > 0
