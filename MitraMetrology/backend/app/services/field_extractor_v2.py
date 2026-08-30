"""
Advanced field extraction with normalization and evidence tracking
"""
import re
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from app.services.text_normalizer import (
    TextNormalizer, NormalizedQuantity, NormalizedPrice, NormalizedDate
)

logger = logging.getLogger(__name__)


@dataclass
class ExtractedFieldV2:
    """Enhanced extracted field with normalization and evidence"""
    field_name: str
    raw_value: Optional[str]  # Original extracted value
    normalized_value: Optional[str]  # Standardized value
    confidence: float
    source_text: str
    bbox: Optional[List[float]]
    extraction_method: str  # 'regex', 'keyword', 'pattern'
    
    # Normalization info
    normalization_type: Optional[str]  # 'quantity', 'price', 'date', 'text'
    normalization_applied: bool = False
    
    # Evidence
    image_id: Optional[str] = None
    language_mix: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_name": self.field_name,
            "raw_value": self.raw_value,
            "normalized_value": self.normalized_value,
            "confidence": self.confidence,
            "source_text": self.source_text,
            "bbox": self.bbox,
            "extraction_method": self.extraction_method,
            "normalization_type": self.normalization_type,
            "normalization_applied": self.normalization_applied,
            "image_id": self.image_id,
            "language_mix": self.language_mix,
        }


