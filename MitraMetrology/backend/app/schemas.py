"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from typing import List, Dict, Optional, Any
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    department: str


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: int
    user_id: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# OCR Text Block Schema
class TextBlock(BaseModel):
    text: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]


class OCRResultSchema(BaseModel):
    ocr_id: str
    text_blocks: List[TextBlock]
    raw_text: str
    confidence_avg: float
    processing_time_ms: int
    
    class Config:
        from_attributes = True


# Extracted Field Schema
class ExtractedFieldSchema(BaseModel):
    field_id: str
    field_name: str
    extracted_value: Optional[str]
    confidence: Optional[float]
    source_text: Optional[str]
    bounding_box: Optional[List[float]]
    extraction_method: Optional[str]
    
    class Config:
        from_attributes = True


# Image Schemas
class ImageSchema(BaseModel):
    image_id: str
    filename: str
    file_size: int
    mime_type: str
    width: int
    height: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Compliance Check Result
class ComplianceCheck(BaseModel):
    field: str
    status: str  # 'pass', 'flag', 'missing'
    confidence: Optional[float]
    details: Optional[str]


class ComplianceResultSchema(BaseModel):
    result_id: str
    rules_version: str
    compliance_checks: List[ComplianceCheck]
    overall_status: str  # 'pass', 'flag', 'needs_review'
    summary: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Scan Schemas
class ScanBase(BaseModel):
    pass


class ScanCreate(ScanBase):
    pass


class ScanResponse(BaseModel):
    scan_id: str
    created_at: datetime
    images: List[ImageSchema] = []
    compliance_result: Optional[ComplianceResultSchema] = None
    
    class Config:
        from_attributes = True


# Detailed Scan Result
class ScanDetailedResult(BaseModel):
    scan_id: str
    created_at: datetime
    images: List[Dict[str, Any]]  # Images with OCR and extracted fields
    compliance_result: Optional[ComplianceResultSchema]
    
    class Config:
        from_attributes = True


# API Response Schemas
class UploadResponse(BaseModel):
    scan_id: str
    image_id: str
    message: str


class APIError(BaseModel):
    error: str
    details: Optional[str] = None
    status_code: int


# Request Schemas
class ComplianceCheckRequest(BaseModel):
    scan_id: str


class ScanRequest(BaseModel):
    user_id: Optional[str] = None
