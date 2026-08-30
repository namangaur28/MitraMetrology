"""
Explainable AI engine for generating evidence-based findings
Implements WHAT, WHY, WHICH, WHERE, HOW framework
"""
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class Evidence:
    """Evidence for a finding"""
    type: str  # 'image', 'text', 'metric', 'comparison'
    location: Optional[Dict[str, float]]  # {"image_id": "...", "bbox": [x1, y1, x2, y2]}
    content: str  # What was found
    confidence: float  # 0-1
    source: str  # 'ocr', 'field_extraction', 'quality_check', 'cross_image'


@dataclass
class Finding:
    """AI-generated finding with full explainability"""
    finding_id: str
    rule_id: str
    field_name: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    status: str  # 'detected', 'potential_violation', 'needs_review'
    
    # The 5 W's of explainability
    what_detected: str  # WHAT: What exactly was detected
    why_flagged: str  # WHY: Why was it flagged
    rule_reference: str  # WHICH: Which rule applies
    where_in_image: List[Evidence]  # WHERE: Where in the image(s)
    confidence_score: float  # HOW: How confident (0-100)
    
    # Additional context
    context: Dict[str, Any]  # Any additional context
    created_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "finding_id": self.finding_id,
            "rule_id": self.rule_id,
            "field_name": self.field_name,
            "severity": self.severity,
            "status": self.status,
            "what_detected": self.what_detected,
            "why_flagged": self.why_flagged,
            "rule_reference": self.rule_reference,
            "where_in_image": [
                {
                    "type": e.type,
                    "location": e.location,
                    "content": e.content,
                    "confidence": e.confidence,
                    "source": e.source
                }
                for e in self.where_in_image
            ],
            "confidence_score": self.confidence_score,
            "context": self.context,
            "created_at": self.created_at
        }


