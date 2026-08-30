"""
Field extraction engine for identifying key information from OCR text
Uses regex, keyword matching, and text normalization
"""
import re
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExtractedField:
    """Represents an extracted field"""
    field_name: str
    value: Optional[str]
    confidence: float
    source_text: str
    bbox: Optional[List[float]]
    extraction_method: str  # 'regex', 'keyword', 'pattern'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "field_name": self.field_name,
            "value": self.value,
            "confidence": self.confidence,
            "source_text": self.source_text,
            "bbox": self.bbox,
            "extraction_method": self.extraction_method
        }


class FieldExtractor:
    """Extracts structured fields from OCR results"""
    
    def __init__(self):
        # Keywords for field identification
        self.keywords = {
            "product_name": ["name", "product", "description", "title"],
            "manufacturer": ["manufacturer", "mfg", "mfr", "made by", "made in"],
            "packer": ["packed by", "packer", "packaging"],
            "importer": ["imported by", "importer", "imported"],
            "mrp": ["mrp", "₹", "price", "rs", "rupees"],
            "net_quantity": ["net", "content", "quantity", "qty", "weight", "ml", "gm", "kg"],
            "date": ["mfg", "manufacturing", "packed", "packing", "imported", "exp", "expiry", "do not use after"],
            "consumer_care": ["consumer care", "phone", "email", "contact", "customer", "toll free"]
        }
    
    def extract_fields(self, text_blocks: List[Dict[str, Any]]) -> Dict[str, ExtractedField]:
        """
        Extract all fields from OCR results
        text_blocks: List of {"text": str, "confidence": float, "bbox": list}
        Returns: Dict of field_name -> ExtractedField
        """
        results = {}
        raw_text = " ".join([block.get("text", "") for block in text_blocks if block.get("text")])
        
        logger.info(f"extract_fields called with {len(text_blocks)} text blocks")
        logger.info(f"Raw text from OCR: {raw_text[:300]}")
        
        # Extract each field type
        results["product_name"] = self._extract_product_name(text_blocks, raw_text)
        results["manufacturer"] = self._extract_manufacturer(text_blocks, raw_text)
        results["packer"] = self._extract_packer(text_blocks, raw_text)
        results["importer"] = self._extract_importer(text_blocks, raw_text)
        results["net_quantity"] = self._extract_net_quantity(text_blocks, raw_text)
        results["mrp"] = self._extract_mrp(text_blocks, raw_text)
        results["date"] = self._extract_date(text_blocks, raw_text)
        results["consumer_care"] = self._extract_consumer_care(text_blocks, raw_text)
        
        # Log what was extracted
        for field_name, field in results.items():
            if field.value:
                logger.info(f"Extracted {field_name}: {field.value}")
        
        # DO NOT use mock data - return what we actually extracted
        return results
    
    def _get_mock_fields(self) -> Dict[str, ExtractedField]:
        """Return mock extracted fields for prototype/testing"""
        return {
            "product_name": ExtractedField(
                field_name="product_name",
                value="Organic Basmati Rice",
                confidence=0.95,
                source_text="Organic Basmati Rice",
                bbox=[10, 20, 300, 60],
                extraction_method="mock"
            ),
            "manufacturer": ExtractedField(
                field_name="manufacturer",
                value="Premium Foods Pvt. Ltd.",
                confidence=0.88,
                source_text="Manufactured by: Premium Foods Pvt. Ltd.",
                bbox=[10, 100, 400, 140],
                extraction_method="mock"
            ),
            "packer": ExtractedField(
                field_name="packer",
                value="Premium Foods Pvt. Ltd., Mumbai, India",
                confidence=0.85,
                source_text="Packed by: Premium Foods Pvt. Ltd., Mumbai, India",
                bbox=[10, 160, 450, 200],
                extraction_method="mock"
            ),
            "importer": ExtractedField(
                field_name="importer",
                value=None,
                confidence=0.0,
                source_text="",
                bbox=None,
                extraction_method="mock"
            ),
            "net_quantity": ExtractedField(
                field_name="net_quantity",
                value="1 kg (1000g)",
                confidence=0.92,
                source_text="Net Quantity: 1 kg (1000g)",
                bbox=[10, 240, 300, 280],
                extraction_method="mock"
            ),
            "mrp": ExtractedField(
                field_name="mrp",
                value="₹299",
                confidence=0.96,
                source_text="MRP: ₹299",
                bbox=[10, 300, 200, 340],
                extraction_method="mock"
            ),
            "date": ExtractedField(
                field_name="date",
                value="Mfg: 01/08/2026 | Best Before: 01/08/2027",
                confidence=0.90,
                source_text="Manufacturing Date: 01/08/2026 | Best Before: 01/08/2027",
                bbox=[10, 360, 500, 400],
                extraction_method="mock"
            ),
            "consumer_care": ExtractedField(
                field_name="consumer_care",
                value="1-800-RICE-CARE | care@premiumfoods.com",
                confidence=0.87,
                source_text="Customer Care: 1-800-RICE-CARE | care@premiumfoods.com",
                bbox=[10, 420, 450, 460],
                extraction_method="mock"
            ),
        }
    
    def _find_by_keyword(self, text_blocks: List[Dict[str, Any]], keywords: List[str], 
                        offset: int = 1) -> Tuple[Optional[str], float, Optional[str], Optional[List[float]]]:
        """
        Find text following keywords
        offset: how many blocks after keyword to look for value
        Returns: (value, confidence, source_text, bbox)
        """
        for i, block in enumerate(text_blocks):
            text_lower = block["text"].lower()
            for keyword in keywords:
                if keyword in text_lower:
                    # Found keyword, look for value in nearby blocks
                    if i + offset < len(text_blocks):
                        value_block = text_blocks[i + offset]
                        return (
                            value_block["text"],
                            value_block["confidence"],
                            f"{block['text']} {value_block['text']}",
                            value_block.get("bbox")
                        )
        return None, 0.0, "", None
    
    def _extract_product_name(self, text_blocks: List[Dict[str, Any]], raw_text: str) -> ExtractedField:
        """Extract product name - typically first meaningful line"""
        if text_blocks:
            first_block = text_blocks[0]
            if len(first_block["text"]) > 2:  # Skip very short text
                return ExtractedField(
                    field_name="product_name",
                    value=first_block["text"],
                    confidence=first_block["confidence"],
                    source_text=first_block["text"],
                    bbox=first_block.get("bbox"),
                    extraction_method="keyword"
                )
        
        return ExtractedField("product_name", None, 0.0, "", None, "keyword")
    
    def _extract_manufacturer(self, text_blocks: List[Dict[str, Any]], raw_text: str) -> ExtractedField:
        """Extract manufacturer information"""
        keywords = self.keywords["manufacturer"]
        value, conf, source, bbox = self._find_by_keyword(text_blocks, keywords)
        
        if value:
            return ExtractedField(
                field_name="manufacturer",
                value=value,
                confidence=conf,
                source_text=source,
                bbox=bbox,
                extraction_method="keyword"
            )
        
        return ExtractedField("manufacturer", None, 0.0, "", None, "keyword")
    
    def _extract_packer(self, text_blocks: List[Dict[str, Any]], raw_text: str) -> ExtractedField:
        """Extract packer information"""
        keywords = self.keywords["packer"]
        value, conf, source, bbox = self._find_by_keyword(text_blocks, keywords)
        
        if value:
            return ExtractedField(
                field_name="packer",
                value=value,
                confidence=conf,
                source_text=source,
                bbox=bbox,
                extraction_method="keyword"
            )
        
        return ExtractedField("packer", None, 0.0, "", None, "keyword")
    
    def _extract_importer(self, text_blocks: List[Dict[str, Any]], raw_text: str) -> ExtractedField:
        """Extract importer information"""
        keywords = self.keywords["importer"]
        value, conf, source, bbox = self._find_by_keyword(text_blocks, keywords)
        
        if value:
            return ExtractedField(
                field_name="importer",
                value=value,
                confidence=conf,
                source_text=source,
                bbox=bbox,
                extraction_method="keyword"
            )
        
        return ExtractedField("importer", None, 0.0, "", None, "keyword")
    
    def _extract_net_quantity(self, text_blocks: List[Dict[str, Any]], raw_text: str) -> ExtractedField:
        """Extract net quantity using regex patterns"""
        # Regex patterns for quantity
        patterns = [
            r'(\d+\.?\d*)\s*(?:ml|ML|mL|Ml)',  # Volume in ml
            r'(\d+\.?\d*)\s*(?:gm|GM|g|G)',      # Weight in grams
            r'(\d+\.?\d*)\s*(?:kg|KG)',          # Weight in kg
            r'(?:net|NET).*?(\d+\.?\d*)\s*(?:ml|gm|kg|g)',
            r'(?:content|CONTENT).*?(\d+\.?\d*)\s*(?:ml|gm|kg|g)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, raw_text)
            for match in matches:
                # Find which block this came from for bbox
                matched_text = match.group(0)
                for block in text_blocks:
                    if matched_text in block["text"]:
                        return ExtractedField(
                            field_name="net_quantity",
                            value=matched_text,
                            confidence=block["confidence"],
                            source_text=matched_text,
                            bbox=block.get("bbox"),
                            extraction_method="regex"
                        )
                
                # If we found a match but couldn't locate block, return with lower confidence
                return ExtractedField(
                    field_name="net_quantity",
                    value=matched_text,
                    confidence=0.7,
                    source_text=matched_text,
                    bbox=None,
                    extraction_method="regex"
                )
        
        return ExtractedField("net_quantity", None, 0.0, "", None, "regex")
    
    def _extract_mrp(self, text_blocks: List[Dict[str, Any]], raw_text: str) -> ExtractedField:
        """Extract MRP/Price using regex patterns"""
        # Patterns for MRP
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
                        return ExtractedField(
                            field_name="mrp",
                            value=f"₹{match.group(1)}",
                            confidence=block["confidence"],
                            source_text=matched_text,
                            bbox=block.get("bbox"),
                            extraction_method="regex"
                        )
                
                return ExtractedField(
                    field_name="mrp",
                    value=f"₹{match.group(1)}",
                    confidence=0.7,
                    source_text=matched_text,
                    bbox=None,
                    extraction_method="regex"
                )
        
        return ExtractedField("mrp", None, 0.0, "", None, "regex")
    
    def _extract_date(self, text_blocks: List[Dict[str, Any]], raw_text: str) -> ExtractedField:
        """Extract manufacturing/packing/expiry date"""
        # Date patterns
        patterns = [
            r'(?:MFG|Mfg|mfg|Manufacturing)\s*(?:Date)?:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:Packed|PACKED|Packing)\s*(?:Date)?:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:Imported|IMPORTED)\s*(?:Date)?:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(?:Exp|EXP|Expiry)\s*(?:Date)?:?\s*(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})'  # Generic date pattern
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, raw_text)
            for match in matches:
                matched_text = match.group(0)
                for block in text_blocks:
                    if match.group(1) in block["text"]:
                        return ExtractedField(
                            field_name="date",
                            value=match.group(1),
                            confidence=block["confidence"],
                            source_text=matched_text,
                            bbox=block.get("bbox"),
                            extraction_method="regex"
                        )
        
        return ExtractedField("date", None, 0.0, "", None, "regex")
    
    def _extract_consumer_care(self, text_blocks: List[Dict[str, Any]], raw_text: str) -> ExtractedField:
        """Extract consumer care details"""
        keywords = self.keywords["consumer_care"]
        
        # Look for consumer care section
        for i, block in enumerate(text_blocks):
            text_lower = block["text"].lower()
            if any(kw in text_lower for kw in keywords):
                # Collect next few lines as consumer care info
                consumer_info = [block["text"]]
                for j in range(i + 1, min(i + 3, len(text_blocks))):
                    consumer_info.append(text_blocks[j]["text"])
                
                combined_text = " ".join(consumer_info)
                return ExtractedField(
                    field_name="consumer_care",
                    value=combined_text,
                    confidence=block["confidence"],
                    source_text=combined_text,
                    bbox=block.get("bbox"),
                    extraction_method="keyword"
                )
        
        return ExtractedField("consumer_care", None, 0.0, "", None, "keyword")


# Singleton instance
field_extractor = FieldExtractor()
