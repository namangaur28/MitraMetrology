"""
Compliance rules engine for checking packaged commodity regulations
"""
import json
import os
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ComplianceCheck:
    """Result of a single compliance check"""
    rule_id: str
    field: str
    name: str
    status: str  # 'pass', 'flag', 'missing', 'needs_review'
    details: str
    confidence: Optional[float] = None


class ComplianceEngine:
    """Evaluates compliance based on versioned rules"""
    
    def __init__(self):
        self.rules_cache = {}
        self._load_rules("2026")
    
    def _load_rules(self, version: str):
        """Load rules from JSON file"""
        try:
            rules_path = os.path.join(
                os.path.dirname(__file__),
                "..",
                "rules",
                version,
                "packaged_commodities_rules.json"
            )
            
            if os.path.exists(rules_path):
                with open(rules_path, 'r') as f:
                    self.rules_cache[version] = json.load(f)
                logger.info(f"Loaded rules version {version}")
            else:
                logger.warning(f"Rules file not found: {rules_path}")
        except Exception as e:
            logger.error(f"Error loading rules: {str(e)}")
    
    def check_compliance(self, extracted_fields: Dict[str, Any], version: str = "2026") -> Dict[str, Any]:
        """
        Check compliance based on extracted fields
        
        extracted_fields: Dict of field_name -> ExtractedField
        Returns: Dict with compliance results
        """
        if version not in self.rules_cache:
            self._load_rules(version)
        
        if version not in self.rules_cache:
            return {
                "result_id": "",
                "rules_version": version,
                "compliance_checks": [],
                "overall_status": "needs_review",
                "summary": "Rules not available for this version"
            }
        
        rules = self.rules_cache[version]
        checks = []
        
        # Evaluate each rule
        for rule in rules.get("rules", []):
            check = self._evaluate_rule(rule, extracted_fields)
            checks.append(check)
        
        # Determine overall status
        overall_status = self._determine_overall_status(checks, rules)
        
        # Generate summary
        summary = self._generate_summary(checks)
        
        return {
            "rules_version": version,
            "compliance_checks": [
                {
                    "rule_id": check.rule_id,
                    "field": check.field,
                    "name": check.name,
                    "status": check.status,
                    "details": check.details,
                    "confidence": check.confidence
                }
                for check in checks
            ],
            "overall_status": overall_status,
            "summary": summary,
            "disclaimer": ". ".join(rules.get("disclaimers", []))
        }
    
    def _evaluate_rule(self, rule: Dict[str, Any], extracted_fields: Dict[str, Any]) -> ComplianceCheck:
        """Evaluate a single rule"""
        field_name = rule.get("field")
        
        # Get extracted field
        field_value = None
        confidence = 0.0
        
        if field_name in extracted_fields:
            field_data = extracted_fields[field_name]
            # Handle both dict and object with .to_dict()
            if hasattr(field_data, 'to_dict'):
                field_data = field_data.to_dict()
            
            field_value = field_data.get("value")
            confidence = field_data.get("confidence", 0.0)
        
        # Check based on rule type
        check_type = rule.get("check_type", "presence")
        mandatory = rule.get("mandatory", False)
        min_confidence = rule.get("min_confidence", 0.0)
        
        if check_type == "presence":
            if field_value:
                status = "pass"
                details = f"{field_value} detected (confidence: {confidence:.0%})"
            else:
                if mandatory:
                    status = "flag"
                    details = "Mandatory field not detected"
                else:
                    status = "needs_review"
                    details = "Field not detected - may need verification"
        else:
            status = "needs_review"
            details = "Advanced compliance check not yet implemented"
        
        return ComplianceCheck(
            rule_id=rule.get("rule_id"),
            field=field_name,
            name=rule.get("name"),
            status=status,
            details=details,
            confidence=confidence
        )
    
    def _determine_overall_status(self, checks: List[ComplianceCheck], rules: Dict[str, Any]) -> str:
        """Determine overall compliance status"""
        statuses = [check.status for check in checks]
        
        # If any mandatory flag exists, overall is flag
        mandatory_rules = [r for r in rules.get("rules", []) if r.get("mandatory", False)]
        mandatory_fields = [r.get("field") for r in mandatory_rules]
        
        for check in checks:
            if check.field in mandatory_fields and check.status == "flag":
                return "flag"
        
        # If any needs_review, overall is needs_review
        if "needs_review" in statuses:
            return "needs_review"
        
        # If all pass, overall is pass
        if all(s == "pass" for s in statuses):
            return "pass"
        
        # Default to needs_review
        return "needs_review"
    
    def _generate_summary(self, checks: List[ComplianceCheck]) -> str:
        """Generate human-readable summary"""
        pass_count = sum(1 for c in checks if c.status == "pass")
        flag_count = sum(1 for c in checks if c.status == "flag")
        review_count = sum(1 for c in checks if c.status == "needs_review")
        
        summary_parts = []
        
        if pass_count > 0:
            summary_parts.append(f"✓ {pass_count} field(s) detected")
        
        if flag_count > 0:
            summary_parts.append(f"✕ {flag_count} mandatory field(s) missing")
        
        if review_count > 0:
            summary_parts.append(f"⚠ {review_count} field(s) need review")
        
        summary = " | ".join(summary_parts) if summary_parts else "No compliance checks performed"
        
        summary += "\n\nIMPORTANT: This is an AI-assisted preliminary assessment. "
        summary += "All results must be verified by authorized enforcement officers."
        
        return summary


# Singleton instance
compliance_engine = ComplianceEngine()
