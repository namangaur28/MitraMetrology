# SIH 2026 Phase 2 - Advanced AI Compliance Intelligence

## Overview

Phase 2 transforms the basic OCR application into an **explainable AI-assisted compliance inspection system** with advanced document understanding, multi-image analysis, and human-in-the-loop verification.

**Key Principle:** This system is an inspection **assistant**, not an autonomous enforcer. Every finding is preliminary and requires human verification.

---

## Architecture Changes

### Phase 1 vs Phase 2

**Phase 1:**
- Basic OCR text extraction
- Simple field extraction (regex + keyword)
- Binary compliance status

**Phase 2:**
- Advanced OCR preprocessing (rotation, perspective, enhancement)
- Normalized field extraction with type conversion
- Explainable findings with evidence
- Multi-image conflict detection
- Preliminary compliance scoring
- PDF report generation
- Human verification workflow

---

## New Services

### 1. Text Normalizer (`text_normalizer.py`)

Standardizes and normalizes extracted values.

**Capabilities:**
- Price normalization: `₹50`, `Rs. 100`, `MRP ₹50.00` → `₹50.00`
- Quantity normalization: `500ml`, `0.5kg`, `500G` → `500 ml`, `0.5 kg`, etc.
- Date extraction: DD/MM/YYYY, DD-MM-YYYY formats
- Currency handling: INR, USD
- Language detection: Hindi/English mix detection
- Comparison methods: `compare_quantities()`, `compare_prices()`, `compare_dates()`

**Usage:**
```python
from app.services.text_normalizer import text_normalizer

price = text_normalizer.extract_and_normalize_price("MRP ₹50")
qty = text_normalizer.extract_and_normalize_quantity("500ml")
date = text_normalizer.extract_and_normalize_date("10/12/2024")

# Language detection
lang_info = text_normalizer.detect_language_mix("नाम Name")
# Returns: {"mixed": True, "has_hindi": True, "has_english": True, ...}
```

### 2. Enhanced Image Processor (`image_processor.py`)

Advanced preprocessing with rotation and perspective correction.

**New Methods:**
- `detect_rotation()` - Detects image rotation using Hough transform
- `correct_rotation()` - Corrects rotated images
- `correct_perspective()` - Applies perspective transform
- `analyze_readability()` - Metrics for image quality

**Metadata Output:**
```json
{
  "rotation_corrected": 15.5,
  "perspective_corrected": true,
  "readability_before": {
    "readability_score": 55,
    "laplacian_variance": 450,
    "contrast": 45,
    "brightness": 120,
    "issues": ["Image could be clearer"]
  },
  "readability_after": {
    "readability_score": 78,
    ...
  }
}
```

### 3. Field Extractor V2 (`field_extractor_v2.py`)

Enhanced field extraction with type normalization.

**Improvements:**
- Returns `ExtractedFieldV2` with `normalized_value`
- Tracks normalization type and whether it was applied
- Language mix detection per field
- Image ID tracking for multi-image scenarios

**Output Structure:**
```python
ExtractedFieldV2(
    field_name="mrp",
    raw_value="₹50",
    normalized_value="₹50.00",
    confidence=0.95,
    normalization_applied=True,
    normalization_type="price",
    language_mix={"mixed": False},
    image_id="img_001"
)
```

### 4. Conflict Detector (`conflict_detector.py`)

Multi-image analysis for duplicates and conflicts.

**Key Functions:**
- `detect_conflicts()` - Finds inconsistent values across images
- `detect_duplicate_images()` - Identifies duplicate or very similar images
- `generate_conflict_resolution_guidance()` - Provides guidance on resolving conflicts

**Conflict Types:**
- `value_match` - Same value, consistent
- `value_mismatch` - Different values (conflict!)
- `format_inconsistency` - Same value, different format

**Conflict Resolution Example:**
```
CONFLICT - MRP: Different values found across images.
  Image 1: ₹100
  Image 2: ₹150
Action: Please visually inspect product to determine correct value.
```

### 5. Explainability Engine (`explainability_engine.py`)

WHAT/WHY/WHICH/WHERE/HOW framework for findings.

**Finding Structure:**
```python
Finding(
    finding_id="FND-1693123456",
    rule_id="LM-002",
    field_name="mrp",
    severity="critical",
    status="potential_violation",
    
    # The 5 W's
    what_detected="MRP declaration could not be detected",
    why_flagged="MRP is mandatory for consumer protection",
    rule_reference="LM-002: Maximum Retail Price (MRP)",
    where_in_image=[Evidence(...)],
    confidence_score=95,
    
    context={...}
)
```

### 6. Compliance Scorer (`compliance_scorer.py`)

Generates preliminary compliance score (0-100).

**Categories:**
- Mandatory Declarations: 40%
- Text Readability: 20%
- Information Extraction: 25%
- Data Consistency: 15%

**Score Interpretation:**
- 85+: HIGH likelihood of compliance
- 70-84: MODERATE - needs verification
- 50-69: LOW - multiple issues
- <50: POTENTIAL NON-COMPLIANCE

