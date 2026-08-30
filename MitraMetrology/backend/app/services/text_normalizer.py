"""
Text normalization and standardization for packaged commodities metadata
"""
import re
from typing import Dict, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class NormalizedQuantity:
    """Normalized quantity with standard units"""
    value: float
    unit: str  # 'ml', 'g', 'kg', 'l'
    original_text: str
    normalized_text: str
    
    def to_grams(self) -> float:
        """Convert to grams for comparison"""
        conversion = {
            'g': 1,
            'mg': 0.001,
            'kg': 1000,
            'ml': 1,  # Assume 1ml = 1g for liquids
            'l': 1000
        }
        return self.value * conversion.get(self.unit, 1)
    
    def __str__(self) -> str:
        return f"{self.value} {self.unit}"


@dataclass
class NormalizedPrice:
    """Normalized price in standard format"""
    value: float
    currency: str  # 'INR'
    original_text: str
    normalized_text: str
    
    def __str__(self) -> str:
        return f"₹{self.value:.2f}"


@dataclass
class NormalizedDate:
    """Normalized date in standard format"""
    day: int
    month: int
    year: int
    original_text: str
    normalized_text: str
    date_type: str  # 'mfg', 'packing', 'expiry', 'import'
    
    def __str__(self) -> str:
        return f"{self.day:02d}/{self.month:02d}/{self.year:04d}"


