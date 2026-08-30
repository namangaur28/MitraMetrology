"""
API routes for scanning and compliance checking
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime
import logging

from app.database import get_db
from app.models import User, Scan, Image, OCRResult, ExtractedField, ComplianceResult
from app.schemas import (
    UploadResponse, ScanResponse, ScanDetailedResult, APIError,
    ComplianceCheckRequest, ComplianceResultSchema
)
from app.services.image_processor import image_processor
from app.services.ocr_service import ocr_service
from app.services.field_extractor import field_extractor
from app.services.compliance_engine import compliance_engine
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["compliance"])


def ensure_upload_dir():
    """Ensure upload directory exists"""
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs(f"{settings.upload_dir}/originals", exist_ok=True)
    os.makedirs(f"{settings.upload_dir}/processed", exist_ok=True)


@router.post("/scan", response_model=ScanResponse)
async def create_scan(db: Session = Depends(get_db)):
    """Create a new scan session"""
    try:
        scan = Scan()
        db.add(scan)
        db.commit()
        db.refresh(scan)
        
        logger.info(f"Created scan: {scan.scan_id}")
        return ScanResponse(
            scan_id=scan.scan_id,
            created_at=scan.created_at,
            images=[],
            compliance_result=None
        )
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_image(
    scan_id: str = Query(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload image to a scan session"""
    ensure_upload_dir()
    
    try:
        # Validate file
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        is_valid, error_msg = image_processor.validate_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Get or create scan
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Save original image
        image_id = str(uuid.uuid4())
        original_path = f"{settings.upload_dir}/originals/{image_id}_{file.filename}"
        
        with open(original_path, "wb") as f:
            f.write(content)
        
        # Validate image
        is_valid_img, error_img = image_processor.validate_image(original_path)
        if not is_valid_img:
            os.remove(original_path)
            raise HTTPException(status_code=400, detail=error_img)
        
        # Get image dimensions
        width, height = image_processor.get_image_dimensions(original_path)
        
        # Process image
        processed_path = f"{settings.upload_dir}/processed/{image_id}_processed.jpg"
        success, error_proc, metadata = image_processor.process_image(original_path, processed_path)
        if not success:
            os.remove(original_path)
            raise HTTPException(status_code=500, detail=error_proc)
        
        # Save to database
        db_image = Image(
            image_id=image_id,
            scan_id=scan.id,
            filename=file.filename,
            file_path=processed_path,
            file_size=file_size,
            mime_type=file.content_type,
            width=width,
            height=height
        )
        db.add(db_image)
        db.commit()
        db.refresh(db_image)
        
        logger.info(f"Uploaded image: {image_id}")
        
        return UploadResponse(
            scan_id=scan_id,
            image_id=image_id,
            message="Image uploaded successfully"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/extract")
async def extract_fields(
    scan_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Extract fields from all images in a scan"""
    try:
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        images = db.query(Image).filter(Image.scan_id == scan.id).all()
        if not images:
            raise HTTPException(status_code=400, detail="No images in scan")
        
        all_extracted_fields = {}
        
        for db_image in images:
            # Run OCR
            success, ocr_result, error = ocr_service.extract_text(db_image.file_path)
            if not success:
                logger.warning(f"OCR failed for image {db_image.image_id}: {error}")
                continue
            
            # Save OCR result
            ocr_db = OCRResult(
                image_id=db_image.id,
                text_blocks=ocr_result.get("text_blocks", []),
                raw_text=ocr_result.get("raw_text", ""),
                confidence_avg=ocr_result.get("confidence_avg", 0.0),
                processing_time_ms=ocr_result.get("processing_time_ms", 0)
            )
            db.add(ocr_db)
            db.commit()
            
            # Extract fields
            extracted = field_extractor.extract_fields(ocr_result.get("text_blocks", []))
            
            # Save extracted fields
            for field_name, field_data in extracted.items():
                db_field = ExtractedField(
                    image_id=db_image.id,
                    field_name=field_name,
                    extracted_value=field_data.value,
                    confidence=field_data.confidence,
                    source_text=field_data.source_text,
                    bounding_box=field_data.bbox,
                    extraction_method=field_data.extraction_method
                )
                db.add(db_field)
                
                # Track for compliance check
                if field_name not in all_extracted_fields:
                    all_extracted_fields[field_name] = field_data
            
            db.commit()
        
        logger.info(f"Extracted fields for scan {scan_id}")
        
        return {
            "scan_id": scan_id,
            "message": f"Fields extracted from {len(images)} image(s)",
            "extracted_fields": {k: v.to_dict() for k, v in all_extracted_fields.items()}
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error extracting fields: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/compliance/check")
async def check_compliance(
    scan_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """Check compliance for a scan"""
    try:
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        # Get all extracted fields for this scan
        extracted_fields_db = db.query(ExtractedField).join(
            Image, ExtractedField.image_id == Image.id
        ).filter(Image.scan_id == scan.id).all()
        
        # Convert to dict for compliance engine
        extracted_dict = {}
        for field in extracted_fields_db:
            if field.field_name not in extracted_dict:
                extracted_dict[field.field_name] = {
                    "value": field.extracted_value,
                    "confidence": field.confidence or 0.0,
                    "source_text": field.source_text,
                    "bbox": field.bounding_box
                }
        
        # Check compliance
        compliance_result = compliance_engine.check_compliance(extracted_dict)
        
        # Save compliance result
        result_id = str(uuid.uuid4())
        db_result = ComplianceResult(
            result_id=result_id,
            scan_id=scan.id,
            rules_version=compliance_result.get("rules_version", "2026"),
            compliance_checks=compliance_result.get("compliance_checks", []),
            overall_status=compliance_result.get("overall_status", "needs_review"),
            summary=compliance_result.get("summary", "")
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        
        logger.info(f"Compliance check completed for scan {scan_id}")
        
        return {
            "result_id": result_id,
            "scan_id": scan_id,
            "rules_version": compliance_result.get("rules_version"),
            "compliance_checks": compliance_result.get("compliance_checks"),
            "overall_status": compliance_result.get("overall_status"),
            "summary": compliance_result.get("summary"),
            "disclaimer": compliance_result.get("disclaimer", "")
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error checking compliance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/scan/{scan_id}")
async def get_scan(scan_id: str, db: Session = Depends(get_db)):
    """Get detailed scan results"""
    try:
        scan = db.query(Scan).filter(Scan.scan_id == scan_id).first()
        if not scan:
            raise HTTPException(status_code=404, detail="Scan not found")
        
        images = db.query(Image).filter(Image.scan_id == scan.id).all()
        compliance_result = db.query(ComplianceResult).filter(
            ComplianceResult.scan_id == scan.id
        ).first()
        
        # Build detailed result
        image_details = []
        for image in images:
            ocr_results = db.query(OCRResult).filter(
                OCRResult.image_id == image.id
            ).all()
            extracted_fields = db.query(ExtractedField).filter(
                ExtractedField.image_id == image.id
            ).all()
            
            image_details.append({
                "image_id": image.image_id,
                "filename": image.filename,
                "file_size": image.file_size,
                "width": image.width,
                "height": image.height,
                "ocr_results": [
                    {
                        "text_blocks": ocr.text_blocks,
                        "raw_text": ocr.raw_text,
                        "confidence_avg": ocr.confidence_avg
                    }
                    for ocr in ocr_results
                ],
                "extracted_fields": [
                    {
                        "field_name": field.field_name,
                        "value": field.extracted_value,
                        "confidence": field.confidence,
                        "source_text": field.source_text,
                        "bbox": field.bounding_box,
                        "extraction_method": field.extraction_method
                    }
                    for field in extracted_fields
                ]
            })
        
        compliance_data = None
        if compliance_result:
            compliance_data = {
                "result_id": compliance_result.result_id,
                "rules_version": compliance_result.rules_version,
                "compliance_checks": compliance_result.compliance_checks,
                "overall_status": compliance_result.overall_status,
                "summary": compliance_result.summary
            }
        
        return {
            "scan_id": scan_id,
            "created_at": scan.created_at,
            "images": image_details,
            "compliance_result": compliance_data
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving scan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{image_id}")
async def get_image(image_id: str, db: Session = Depends(get_db)):
    """Get processed image file"""
    try:
        image = db.query(Image).filter(Image.image_id == image_id).first()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        if not os.path.exists(image.file_path):
            raise HTTPException(status_code=404, detail="Image file not found on disk")
        
        # Return file using FileResponse
        from fastapi.responses import FileResponse
        return FileResponse(
            image.file_path,
            media_type="image/jpeg",
            filename=image.filename
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving image: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}
