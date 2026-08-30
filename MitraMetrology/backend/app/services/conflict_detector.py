"""
Multi-image deduplication and conflict detection
Identifies duplicates and conflicting information across multiple images
"""
import logging
from typing import Dict, List, Optional, Tuple, Any
from app.services.text_normalizer import TextNormalizer, NormalizedQuantity, NormalizedPrice, NormalizedDate

logger = logging.getLogger(__name__)


class ConflictDetector:
    """Detect conflicts and duplicates across multiple images"""
    
    def __init__(self):
        self.normalizer = TextNormalizer()
        
        # Fields that should be consistent across all images
        self.fields_requiring_consistency = [
            "mrp",
            "net_quantity",
            "manufacturer",
            "product_name"
        ]
        
        # Fields that might differ (packer vs manufacturer)
        self.fields_allowing_variation = [
            "packer",
            "importer",
            "date"  # Different images might have different dates
        ]
    
    def detect_conflicts(self, multi_image_fields: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Detect conflicts in extracted fields across images
        
        multi_image_fields format:
        {
            "image_1": {
                "mrp": {"value": "₹100", "confidence": 0.95, ...},
                "net_quantity": {...},
                ...
            },
            "image_2": {...},
            ...
        }
        
        Returns:
        {
            "has_conflicts": bool,
            "conflicts": [
                {
                    "field": "mrp",
                    "images": ["image_1", "image_2"],
                    "values": {"image_1": "₹100", "image_2": "₹100"},
                    "conflict_type": "value_match" | "value_mismatch" | "format_inconsistency",
                    "severity": "high" | "medium" | "low",
                    "resolution": "consistent" | "conflicting"
                }
            ]
        }
        """
        conflicts = []
        has_conflicts = False
        
        # Organize fields by image
        fields_by_image = {}
        all_fields = set()
        
        for image_id, fields in multi_image_fields.items():
            fields_by_image[image_id] = fields
            all_fields.update(fields.keys())
        
        image_ids = list(multi_image_fields.keys())
        if len(image_ids) < 2:
            return {"has_conflicts": False, "conflicts": []}
        
        # Check each field across images
        for field_name in all_fields:
            if field_name in self.fields_requiring_consistency:
                conflict = self._check_field_consistency(
                    field_name, fields_by_image, image_ids
                )
                if conflict:
                    conflicts.append(conflict)
                    if conflict["resolution"] == "conflicting":
                        has_conflicts = True
        
        return {
            "has_conflicts": has_conflicts,
            "conflicts": conflicts,
            "total_images": len(image_ids),
            "inconsistent_fields": [c["field"] for c in conflicts if c["resolution"] == "conflicting"]
        }
    
    def _check_field_consistency(self, field_name: str, fields_by_image: Dict[str, Dict],
                                image_ids: List[str]) -> Optional[Dict[str, Any]]:
        """Check if a field is consistent across images"""
        field_values = {}
        confidence_levels = {}
        missing_in = []
        
        # Collect values from all images
        for image_id in image_ids:
            if image_id in fields_by_image and field_name in fields_by_image[image_id]:
                field_data = fields_by_image[image_id][field_name]
                field_values[image_id] = field_data.get("value") or field_data.get("raw_value")
                confidence_levels[image_id] = field_data.get("confidence", 0)
            else:
                missing_in.append(image_id)
        
        # If field not found in multiple images, don't report as conflict
        if len(field_values) < 2:
            return None
        
        # Compare field values
        is_consistent = self._values_are_consistent(field_name, field_values)
        
        if not is_consistent:
            return {
                "field": field_name,
                "images": list(field_values.keys()),
                "values": field_values,
                "confidence_levels": confidence_levels,
                "conflict_type": self._determine_conflict_type(field_name, field_values),
                "severity": "high",
                "resolution": "conflicting",
                "missing_in": missing_in if missing_in else None
            }
        else:
            # Consistent, but still report for verification
            return {
                "field": field_name,
                "images": list(field_values.keys()),
                "values": field_values,
                "confidence_levels": confidence_levels,
                "conflict_type": "value_match",
                "severity": "low",
                "resolution": "consistent",
                "missing_in": missing_in if missing_in else None
            }
    
    def _values_are_consistent(self, field_name: str, field_values: Dict[str, Any]) -> bool:
        """Check if values are consistent across images"""
        if len(field_values) < 2:
            return True
        
        values = list(field_values.values())
        first_value = values[0]
        
        # Field-specific comparison logic
        if field_name == "mrp":
            # Parse prices and compare numerically
            prices = []
            for val in values:
                price = self.normalizer.extract_and_normalize_price(val)
                if price:
                    prices.append(price)
            
            if len(prices) < 2:
                return True
            
            # Check if all prices match
            first_price = prices[0]
            return all(self.normalizer.compare_prices(first_price, p) for p in prices[1:])
        
        elif field_name == "net_quantity":
            # Parse quantities and compare numerically
            quantities = []
            for val in values:
                qty = self.normalizer.extract_and_normalize_quantity(val)
                if qty:
                    quantities.append(qty)
            
            if len(quantities) < 2:
                return True
            
            # Check if all quantities match
            first_qty = quantities[0]
            return all(self.normalizer.compare_quantities(first_qty, q) for q in quantities[1:])
        
        elif field_name in ["product_name", "manufacturer"]:
            # Normalize and compare text
            normalized_values = [
                self.normalizer.normalize_manufacturer_name(val).lower()
                for val in values
            ]
            return all(v == normalized_values[0] for v in normalized_values[1:])
        
        else:
            # Direct string comparison for other fields
            return all(v == first_value for v in values[1:])
    
    def _determine_conflict_type(self, field_name: str, field_values: Dict[str, Any]) -> str:
        """Determine the type of conflict"""
        values = list(field_values.values())
        
        if len(set(str(v).lower() for v in values)) == 1:
            return "value_match"
        
        # Check if it's just a format difference
        if field_name in ["mrp", "net_quantity"]:
            try:
                if field_name == "mrp":
                    prices = [self.normalizer.extract_and_normalize_price(v) for v in values]
                    if all(prices) and all(p.value == prices[0].value for p in prices):
                        return "format_inconsistency"
                elif field_name == "net_quantity":
                    qtys = [self.normalizer.extract_and_normalize_quantity(v) for v in values]
                    if all(qtys) and all(self.normalizer.compare_quantities(q, qtys[0]) for q in qtys):
                        return "format_inconsistency"
            except:
                pass
        
        return "value_mismatch"
    
    def detect_duplicate_images(self, image_ocr_results: Dict[str, str]) -> Dict[str, Any]:
        """
        Detect potential duplicate or near-duplicate images
        
        image_ocr_results: {"image_1": raw_ocr_text, "image_2": raw_ocr_text, ...}
        
        Returns duplicate information for review
        """
        duplicates = []
        similarity_threshold = 0.85
        
        image_ids = list(image_ocr_results.keys())
        
        for i, image_1 in enumerate(image_ids):
            for image_2 in image_ids[i+1:]:
                similarity = self._calculate_text_similarity(
                    image_ocr_results[image_1],
                    image_ocr_results[image_2]
                )
                
                if similarity > similarity_threshold:
                    duplicates.append({
                        "image_1": image_1,
                        "image_2": image_2,
                        "similarity": similarity,
                        "status": "likely_duplicate" if similarity > 0.95 else "very_similar"
                    })
        
        return {
            "has_duplicates": len(duplicates) > 0,
            "duplicates": duplicates,
            "recommendation": "Review and remove duplicate images for cleaner analysis" if duplicates else None
        }
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (Jaccard similarity)"""
        if not text1 or not text2:
            return 0.0
        
        # Tokenize
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
    
    def generate_conflict_resolution_guidance(self, conflicts: List[Dict[str, Any]]) -> List[str]:
        """Generate guidance for resolving conflicts"""
        guidance = []
        
        for conflict in conflicts:
            if conflict["resolution"] == "conflicting":
                field = conflict["field"]
                images = conflict["images"]
                
                if conflict["conflict_type"] == "value_mismatch":
                    guidance.append(
                        f"CONFLICT - {field.upper()}: Different values found across images. "
                        f"Images {images} show: {conflict['values']}. "
                        f"Please visually inspect the product to determine the correct value."
                    )
                elif conflict["conflict_type"] == "format_inconsistency":
                    guidance.append(
                        f"FORMAT VARIATION - {field.upper()}: Same value but different format. "
                        f"This is likely acceptable - appears to be formatting variation, not value difference."
                    )
        
        if not guidance:
            guidance.append("No significant conflicts detected across images.")
        
        return guidance


# Singleton instance
conflict_detector = ConflictDetector()