class ExplainabilityEngine:
    """Generate explainable AI findings with evidence"""
    
    def __init__(self):
        self.rule_explanations = {
            "LM-001": "Product name must be clearly displayed for consumer identification",
            "LM-002": "MRP display is mandatory for consumer protection and price transparency",
            "LM-003": "Net quantity in SI units is required for accurate measurement verification",
            "LM-004": "Manufacturer details are required for consumer recourse and accountability",
            "LM-005": "Consumer care instructions help ensure safe product usage",
            "LM-006": "Packer details must be shown if different from manufacturer",
            "LM-007": "Importer details are required for imported goods traceability",
            "LM-008": "Manufacturing date helps track product freshness",
            "LM-009": "Text must be readable for consumer understanding",
            "LM-010": "Information across images must be consistent for accuracy"
        }
    
    def generate_missing_field_finding(self, field_name: str, rule_id: str, severity: str,
                                      searched_images: List[str], search_confidence: float) -> Finding:
        """Generate finding for missing field"""
        finding_id = f"FND-{datetime.now().timestamp()}"
        
        what_detected = f"{field_name} declaration could not be confidently detected in any image."
        why_flagged = f"The {field_name} is required by regulations but was not found in the scanned images."
        rule_ref = self.rule_explanations.get(rule_id, f"Rule {rule_id}")
        
        finding = Finding(
            finding_id=finding_id,
            rule_id=rule_id,
            field_name=field_name,
            severity=severity,
            status="potential_violation" if severity in ["critical", "high"] else "needs_review",
            what_detected=what_detected,
            why_flagged=why_flagged,
            rule_reference=rule_ref,
            where_in_image=[],  # Nothing detected
            confidence_score=100 - search_confidence,  # Confidence in detection failure
            context={
                "images_searched": len(searched_images),
                "search_confidence": search_confidence
            },
            created_at=datetime.now().isoformat()
        )
        
        return finding
    
    def generate_detected_finding(self, field_name: str, value: str, rule_id: str,
                                 image_id: str, bbox: List[float], ocr_confidence: float,
                                 normalized_value: Optional[str] = None) -> Finding:
        """Generate finding for successfully detected field"""
        finding_id = f"FND-{datetime.now().timestamp()}"
        
        display_value = normalized_value or value
        what_detected = f"{field_name.replace('_', ' ').title()}: {display_value}"
        why_flagged = f"{field_name.replace('_', ' ')} was successfully detected and extracted."
        rule_ref = self.rule_explanations.get(rule_id, f"Rule {rule_id}")
        
        evidence = Evidence(
            type="image",
            location={"image_id": image_id, "bbox": bbox},
            content=value,
            confidence=ocr_confidence,
            source="ocr"
        )
        
        finding = Finding(
            finding_id=finding_id,
            rule_id=rule_id,
            field_name=field_name,
            severity="low",  # Not a violation
            status="detected",
            what_detected=what_detected,
            why_flagged=why_flagged,
            rule_reference=rule_ref,
            where_in_image=[evidence],
            confidence_score=int(ocr_confidence * 100),
            context={
                "value_normalized": normalized_value is not None,
                "original_value": value
            },
            created_at=datetime.now().isoformat()
        )
        
        return finding
    
    def generate_conflict_finding(self, field_name: str, image_conflicts: Dict[str, Any]) -> Finding:
        """Generate finding for conflicting values across images"""
        finding_id = f"FND-{datetime.now().timestamp()}"
        
        values_str = ", ".join([f"{img}: {val}" for img, val in image_conflicts.get("conflicting_values", {}).items()])
        
        what_detected = f"Conflicting values for {field_name} detected: {values_str}"
        why_flagged = "Same field has different values across images, indicating potential data inconsistency or labeling error."
        rule_ref = "LM-010: Data Consistency Across Images"
        
        evidence_list = []
        for img_id, value in image_conflicts.get("conflicting_values", {}).items():
            evidence_list.append(Evidence(
                type="comparison",
                location={"image_id": img_id},
                content=value,
                confidence=image_conflicts.get("confidence", {}).get(img_id, 0.5),
                source="comparison"
            ))
        
        finding = Finding(
            finding_id=finding_id,
            rule_id="LM-010",
            field_name=field_name,
            severity="high",
            status="needs_review",
            what_detected=what_detected,
            why_flagged=why_flagged,
            rule_reference=rule_ref,
            where_in_image=evidence_list,
            confidence_score=image_conflicts.get("conflict_score", 50),
            context={
                "conflicting_images": list(image_conflicts.get("conflicting_values", {}).keys()),
                "conflict_type": "value_mismatch"
            },
            created_at=datetime.now().isoformat()
        )
        
        return finding
    
    def generate_readability_finding(self, image_id: str, readability_score: float,
                                    issues: List[str]) -> Optional[Finding]:
        """Generate finding for readability issues"""
        if readability_score >= 70:  # Good readability
            return None
        
        finding_id = f"FND-{datetime.now().timestamp()}"
        
        severity = "critical" if readability_score < 40 else "high"
        what_detected = f"Image readability score: {readability_score}/100. Issues: {', '.join(issues)}"
        why_flagged = "Poor readability may affect OCR accuracy and compliance assessment reliability."
        rule_ref = "LM-009: Text Readability and Visibility"
        
        evidence = Evidence(
            type="metric",
            location={"image_id": image_id},
            content=f"Readability: {readability_score}/100",
            confidence=1.0,
            source="quality_check"
        )
        
        finding = Finding(
            finding_id=finding_id,
            rule_id="LM-009",
            field_name="text_readability",
            severity=severity,
            status="needs_review",
            what_detected=what_detected,
            why_flagged=why_flagged,
            rule_reference=rule_ref,
            where_in_image=[evidence],
            confidence_score=readability_score,
            context={
                "readability_issues": issues,
                "recommendation": "Please provide clearer image for better analysis"
            },
            created_at=datetime.now().isoformat()
        )
        
        return finding
    
    def generate_format_error_finding(self, field_name: str, rule_id: str, value: str,
                                     image_id: str, bbox: List[float], expected_format: str) -> Finding:
        """Generate finding for format errors"""
        finding_id = f"FND-{datetime.now().timestamp()}"
        
        what_detected = f"{field_name.title()} detected but format may be incorrect: '{value}'"
        why_flagged = f"Expected format: {expected_format}. This may indicate a malformed or non-standard declaration."
        rule_ref = self.rule_explanations.get(rule_id, f"Rule {rule_id}")
        
        evidence = Evidence(
            type="image",
            location={"image_id": image_id, "bbox": bbox},
            content=value,
            confidence=0.6,
            source="ocr"
        )
        
        finding = Finding(
            finding_id=finding_id,
            rule_id=rule_id,
            field_name=field_name,
            severity="high",
            status="needs_review",
            what_detected=what_detected,
            why_flagged=why_flagged,
            rule_reference=rule_ref,
            where_in_image=[evidence],
            confidence_score=60,
            context={
                "expected_format": expected_format,
                "actual_value": value
            },
            created_at=datetime.now().isoformat()
        )
        
        return finding
    
    def generate_summary_report(self, findings: List[Finding]) -> Dict[str, Any]:
        """Generate summary report from findings"""
        critical_count = sum(1 for f in findings if f.severity == "critical")
        high_count = sum(1 for f in findings if f.severity == "high")
        medium_count = sum(1 for f in findings if f.severity == "medium")
        
        detected_count = sum(1 for f in findings if f.status == "detected")
        violations_count = sum(1 for f in findings if f.status == "potential_violation")
        review_count = sum(1 for f in findings if f.status == "needs_review")
        
        return {
            "total_findings": len(findings),
            "by_severity": {
                "critical": critical_count,
                "high": high_count,
                "medium": medium_count
            },
            "by_status": {
                "detected": detected_count,
                "potential_violation": violations_count,
                "needs_review": review_count
            },
            "overall_assessment": self._determine_overall_assessment(findings),
            "key_findings": [f.to_dict() for f in findings[:5]],  # Top 5
            "recommendations": self._generate_recommendations(findings)
        }
    
    def _determine_overall_assessment(self, findings: List[Finding]) -> str:
        """Determine overall compliance assessment"""
        if any(f.severity == "critical" and f.status == "potential_violation" for f in findings):
            return "potential_non_compliance"
        elif any(f.severity == "high" and f.status in ["potential_violation", "needs_review"] for f in findings):
            return "needs_human_verification"
        else:
            return "potentially_compliant"
    
    def _generate_recommendations(self, findings: List[Finding]) -> List[str]:
        """Generate recommendations based on findings"""
        recommendations = []
        
        critical_findings = [f for f in findings if f.severity == "critical"]
        if critical_findings:
            recommendations.append(
                f"Critical: {len(critical_findings)} mandatory declaration(s) missing. Requires immediate inspection."
            )
        
        readability_findings = [f for f in findings if f.field_name == "text_readability"]
        if readability_findings:
            recommendations.append(
                "Image quality issues detected. Please provide clearer photographs for accurate compliance assessment."
            )
        
        conflict_findings = [f for f in findings if f.rule_id == "LM-010"]
        if conflict_findings:
            recommendations.append(
                "Conflicting information detected across images. Please verify which image shows correct information."
            )
        
        if not recommendations:
            recommendations.append(
                "All detected information appears consistent. Proceed with human verification."
            )
        
        return recommendations


# Singleton instance
explainability_engine = ExplainabilityEngine()