**Clear Disclaimer:**
```
This is an AI-generated PRELIMINARY score only.
NOT a legal compliance determination.
```

### 7. PDF Report Generator (`pdf_report_generator.py`)

Professional compliance inspection reports with ReportLab.

**Report Sections:**
1. Inspection Header (ID, date, overall status)
2. Product Information
3. Extracted Declarations (with confidence)
4. Compliance Findings
5. Preliminary Compliance Score
6. Recommendations
7. Inspector Verification Section (for manual override)
8. Disclaimer

### 8. Audit Logger (`audit_logger.py`)

Immutable audit trail for all inspection actions.

**Logged Events:**
- `scan_created` - Scan session initiated
- `image_uploaded` - Image added to scan
- `ocr_completed` - OCR analysis finished
- `fields_extracted` - Fields extracted
- `findings_generated` - Findings created
- `score_calculated` - Score computed
- `finding_verified` - Inspector reviewed finding
- `finding_overridden` - AI result overridden
- `report_generated` - Report created

**Audit Entry:**
```json
{
  "timestamp": "2026-08-26T13:00:00",
  "scan_id": "scan_001",
  "action": "finding_verified",
  "entity_type": "finding",
  "entity_id": "finding_001",
  "user": "inspector_name",
  "decision": "approve",
  "comment": "Verified on physical product",
  "immutable": true
}
```

---

## Versioned Rules Engine

### Rules Version 2.0

Rules stored in `app/rules/2026/packaged_commodities_rules_v2.json`

**10 Rules Implemented:**

| Rule ID | Category | Field | Severity | Mandatory |
|---------|----------|-------|----------|-----------|
| LM-001 | Mandatory | product_name | Critical | Yes |
| LM-002 | Mandatory | mrp | Critical | Yes |
| LM-003 | Mandatory | net_quantity | Critical | Yes |
| LM-004 | Mandatory | manufacturer | Critical | Yes |
| LM-005 | Optional | consumer_care | High | No |
| LM-006 | Conditional | packer | High | No |
| LM-007 | Conditional | importer | High | No |
| LM-008 | Recommended | date | Medium | No |
| LM-009 | Quality | text_readability | High | Yes |
| LM-010 | Cross-field | data_consistency | High | No |

**Rule Structure:**
```json
{
  "rule_id": "LM-002",
  "category": "mandatory_declaration",
  "field": "mrp",
  "name": "Maximum Retail Price (MRP)",
  "severity": "critical",
  "mandatory": true,
  "check_type": "presence_and_format",
  "format_regex": "^₹?\\s*\\d+(\\.\\d{2})?$",
  "evidence_required": true,
  "additional_checks": ["must_be_positive", "reasonable_range"]
}
```

---

## Database Models (Phase 2)

### New Tables

**InspectionFinding**
- AI-generated findings with evidence
- Links to rules and scan
- Stores WHAT/WHY/WHICH/WHERE/HOW

**VerificationRecord**
- Inspector verification of findings
- Override capability
- Comment tracking

**AuditLog**
- Immutable audit trail
- All actions logged
- Timestamp and user tracking

**ComplianceScore**
- Preliminary score (0-100)
- Category breakdown
- Clear "NOT legal determination" flag

**ReadabilityAnalysis**
- Image quality metrics
- Font size estimates (with calibration note)
- Blur, contrast, brightness

**ImageConflict**
- Tracks conflicting values across images
- Resolution status
- Who resolved it

**ComplianceReport**
- Generated PDF reports
- Report path and metadata
- Snapshot of findings

---

## API Changes (Phase 2)

### New Endpoints (Proposed)

```
POST /api/v2/scan
  └─ Creates scan with v2 processing pipeline

POST /api/v2/scan/{id}/analyze
  └─ Run full analysis: OCR → extraction → findings → scoring

GET /api/v2/scan/{id}/findings
  └─ Get all findings with explainability

POST /api/v2/scan/{id}/findings/{finding_id}/verify
  └─ Inspector verifies/overrides finding

GET /api/v2/scan/{id}/report/pdf
  └─ Generate PDF report

GET /api/v2/scan/{id}/audit-trail
  └─ Get immutable audit log
```

### Response Example

```json
{
  "scan_id": "scan_001",
  "status": "completed",
  "overall_assessment": "needs_human_verification",
  
  "findings": [
    {
      "finding_id": "FND-001",
      "rule_id": "LM-002",
      "what_detected": "MRP ₹100 detected on image 1",
      "why_flagged": "MRP declaration is mandatory",
      "rule_reference": "LM-002: Maximum Retail Price",
      "where_in_image": {
        "image_id": "img_001",
        "bbox": [100, 150, 300, 180],
        "confidence": 0.95
      },
      "status": "detected"
    },
    {
      "finding_id": "FND-002",
      "rule_id": "LM-004",
      "what_detected": "Manufacturer details could not be detected",
      "why_flagged": "Manufacturer information is required by law",
      "status": "potential_violation",
      "severity": "critical"
    }
  ],
  
  "compliance_score": {
    "overall": 72,
    "is_preliminary": true,
    "is_legal_determination": false,
    "categories": {
      "mandatory_declarations": 30,
      "text_readability": 18,
      "information_extraction": 20,
      "data_consistency": 4
    }
  },
  
  "audit_trail": [
    {"timestamp": "...", "action": "scan_created"},
    {"timestamp": "...", "action": "image_uploaded"},
    ...
  ]
}
```