class TextNormalizer:
    """Standardize and normalize text from OCR results"""
    
    def __init__(self):
        # Indian and international currency patterns
        self.currency_patterns = {
            'INR': [r'₹', r'Rs\.?', r'Rs\.', r'INR', r'रु\.?'],
            'USD': [r'\$', r'USD'],
        }
        
        # Quantity patterns with multiple formats
        self.quantity_patterns = [
            # Format: number unit (e.g., "500 ml", "250g")
            (r'(\d+\.?\d*)\s*(?:ml|mL|Ml|ML)', 'ml'),
            (r'(\d+\.?\d*)\s*(?:g|G|gm|GM|gm\.)', 'g'),
            (r'(\d+\.?\d*)\s*(?:kg|KG|Kg)', 'kg'),
            (r'(\d+\.?\d*)\s*(?:l|L|litre|liter|लीटर)', 'l'),
        ]
        
        # Date patterns (DD/MM/YYYY, DD-MM-YYYY, etc.)
        self.date_patterns = [
            (r'(\d{1,2})[-/](\d{1,2})[-/](\d{4})', 'dmy'),  # DD/MM/YYYY
            (r'(\d{4})[-/](\d{1,2})[-/](\d{1,2})', 'ymd'),  # YYYY/MM/DD
            (r'(\d{1,2})\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(\d{4})', 'named'),
        ]
        
        # Common text variations
        self.replacements = {
            'manufacter': 'manufacturer',
            'manufactuerer': 'manufacturer',
            'net wt': 'net weight',
            'net weight': 'net weight',
            'mrp': 'mrp',
            'max retail price': 'mrp',
            'mfg': 'manufactured',
            'mfg date': 'manufactured date',
            'exp': 'expiry',
            'exp date': 'expiry date',
            'best before': 'expiry',
            'best by': 'expiry',
        }
    
    def normalize_text(self, text: str) -> str:
        """Basic text normalization"""
        if not text:
            return ""
        
        # Convert to lowercase for processing
        normalized = text.strip().lower()
        
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Apply common replacements
        for old, new in self.replacements.items():
            normalized = re.sub(r'\b' + re.escape(old) + r'\b', new, normalized)
        
        # Remove special characters except currency symbols and essential punctuation
        normalized = re.sub(r'[^\w\s₹\$\-\./]', '', normalized)
        
        return normalized
    
    def extract_and_normalize_price(self, text: str) -> Optional[NormalizedPrice]:
        """Extract and normalize price from text"""
        if not text:
            return None
        
        # Look for MRP or price patterns
        patterns = [
            (r'(?:mrp|price|cost)?\s*[₹Rs\.]*\s*(\d+\.?\d*)', 'INR'),
            (r'[₹Rs\.]\s*(\d+\.?\d*)', 'INR'),
            (r'\$\s*(\d+\.?\d*)', 'USD'),
        ]
        
        for pattern, currency in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                normalized_text = f"₹{value:.2f}" if currency == 'INR' else f"${value:.2f}"
                
                return NormalizedPrice(
                    value=value,
                    currency=currency,
                    original_text=text,
                    normalized_text=normalized_text
                )
        
        return None
    
    def extract_and_normalize_quantity(self, text: str) -> Optional[NormalizedQuantity]:
        """Extract and normalize quantity from text"""
        if not text:
            return None
        
        text_clean = text.strip().lower()
        
        for pattern, unit in self.quantity_patterns:
            match = re.search(pattern, text_clean)
            if match:
                value = float(match.group(1))
                
                # Normalize to canonical form
                normalized_text = f"{value} {unit}"
                
                return NormalizedQuantity(
                    value=value,
                    unit=unit,
                    original_text=text,
                    normalized_text=normalized_text
                )
        
        return None
    
    def extract_and_normalize_date(self, text: str, date_type: str = 'mfg') -> Optional[NormalizedDate]:
        """Extract and normalize date from text"""
        if not text:
            return None
        
        text_clean = text.strip().lower()
        
        # Try each date pattern
        for pattern, date_format in self.date_patterns:
            match = re.search(pattern, text_clean, re.IGNORECASE)
            if match:
                try:
                    if date_format == 'dmy':
                        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    elif date_format == 'ymd':
                        year, month, day = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    else:
                        continue
                    
                    # Validate date ranges
                    if not (1 <= month <= 12 and 1 <= day <= 31):
                        continue
                    
                    normalized_text = f"{day:02d}/{month:02d}/{year:04d}"
                    
                    return NormalizedDate(
                        day=day,
                        month=month,
                        year=year,
                        original_text=text,
                        normalized_text=normalized_text,
                        date_type=date_type
                    )
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def detect_language_mix(self, text: str) -> Dict[str, any]:
        """Detect if text contains Hindi/English mix"""
        # Unicode ranges for Hindi Devanagari script
        hindi_pattern = re.compile(r'[\u0900-\u097F]')
        english_pattern = re.compile(r'[a-zA-Z]')
        
        hindi_chars = len(hindi_pattern.findall(text))
        english_chars = len(english_pattern.findall(text))
        
        return {
            'has_hindi': hindi_chars > 0,
            'has_english': english_chars > 0,
            'hindi_char_count': hindi_chars,
            'english_char_count': english_chars,
            'mixed': hindi_chars > 0 and english_chars > 0
        }
    
    def normalize_manufacturer_name(self, text: str) -> str:
        """Normalize manufacturer/company names"""
        if not text:
            return ""
        
        normalized = text.strip()
        
        # Remove common suffixes/prefixes
        normalized = re.sub(r'\b(?:Ltd|Limited|Inc|Incorporated|Pvt|Private|LLC|Corp|Corporation)\b\.?', '', normalized, flags=re.IGNORECASE)
        
        # Remove extra spaces
        normalized = re.sub(r'\s+', ' ', normalized).strip()
        
        return normalized
    
    def compare_quantities(self, qty1: NormalizedQuantity, qty2: NormalizedQuantity) -> bool:
        """Check if two quantities are equal"""
        if not qty1 or not qty2:
            return False
        
        # Convert both to grams for comparison
        g1 = qty1.to_grams()
        g2 = qty2.to_grams()
        
        # Allow 1% tolerance for measurement variations
        tolerance = max(g1, g2) * 0.01
        return abs(g1 - g2) <= tolerance
    
    def compare_prices(self, price1: NormalizedPrice, price2: NormalizedPrice) -> bool:
        """Check if two prices are equal"""
        if not price1 or not price2:
            return False
        
        if price1.currency != price2.currency:
            return False
        
        # Allow 1% tolerance for price variations
        tolerance = max(price1.value, price2.value) * 0.01
        return abs(price1.value - price2.value) <= tolerance
    
    def compare_dates(self, date1: NormalizedDate, date2: NormalizedDate) -> bool:
        """Check if two dates are equal"""
        if not date1 or not date2:
            return False
        
        return (date1.day == date2.day and 
                date1.month == date2.month and 
                date1.year == date2.year)


# Singleton instance
text_normalizer = TextNormalizer()
