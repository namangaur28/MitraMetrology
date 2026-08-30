"""
Audit logging service for immutable compliance audit trail
"""
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from app.models import Scan

logger = logging.getLogger(__name__)


class AuditLogger:
    """Log audit events immutably"""
    
    def __init__(self):
        self.ACTIONS = {
            "scan_created": "Scan session created",
            "image_uploaded": "Image uploaded to scan",
            "ocr_completed": "OCR analysis completed",
            "fields_extracted": "Fields extracted from OCR",
            "findings_generated": "Compliance findings generated",
            "score_calculated": "Compliance score calculated",
            "report_generated": "Report generated",
            "finding_verified": "Finding verified by inspector",
            "finding_overridden": "AI finding overridden by inspector",
            "scan_completed": "Scan analysis completed",
            "conflict_detected": "Conflict detected across images",
            "duplicate_detected": "Duplicate/similar image detected"
        }
    
    def log_event(self, scan_id: str, action: str, entity_type: str, 
                 entity_id: str, details: Optional[Dict[str, Any]] = None,
                 user: Optional[str] = None) -> bool:
        """
        Log an audit event
        This should be saved to database as immutable record
        
        Returns: True if logged successfully
        """
        try:
            event = {
                "timestamp": datetime.utcnow().isoformat(),
                "scan_id": scan_id,
                "action": action,
                "action_description": self.ACTIONS.get(action, "Unknown action"),
                "entity_type": entity_type,
                "entity_id": entity_id,
                "details": details or {},
                "user": user or "system",
                "immutable": True  # Mark as immutable
            }
            
            # In production, this would be saved to database
            # db_session.add(AuditLog(**event))
            # db_session.commit()
            
            logger.info(f"AUDIT: {action} | Scan: {scan_id} | Entity: {entity_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error logging audit event: {str(e)}")
            return False
    
    def generate_audit_trail(self, scan_id: str) -> Dict[str, Any]:
        """
        Generate audit trail for a scan
        Shows all actions taken during compliance inspection
        """
        audit_trail = {
            "scan_id": scan_id,
            "timeline": [
                # These would be retrieved from database
                # {
                #     "timestamp": "...",
                #     "action": "scan_created",
                #     "details": {...}
                # },
                # ...
            ],
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return audit_trail
    
    def log_scan_created(self, scan_id: str, user: Optional[str] = None) -> bool:
        """Log scan creation"""
        return self.log_event(
            scan_id=scan_id,
            action="scan_created",
            entity_type="scan",
            entity_id=scan_id,
            user=user,
            details={"status": "initiated"}
        )
    
    def log_image_uploaded(self, scan_id: str, image_id: str, 
                          file_size: int, user: Optional[str] = None) -> bool:
        """Log image upload"""
        return self.log_event(
            scan_id=scan_id,
            action="image_uploaded",
            entity_type="image",
            entity_id=image_id,
            user=user,
            details={"file_size": file_size}
        )
    
    def log_ocr_completed(self, scan_id: str, image_id: str, 
                         text_confidence: float, user: Optional[str] = None) -> bool:
        """Log OCR completion"""
        return self.log_event(
            scan_id=scan_id,
            action="ocr_completed",
            entity_type="ocr_result",
            entity_id=image_id,
            user=user,
            details={"text_confidence": text_confidence}
        )
    
    def log_fields_extracted(self, scan_id: str, image_id: str,
                            fields_count: int, user: Optional[str] = None) -> bool:
        """Log field extraction"""
        return self.log_event(
            scan_id=scan_id,
            action="fields_extracted",
            entity_type="extracted_fields",
            entity_id=image_id,
            user=user,
            details={"fields_extracted": fields_count}
        )
    
    def log_findings_generated(self, scan_id: str, findings_count: int,
                              findings_by_severity: Dict[str, int],
                              user: Optional[str] = None) -> bool:
        """Log finding generation"""
        return self.log_event(
            scan_id=scan_id,
            action="findings_generated",
            entity_type="findings",
            entity_id=scan_id,
            user=user,
            details={
                "findings_count": findings_count,
                "by_severity": findings_by_severity
            }
        )
    
    def log_score_calculated(self, scan_id: str, score: float,
                            user: Optional[str] = None) -> bool:
        """Log score calculation"""
        return self.log_event(
            scan_id=scan_id,
            action="score_calculated",
            entity_type="compliance_score",
            entity_id=scan_id,
            user=user,
            details={"score": score}
        )
    
    def log_report_generated(self, scan_id: str, report_id: str,
                            report_format: str, user: Optional[str] = None) -> bool:
        """Log report generation"""
        return self.log_event(
            scan_id=scan_id,
            action="report_generated",
            entity_type="compliance_report",
            entity_id=report_id,
            user=user,
            details={"format": report_format}
        )
    
    def log_finding_verified(self, scan_id: str, finding_id: str,
                            decision: str, comment: str = "",
                            inspector: str = "") -> bool:
        """Log finding verification"""
        return self.log_event(
            scan_id=scan_id,
            action="finding_verified",
            entity_type="finding",
            entity_id=finding_id,
            user=inspector,
            details={
                "decision": decision,
                "comment": comment,
                "verified_at": datetime.utcnow().isoformat()
            }
        )
    
    def log_finding_overridden(self, scan_id: str, finding_id: str,
                              original_status: str, new_status: str,
                              reason: str = "",
                              inspector: str = "") -> bool:
        """Log AI finding override"""
        return self.log_event(
            scan_id=scan_id,
            action="finding_overridden",
            entity_type="finding",
            entity_id=finding_id,
            user=inspector,
            details={
                "original_status": original_status,
                "new_status": new_status,
                "reason": reason,
                "overridden_at": datetime.utcnow().isoformat()
            }
        )
    
    def log_scan_completed(self, scan_id: str, overall_status: str,
                          user: Optional[str] = None) -> bool:
        """Log scan completion"""
        return self.log_event(
            scan_id=scan_id,
            action="scan_completed",
            entity_type="scan",
            entity_id=scan_id,
            user=user,
            details={
                "overall_status": overall_status,
                "completed_at": datetime.utcnow().isoformat()
            }
        )
    
    def log_conflict_detected(self, scan_id: str, field_name: str,
                             image_ids: list, user: Optional[str] = None) -> bool:
        """Log conflict detection"""
        return self.log_event(
            scan_id=scan_id,
            action="conflict_detected",
            entity_type="image_conflict",
            entity_id=scan_id,
            user=user,
            details={
                "field": field_name,
                "images_involved": image_ids
            }
        )
    
    def log_duplicate_detected(self, scan_id: str, image_1: str,
                              image_2: str, similarity: float,
                              user: Optional[str] = None) -> bool:
        """Log duplicate image detection"""
        return self.log_event(
            scan_id=scan_id,
            action="duplicate_detected",
            entity_type="image_duplicate",
            entity_id=scan_id,
            user=user,
            details={
                "image_1": image_1,
                "image_2": image_2,
                "similarity": similarity
            }
        )


# Singleton instance
audit_logger = AuditLogger()
