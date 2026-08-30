"""
Phase 2 Database models for advanced compliance intelligence
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import uuid
import enum


class InspectionFinding(Base):
    """AI-generated findings for compliance inspection"""
    __tablename__ = "inspection_findings"
    
    id = Column(Integer, primary_key=True, index=True)
    finding_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(Integer, ForeignKey("scans.id"))
    rule_id = Column(String(50))  # e.g., "LM-001"
    finding_type = Column(String(50))  # 'missing', 'malformed', 'conflicting', 'unclear'
    severity = Column(String(20))  # 'critical', 'high', 'medium', 'low'
    status = Column(String(50))  # 'detected', 'potential_violation', 'needs_review'
    
    # Evidence
    evidence_images = Column(JSON)  # List of image IDs with bounding boxes
    evidence_text = Column(Text)  # Source text from OCR
    evidence_confidence = Column(Float)  # 0.0 to 1.0
    
    # AI explanation
    what_detected = Column(Text)  # What the AI found
    why_flagged = Column(Text)  # Why it was flagged
    how_confident = Column(Float)  # Confidence 0-100
    
    # Rule reference
    rule_reference = Column(String(500))  # Legal reference
    rule_description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scan = relationship("Scan", back_populates="inspection_findings")
    verification_record = relationship("VerificationRecord", back_populates="finding", uselist=False)


class VerificationRecord(Base):
    """Human verification/override of AI findings"""
    __tablename__ = "verification_records"
    
    id = Column(Integer, primary_key=True, index=True)
    verification_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    finding_id = Column(Integer, ForeignKey("inspection_findings.id"))
    
    # Inspector decision
    decision = Column(String(50))  # 'approve', 'reject', 'needs_more_info'
    inspector_comment = Column(Text)
    
    # AI vs Inspector
    ai_result = Column(String(50))  # Original AI result
    inspector_override = Column(Boolean, default=False)  # Did inspector override?
    
    verified_by = Column(String(255))  # Inspector name/ID
    verified_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    finding = relationship("InspectionFinding", back_populates="verification_record")


class AuditLog(Base):
    """Immutable audit trail"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(Integer, ForeignKey("scans.id"))
    
    action = Column(String(100))  # e.g., 'scan_created', 'image_uploaded', 'analysis_completed'
    entity_type = Column(String(50))  # 'scan', 'image', 'finding', 'verification'
    entity_id = Column(String(36))
    
    details = Column(JSON)  # Additional details
    user = Column(String(255))  # Who performed the action
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    scan = relationship("Scan")


class ComplianceScore(Base):
    """Preliminary compliance score (not legal determination)"""
    __tablename__ = "compliance_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    score_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(Integer, ForeignKey("scans.id"), unique=True)
    
    overall_score = Column(Float)  # 0-100
    
    # Category scores
    mandatory_declarations_score = Column(Float)
    text_readability_score = Column(Float)
    information_extraction_score = Column(Float)
    data_consistency_score = Column(Float)
    
    # Metadata
    scoring_version = Column(String(20))  # "2.0"
    calculation_details = Column(JSON)  # How score was calculated
    
    # Disclaimer
    is_preliminary = Column(Boolean, default=True)
    is_legal_determination = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scan = relationship("Scan", back_populates="compliance_score")


class ReadabilityAnalysis(Base):
    """Image readability and font analysis"""
    __tablename__ = "readability_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    image_id = Column(Integer, ForeignKey("images.id"))
    
    # Readability metrics
    readability_score = Column(Float)  # 0-100
    laplacian_variance = Column(Float)  # Blur detection
    contrast = Column(Float)
    brightness = Column(Float)
    resolution_dpi = Column(Float)
    
    # Issues found
    issues = Column(JSON)  # List of readability issues
    
    # Font analysis
    font_height_pixels = Column(Float)
    estimated_physical_size = Column(String(100))  # e.g., "2mm - 3mm (estimated)"
    requires_calibration = Column(Boolean, default=True)  # Physical size needs calibrated inspection
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    image = relationship("Image", back_populates="readability_analysis")


class ImageConflict(Base):
    """Track conflicting information across multiple images"""
    __tablename__ = "image_conflicts"
    
    id = Column(Integer, primary_key=True, index=True)
    conflict_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(Integer, ForeignKey("scans.id"))
    
    field_name = Column(String(100))  # e.g., 'mrp', 'net_quantity'
    
    # Conflicting values
    image_ids = Column(JSON)  # List of image IDs with conflicts
    values = Column(JSON)  # List of conflicting values
    confidence_levels = Column(JSON)  # Confidence for each value
    
    conflict_severity = Column(String(50))  # 'high', 'medium', 'low'
    conflict_type = Column(String(50))  # 'value_mismatch', 'format_inconsistency'
    
    resolved = Column(Boolean, default=False)
    resolution = Column(Text)  # How was conflict resolved
    resolved_by = Column(String(255))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    scan = relationship("Scan", back_populates="image_conflicts")


class ComplianceReport(Base):
    """Generated compliance report"""
    __tablename__ = "compliance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(Integer, ForeignKey("scans.id"))
    
    report_type = Column(String(50))  # 'pdf', 'json', 'html'
    report_path = Column(String(512))  # Path to generated report
    file_size = Column(Integer)
    
    # Report metadata
    generated_at = Column(DateTime, default=datetime.utcnow)
    generated_by = Column(String(255))  # System or user who generated
    
    # Content snapshot
    inspection_id = Column(String(36))
    findings_count = Column(Integer)
    compliance_score = Column(Float)
    overall_status = Column(String(50))
    
    # Relationships
    scan = relationship("Scan", back_populates="compliance_reports")


# Update Scan model with new relationships (to be applied in migration)
# This is pseudo-code showing the additions to existing Scan model:
"""
In existing Scan model, add:
    inspection_findings = relationship("InspectionFinding", back_populates="scan", cascade="all, delete-orphan")
    image_conflicts = relationship("ImageConflict", back_populates="scan", cascade="all, delete-orphan")
    compliance_score = relationship("ComplianceScore", back_populates="scan", uselist=False, cascade="all, delete-orphan")
    compliance_reports = relationship("ComplianceReport", back_populates="scan", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="scan", cascade="all, delete-orphan")
"""

# Update Image model with new relationships
"""
In existing Image model, add:
    readability_analysis = relationship("ReadabilityAnalysis", back_populates="image", uselist=False, cascade="all, delete-orphan")
"""