---

## Testing

### Test Files

**test_phase2_services.py** - Comprehensive tests for:
- Text normalization (prices, quantities, dates)
- Field extraction with normalization
- Conflict detection
- Compliance scoring
- Explainability engine

### Synthetic Test Packages (11 Scenarios)

```python
from tests.synthetic_test_packages import get_test_package

# Load test scenario
package = get_test_package("compliant")  # All fields present

package = get_test_package("missing_mrp")  # Critical violation

package = get_test_package("conflicting_values")  # Front vs back conflict

package = get_test_package("hindi_english_mix")  # Bilingual

package = get_test_package("blurry_image")  # Readability issues

# ... 6 more scenarios
```

**Running Tests:**
```bash
# Run all Phase 2 tests
pytest tests/test_phase2_services.py -v

# Run specific test
pytest tests/test_phase2_services.py::TestTextNormalizer -v

# Test with synthetic packages
pytest tests/test_phase2_services.py -k "compliant or missing" -v
```

---

## Known Limitations (Phase 2)

### Planned for Phase 3

- [ ] User authentication and authorization
- [ ] Human-in-the-loop UI (approve/reject findings)
- [ ] Mobile app for inspectors
- [ ] Integration with government databases
- [ ] Blockchain audit trail
- [ ] Multi-language UI (Hindi, regional)
- [ ] Advanced OCR with custom models
- [ ] Batch processing (100+ images)

### Current Limitations

- YOLO not integrated (can be added if beneficial)
- No real-time notifications
- No distributed processing (Celery infrastructure ready)
- Font size requires calibrated inspection
- Single-instance deployment

---

## Migration Path from Phase 1

### Backward Compatibility

- Phase 1 database tables remain unchanged
- Phase 1 API endpoints (/api/scan, /api/upload, etc.) still work
- New Phase 2 endpoints at `/api/v2/` 

### Migration Steps

1. Add Phase 2 database models (non-breaking)
2. Deploy Phase 2 services alongside Phase 1
3. Update image processor to use new methods (with fallback)
4. Enable Phase 2 endpoints for new scans
5. Maintain Phase 1 compatibility for existing scans

---

## Performance Considerations

### Optimization

- Image preprocessing caching (processed images reused)
- OCR result caching (avoid re-processing same image)
- Database indexes on scan_id, finding_id
- Async processing ready (Celery infrastructure in requirements.txt)

### Scalability Path

- Current: Single-instance with optimized queries
- Phase 3: Async processing with Celery + Redis
- Phase 3: Distributed OCR processing
- Phase 3: Caching layer with Redis

---

## Compliance Rules Reference

### Legal Basis

All rules based on:
- **Legal Metrology (Packaged Commodities) Rules, 2011**
- **Official Legal Metrology Act documentation**
- **Government of India standards**

### Rule Categories

1. **Mandatory Declarations** - Must be present on all packages
2. **Conditional Declarations** - Required based on product type or origin
3. **Recommended Declarations** - Best practices
4. **Quality Metrics** - Standards for clarity and readability
5. **Cross-Field Validation** - Consistency across images

---

## Documentation Files

- `PHASE2_DOCUMENTATION.md` - This file
- `IMPLEMENTATION_SUMMARY.md` - Phase 1 technical details
- `README.md` - Project overview
- `SETUP.md` - Deployment and setup

---

## Quick Start with Phase 2

```python
# 1. Initialize services
from app.services.text_normalizer import text_normalizer
from app.services.field_extractor_v2 import field_extractor_v2
from app.services.conflict_detector import conflict_detector
from app.services.explainability_engine import explainability_engine
from app.services.compliance_scorer import compliance_scorer

# 2. Process image
from app.services.image_processor import image_processor
success, error, metadata = image_processor.process_image(
    "input.jpg", "processed.jpg"
)

# 3. Extract with normalization
extracted = field_extractor_v2.extract_fields(text_blocks)

# 4. Detect conflicts across images
conflicts = conflict_detector.detect_conflicts(multi_image_fields)

# 5. Generate findings
finding = explainability_engine.generate_detected_finding(
    "mrp", "₹100", "LM-002", "img_1", [10,10,100,30], 0.95
)

# 6. Score compliance
score = compliance_scorer.calculate_score(findings, readability, conflicts)

# 7. Generate report
pdf_bytes = pdf_report_generator.generate_report(inspection_data)
```

---

**Phase 2 Status:** ✅ Complete - Ready for integration testing

**Next Phase:** Human-in-the-loop UI and government integration