class FieldExtractorV2:
    """Advanced field extraction with normalization"""
    
    def __init__(self):
        self.normalizer = TextNormalizer()
        self.keywords = {
            "product_name": ["name", "product", "description", "title", "brand"],
            "manufacturer": ["manufacturer", "mfg", "mfr", "made by", "made in", "निर्माता"],
            "packer": ["packed by", "packer", "packaging", "packed"],
            "importer": ["imported by", "importer", "imported", "distributor"],
            "mrp": ["mrp", "price", "retail price", "cost", "मूल्य"],
            "net_quantity": ["net", "content", "quantity", "qty", "weight", "wt", "वजन"],
            "date": ["mfg", "manufacturing", "packed", "packing", "imported", "exp", "expiry", "do not use after"],
            "consumer_care": ["consumer care", "phone", "email", "contact", "customer", "toll free"]
        }
    
    def extract_fields(self, text_blocks: List[Dict[str, Any]], image_id: Optional[str] = None) -> Dict[str, ExtractedFieldV2]:
        """
        Extract all fields from OCR results with normalization
        """
        results = {}
        raw_text = " ".join([block["text"] for block in text_blocks])
        
        # Extract fields
        results["product_name"] = self._extract_product_name(text_blocks, raw_text, image_id)
        results["manufacturer"] = self._extract_manufacturer(text_blocks, raw_text, image_id)
        results["packer"] = self._extract_packer(text_blocks, raw_text, image_id)
        results["importer"] = self._extract_importer(text_blocks, raw_text, image_id)
        results["net_quantity"] = self._extract_net_quantity(text_blocks, raw_text, image_id)
        results["mrp"] = self._extract_mrp(text_blocks, raw_text, image_id)
        results["date"] = self._extract_date(text_blocks, raw_text, image_id)
        results["consumer_care"] = self._extract_consumer_care(text_blocks, raw_text, image_id)
        
        return results
    
    def _create_field(self, field_name: str, raw_value: Optional[str], 
                     source_text: str, bbox: Optional[List[float]],
                     confidence: float, method: str, image_id: Optional[str] = None) -> ExtractedFieldV2:
        """Helper to create ExtractedFieldV2"""
        field = ExtractedFieldV2(
            field_name=field_name,
            raw_value=raw_value,
            normalized_value=raw_value,
            confidence=confidence,
            source_text=source_text,
            bbox=bbox,
            extraction_method=method,
            image_id=image_id
        )
        
        # Apply normalization
        if raw_value:
            field.language_mix = self.normalizer.detect_language_mix(raw_value)
            
            # Normalize based on field type
            if field_name == "mrp":
                price = self.normalizer.extract_and_normalize_price(raw_value)
                if price:
                    field.normalized_value = str(price)
                    field.normalization_applied = True
                    field.normalization_type = "price"
            
            elif field_name == "net_quantity":
                qty = self.normalizer.extract_and_normalize_quantity(raw_value)
                if qty:
                    field.normalized_value = str(qty)
                    field.normalization_applied = True
                    field.normalization_type = "quantity"
            
            elif field_name == "date":
                date = self.normalizer.extract_and_normalize_date(raw_value)
                if date:
                    field.normalized_value = str(date)
                    field.normalization_applied = True
                    field.normalization_type = "date"
            
            elif field_name == "manufacturer":
                normalized = self.normalizer.normalize_manufacturer_name(raw_value)
                if normalized != raw_value:
                    field.normalized_value = normalized
                    field.normalization_applied = True
                    field.normalization_type = "text"
        
        return field
    
    def _extract_product_name(self, text_blocks: List[Dict[str, Any]], raw_text: str, 
                             image_id: Optional[str] = None) -> ExtractedFieldV2:
        """Extract product name - typically first meaningful line"""
        if text_blocks:
            first_block = text_blocks[0]
            if len(first_block["text"]) > 2:
                return self._create_field(
                    "product_name",
                    first_block["text"],
                    first_block["text"],
                    first_block.get("bbox"),
                    first_block["confidence"],
                    "keyword",
                    image_id
                )
        
        return self._create_field("product_name", None, "", None, 0.0, "keyword", image_id)
    
    def _extract_manufacturer(self, text_blocks: List[Dict[str, Any]], raw_text: str,
                             image_id: Optional[str] = None) -> ExtractedFieldV2:
        """Extract manufacturer information"""
        keywords = self.keywords["manufacturer"]
        value, conf, source, bbox = self._find_by_keyword(text_blocks, keywords)
        
        if value:
            return self._create_field("manufacturer", value, source, bbox, conf, "keyword", image_id)
        
        return self._create_field("manufacturer", None, "", None, 0.0, "keyword", image_id)
    
    def _extract_packer(self, text_blocks: List[Dict[str, Any]], raw_text: str,
                       image_id: Optional[str] = None) -> ExtractedFieldV2:
        """Extract packer information"""
        keywords = self.keywords["packer"]
        value, conf, source, bbox = self._find_by_keyword(text_blocks, keywords)
        
        if value:
            return self._create_field("packer", value, source, bbox, conf, "keyword", image_id)
        
        return self._create_field("packer", None, "", None, 0.0, "keyword", image_id)
    
    def _extract_importer(self, text_blocks: List[Dict[str, Any]], raw_text: str,
                         image_id: Optional[str] = None) -> ExtractedFieldV2:
        """Extract importer information"""
        keywords = self.keywords["importer"]
        value, conf, source, bbox = self._find_by_keyword(text_blocks, keywords)
        
        if value:
            return self._create_field("importer", value, source, bbox, conf, "keyword", image_id)
        
        return self._create_field("importer", None, "", None, 0.0, "keyword", image_id)
    
    def _extract_net_quantity(self, text_blocks: List[Dict[str, Any]], raw_text: str,
                             image_id: Optional[str] = None) -> ExtractedFieldV2:
        """Extract net quantity using regex patterns"""
        patterns = [
            r'(\d+\.?\d*)\s*(?:ml|ML|mL|Ml)',
            r'(\d+\.?\d*)\s*(?:gm|GM|g|G)',
            r'(\d+\.?\d*)\s*(?:kg|KG)',
            r'(?:net|NET).*?(\d+\.?\d*)\s*(?:ml|gm|kg|g)',
            r'(?:content|CONTENT).*?(\d+\.?\d*)\s*(?:ml|gm|kg|g)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, raw_text)
            for match in matches:
                matched_text = match.group(0)
                for block in text_blocks:
                    if matched_text in block["text"]:
                        return self._create_field("net_quantity", matched_text, matched_text,
                                                block.get("bbox"), block["confidence"], "regex", image_id)
                
                return self._create_field("net_quantity", matched_text, matched_text,
                                        None, 0.7, "regex", image_id)
        
        return self._create_field("net_quantity", None, "", None, 0.0, "regex", image_id)
    
    def _extract_mrp(self, text_blocks: List[Dict[str, Any]], raw_text: str,
                    image_id: Optional[str] = None) -> ExtractedFieldV2:
        """Extract MRP/Price using regex patterns"""
        patterns = [
            r'MRP\s*₹?\s*(\d+\.?\d*)',
            r'₹\s*(\d+\.?\d*)',
            r'RS\.?\s*(\d+\.?\d*)',
            r'(?:Price|PRICE)\s*₹?\s*(\d+\.?\d*)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, raw_text, re.IGNORECASE)
            for match in matches:
                matched_text = match.group(0)
                for block in text_blocks:
                    if matched_text in block["text"] or match.group(1) in block["text"]:
                        return self._create_field("mrp", f"₹{match.group(1)}", matched_text,
                                                block.get("bbox"), block["confidence"], "regex", image_id)
                
                return self._create_field("mrp", f"₹{match.group(1)}", matched_text,
                                        None, 0.7, "regex", image_id)
        
        return self._create_field("mrp", None, "", None, 0.0, "regex", image_id)
    
    def _extract_date(self, text_blocks: List[Dict[str, Any]], raw_text: str,
                     image_id: Optional[str] = None) -> ExtractedFieldV2:
        """Extract manufacturing/packing/expiry date"""
        patterns = [
            r'(?:MFG|Mfg|mfg|Manufacturing)\s*(?:Date)?:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:Packed|PACKED|Packing)\s*(?:Date)?:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:Imported|IMPORTED)\s*(?:Date)?:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:Exp|EXP|Expiry)\s*(?:Date)?:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, raw_text)
            for match in matches:
                matched_text = match.group(0)
                for block in text_blocks:
                    if match.group(1) in block["text"]:
                        return self._create_field("date", matched_text, matched_text,
                                                block.get("bbox"), block["confidence"], "regex", image_id)
        
        return self._create_field("date", None, "", None, 0.0, "regex", image_id)
    
    def _extract_consumer_care(self, text_blocks: List[Dict[str, Any]], raw_text: str,
                              image_id: Optional[str] = None) -> ExtractedFieldV2:
        """Extract consumer care details"""
        keywords = self.keywords["consumer_care"]
        
        for i, block in enumerate(text_blocks):
            text_lower = block["text"].lower()
            if any(kw in text_lower for kw in keywords):
                consumer_info = [block["text"]]
                for j in range(i + 1, min(i + 3, len(text_blocks))):
                    consumer_info.append(text_blocks[j]["text"])
                
                combined_text = " ".join(consumer_info)
                return self._create_field("consumer_care", combined_text, combined_text,
                                        block.get("bbox"), block["confidence"], "keyword", image_id)
        
        return self._create_field("consumer_care", None, "", None, 0.0, "keyword", image_id)
    
    def _find_by_keyword(self, text_blocks: List[Dict[str, Any]], keywords: List[str],
                        offset: int = 1) -> tuple:
        """Find text following keywords"""
        for i, block in enumerate(text_blocks):
            text_lower = block["text"].lower()
            for keyword in keywords:
                if keyword in text_lower:
                    if i + offset < len(text_blocks):
                        value_block = text_blocks[i + offset]
                        return (
                            value_block["text"],
                            value_block["confidence"],
                            f"{block['text']} {value_block['text']}",
                            value_block.get("bbox")
                        )
        return None, 0.0, "", None


# Singleton instance
field_extractor_v2 = FieldExtractorV2()
