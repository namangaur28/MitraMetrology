"""
Database models for SIH Compliance Checker
"""
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import uuid


class User(Base):
    """User model for enforcement officers"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255))
    email = Column(String(255), unique=True, index=True)
    department = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scans = relationship("Scan", back_populates="user")


class Scan(Base):
    """Scan session model"""
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="scans")
    images = relationship("Image", back_populates="scan", cascade="all, delete-orphan")
    compliance_result = relationship("ComplianceResult", back_populates="scan", uselist=False, cascade="all, delete-orphan")


class Image(Base):
    """Image model for uploaded images"""
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    image_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"))
    filename = Column(String(255))
    file_path = Column(String(512))
    file_size = Column(Integer)
    mime_type = Column(String(50))
    width = Column(Integer)
    height = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scan = relationship("Scan", back_populates="images")
    ocr_results = relationship("OCRResult", back_populates="image", cascade="all, delete-orphan")
    extracted_fields = relationship("ExtractedField", back_populates="image", cascade="all, delete-orphan")


class OCRResult(Base):
    """OCR extraction results"""
    __tablename__ = "ocr_results"
    
    id = Column(Integer, primary_key=True, index=True)
    ocr_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    image_id = Column(Integer, ForeignKey("images.id"))
    text_blocks = Column(JSON)  # List of detected text with confidence and bounding boxes
    raw_text = Column(Text)  # Full extracted text
    confidence_avg = Column(Float)  # Average confidence score
    processing_time_ms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    image = relationship("Image", back_populates="ocr_results")


class ExtractedField(Base):
    """Extracted fields from OCR results"""
    __tablename__ = "extracted_fields"
    
    id = Column(Integer, primary_key=True, index=True)
    field_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    image_id = Column(Integer, ForeignKey("images.id"))
    field_name = Column(String(100), index=True)  # e.g., 'product_name', 'mrp', 'manufacturer'
    extracted_value = Column(Text)
    confidence = Column(Float)
    source_text = Column(Text)  # Original text from OCR
    bounding_box = Column(JSON)  # [x1, y1, x2, y2]
    extraction_method = Column(String(50))  # 'regex', 'keyword', 'pattern'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    image = relationship("Image", back_populates="extracted_fields")


class ComplianceResult(Base):
    """Compliance check results"""
    __tablename__ = "compliance_results"
    
    id = Column(Integer, primary_key=True, index=True)
    result_id = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()))
    scan_id = Column(Integer, ForeignKey("scans.id"))
    rules_version = Column(String(50))  # e.g., '2026'
    compliance_checks = Column(JSON)  # Structured compliance results
    overall_status = Column(String(50))  # 'pass', 'flag', 'needs_review'
    summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    scan = relationship("Scan", back_populates="compliance_result")
