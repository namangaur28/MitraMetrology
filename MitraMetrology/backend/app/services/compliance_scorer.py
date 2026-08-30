"""
Preliminary compliance scoring system
Generates AI-based preliminary score (NOT a legal determination)
"""
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class ComplianceScorer:
    """Generate preliminary compliance scores"""
    
    def __init__(self):
        # Maximum points for each category
        self.MANDATORY_DECLARATIONS_MAX = 40
        self.TEXT_READABILITY_MAX = 20
        self.INFORMATION_EXTRACTION_MAX = 25
        self.DATA_CONSISTENCY_MAX = 15
        self.TOTAL_MAX = 100
        
        # Mandatory fields and their weights
        self.MANDATORY_FIELDS = {
            "product_name": 10,
            "manufacturer": 10,
            "net_quantity": 10,
            "mrp": 10
        }
    
    def calculate_score(self, findings: List[Dict[str, Any]], 
                       readability_metrics: Dict[str, float],
                       conflict_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate preliminary compliance score
        
        Returns:
        {
            "overall_score": 0-100,
            "categories": {
                "mandatory_declarations": 0-40,
                "text_readability": 0-20,
                "information_extraction": 0-25,
                "data_consistency": 0-15
            },
            "is_preliminary": true,
            "is_legal_determination": false,
            "score_breakdown": {...},
            "recommendations": [...]
        }
        """
        
        # Score each category
        mandatory_score = self._score_mandatory_declarations(findings)
        readability_score = self._score_text_readability(readability_metrics)
        extraction_score = self._score_information_extraction(findings)
        consistency_score = self._score_data_consistency(conflict_data)
        
        # Calculate overall
        overall_score = (mandatory_score + readability_score + extraction_score + consistency_score)
        
        # Ensure within 0-100
        overall_score = min(100, max(0, overall_score))
        
        return {
            "overall_score": overall_score,
            "categories": {
                "mandatory_declarations": mandatory_score,
                "text_readability": readability_score,
                "information_extraction": extraction_score,
                "data_consistency": consistency_score
            },
            "is_preliminary": True,
            "is_legal_determination": False,
            "score_details": self._generate_score_details(
                findings, readability_metrics, conflict_data,
                mandatory_score, readability_score, extraction_score, consistency_score
            ),
            "interpretation": self._interpret_score(overall_score),
            "disclaimer": (
                "This is an AI-generated PRELIMINARY score only. "
                "It does NOT constitute an official legal compliance determination. "
                "A qualified legal metrology officer must verify the actual product."
            ),
            "next_steps": self._recommend_next_steps(overall_score, findings)
        }
    
    def _score_mandatory_declarations(self, findings: List[Dict[str, Any]]) -> float:
        """Score mandatory field declarations (0-40 points)"""
        score = 0
        
        # Track which mandatory fields are detected
        detected_fields = set()
        
        for finding in findings:
            if finding.get("status") == "detected" and finding.get("field_name") in self.MANDATORY_FIELDS:
                detected_fields.add(finding["field_name"])
        
        # Award points for detected mandatory fields
        for field, points in self.MANDATORY_FIELDS.items():
            if field in detected_fields:
                score += points
        
        # Deduct for critical missing fields
        missing_count = len(self.MANDATORY_FIELDS) - len(detected_fields)
        if missing_count > 0:
            penalty = missing_count * 5
            score = max(0, score - penalty)
        
        return min(self.MANDATORY_DECLARATIONS_MAX, score)
    
    def _score_text_readability(self, readability_metrics: Dict[str, float]) -> float:
        """Score text readability (0-20 points)"""
        if not readability_metrics:
            return 0
        
        avg_readability = readability_metrics.get("average_readability_score", 0)
        
        # Convert readability score (0-100) to category score (0-20)
        # Mapping: 0-40 = 0-5 points, 40-70 = 5-15 points, 70-100 = 15-20 points
        if avg_readability < 40:
            return min(5, avg_readability / 8)
        elif avg_readability < 70:
            return 5 + (avg_readability - 40) * 0.33
        else:
            return 15 + (avg_readability - 70) * 0.2
    
    def _score_information_extraction(self, findings: List[Dict[str, Any]]) -> float:
        """Score information extraction quality (0-25 points)"""
        total_findings = len(findings)
        if total_findings == 0:
            return 0
        
        # Count by status
        detected_count = sum(1 for f in findings if f.get("status") == "detected")
        violation_count = sum(1 for f in findings if f.get("status") == "potential_violation")
        review_count = sum(1 for f in findings if f.get("status") == "needs_review")
        
        # Calculate score
        detection_rate = detected_count / total_findings if total_findings > 0 else 0
        violation_rate = violation_count / total_findings if total_findings > 0 else 0
        
        # Detected fields are good, violations are bad
        score = (detection_rate * 25) - (violation_rate * 10)
        
        return min(25, max(0, score))
    
    def _score_data_consistency(self, conflict_data: Dict[str, Any]) -> float:
        """Score data consistency across images (0-15 points)"""
        if not conflict_data:
            return self.DATA_CONSISTENCY_MAX  # Full points if no conflicts to detect
        
        has_conflicts = conflict_data.get("has_conflicts", False)
        
        if not has_conflicts:
            return self.DATA_CONSISTENCY_MAX  # Full points for consistent data
        
        # Deduct points for conflicts
        inconsistent_fields = len(conflict_data.get("inconsistent_fields", []))
        
        # Each inconsistent field loses 3 points
        penalty = inconsistent_fields * 3
        score = self.DATA_CONSISTENCY_MAX - penalty
        
        return max(0, min(self.DATA_CONSISTENCY_MAX, score))
    
    def _generate_score_details(self, findings: List[Dict], readability: Dict,
                               conflicts: Dict, mandatory: float, readability_score: float,
                               extraction: float, consistency: float) -> Dict[str, Any]:
        """Generate detailed breakdown of scoring"""
        return {
            "mandatory_declarations": {
                "score": mandatory,
                "max_points": self.MANDATORY_DECLARATIONS_MAX,
                "details": self._details_mandatory(findings),
                "weight": "40%"
            },
            "text_readability": {
                "score": readability_score,
                "max_points": self.TEXT_READABILITY_MAX,
                "average_score": readability.get("average_readability_score", 0),
                "weight": "20%"
            },
            "information_extraction": {
                "score": extraction,
                "max_points": self.INFORMATION_EXTRACTION_MAX,
                "detected_fields": sum(1 for f in findings if f.get("status") == "detected"),
                "weight": "25%"
            },
            "data_consistency": {
                "score": consistency,
                "max_points": self.DATA_CONSISTENCY_MAX,
                "conflicts_found": conflicts.get("has_conflicts", False),
                "weight": "15%"
            }
        }
    
    def _details_mandatory(self, findings: List[Dict]) -> Dict[str, bool]:
        """Detail which mandatory fields were found"""
        return {
            field: any(f.get("field_name") == field and f.get("status") == "detected" 
                      for f in findings)
            for field in self.MANDATORY_FIELDS.keys()
        }
    
    def _interpret_score(self, score: float) -> str:
        """Interpret what the score means"""
        if score >= 85:
            return (
                "HIGH COMPLIANCE LIKELIHOOD: All or most mandatory declarations detected "
                "with good readability and consistency. Likely meets Legal Metrology requirements. "
                "Still requires human verification."
            )
        elif score >= 70:
            return (
                "MODERATE COMPLIANCE: Most mandatory fields detected. Some minor issues may exist. "
                "Requires human inspection for final determination."
            )
        elif score >= 50:
            return (
                "LOW COMPLIANCE: Several issues detected. Important information may be missing. "
                "Detailed inspection required."
            )
        else:
            return (
                "POTENTIAL NON-COMPLIANCE: Multiple critical issues detected. "
                "Immediate inspection recommended."
            )
    
    def _recommend_next_steps(self, score: float, findings: List[Dict]) -> List[str]:
        """Generate recommendations based on score"""
        recommendations = []
        
        if score < 50:
            recommendations.append("REQUEST INSPECTION: Product appears to have compliance issues.")
        elif score < 70:
            recommendations.append("HUMAN VERIFICATION: Score suggests need for detailed inspection.")
        else:
            recommendations.append("GOOD INITIAL ASSESSMENT: Proceed with standard verification process.")
        
        # Add specific field recommendations
        critical_missing = [f for f in findings if f.get("status") == "potential_violation" and f.get("severity") == "critical"]
        if critical_missing:
            fields = ", ".join(set(f.get("field_name") for f in critical_missing))
            recommendations.append(f"VERIFY MISSING FIELDS: {fields}")
        
        readability_issues = [f for f in findings if f.get("field_name") == "text_readability" and f.get("status") == "needs_review"]
        if readability_issues:
            recommendations.append("IMPROVE IMAGE QUALITY: Provide clearer photographs for better analysis.")
        
        conflicts = [f for f in findings if f.get("rule_id") == "LM-010"]
        if conflicts:
            recommendations.append("RESOLVE CONFLICTS: Determine correct values from conflicting image data.")
        
        return recommendations


# Singleton instance
compliance_scorer = ComplianceScorer()
