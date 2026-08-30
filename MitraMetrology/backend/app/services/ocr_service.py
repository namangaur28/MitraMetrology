"""
OCR service using Tesseract (via pytesseract) for text extraction.
Lightweight, no PyTorch/CUDA required, works on ARM64.
"""
import cv2
import time
import logging
from typing import List, Dict, Any, Tuple

logger = logging.getLogger(__name__)

try:
    import pytesseract
    from PIL import Image
    import numpy as np
    TESSERACT_AVAILABLE = True
    logger.info("Tesseract OCR available")
except Exception as e:
    TESSERACT_AVAILABLE = False
    logger.warning(f"Tesseract not available: {e}. Using demo mode.")
    # Import demo/fallback service
    try:
        from .ocr_service_simple import SimpleOCRService
    except:
        SimpleOCRService = None


class OCRService:
    """Handles OCR extraction using Tesseract"""

    def __init__(self):
        self.ocr_available = TESSERACT_AVAILABLE
        self.simple_service = None
        
        if self.ocr_available:
            try:
                # Quick sanity check
                version = pytesseract.get_tesseract_version()
                logger.info(f"Tesseract initialized: version {version}")
            except Exception as e:
                logger.error(f"Failed to init Tesseract: {e}")
                self.ocr_available = False
        
        # Initialize fallback service if Tesseract not available
        if not self.ocr_available and SimpleOCRService:
            self.simple_service = SimpleOCRService()
            logger.info("Using simplified OCR service (demo mode)")

    def _preprocess(self, image_path: str):
        """Load and pre-process image for best OCR accuracy."""
        img = cv2.imread(image_path)
        if img is None:
            return None, None
        # Upscale small images
        h, w = img.shape[:2]
        if max(h, w) < 1000:
            scale = 1000 / max(h, w)
            img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
        # Convert to grayscale + mild sharpening
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (1, 1), 0)
        # Adaptive threshold for better contrast on product labels
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 31, 2
        )
        pil_img = Image.fromarray(thresh)
        pil_orig = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        return pil_img, pil_orig

    def extract_text(self, image_path: str) -> Tuple[bool, Dict[str, Any], str]:
        """
        Extract text from image using Tesseract.
        Falls back to demo mode if Tesseract not available.
        Returns: (success, result_dict, error_message)
        """
        try:
            start_time = time.time()

            # Use simple service if Tesseract not available
            if not self.ocr_available:
                if self.simple_service:
                    result = self.simple_service.extract_text_from_image(image_path)
                    if result["success"]:
                        return True, {
                            "text_blocks": result["text_blocks"],
                            "raw_text": result["raw_text"],
                            "confidence_avg": result["confidence"],
                            "processing_time_ms": 100,
                            "method": "demo_mode"
                        }, ""
                return False, {}, "OCR service not available"

            pil_thresh, pil_orig = self._preprocess(image_path)
            if pil_thresh is None:
                return False, {}, "Failed to read image"

            logger.info(f"Running Tesseract on {image_path}")

            # --- Run on pre-processed image ---
            custom_config = r"--oem 3 --psm 6"
            data = pytesseract.image_to_data(
                pil_thresh,
                config=custom_config,
                output_type=pytesseract.Output.DICT
            )

            text_blocks = []
            all_text = []
            confidences = []

            n = len(data["text"])
            for i in range(n):
                word = data["text"][i].strip()
                conf = int(data["conf"][i])
                if conf < 30 or not word:
                    continue
                x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
                norm_conf = conf / 100.0
                block = {
                    "text": word,
                    "confidence": norm_conf,
                    "bbox": [x, y, x + w, y + h]
                }
                text_blocks.append(block)
                all_text.append(word)
                confidences.append(norm_conf)
                logger.debug(f"Detected: '{word}' (confidence: {norm_conf:.2f})")

            # --- Also run on original (colour) image for any missed text ---
            raw_text_full = pytesseract.image_to_string(
                pil_orig,
                config=custom_config
            ).strip()

            # Merge: use word blocks from thresh run + full raw text from colour run
            raw_combined = raw_text_full if raw_text_full else " ".join(all_text)

            processing_time = int((time.time() - start_time) * 1000)
            result = {
                "text_blocks": text_blocks,
                "raw_text": raw_combined,
                "confidence_avg": (sum(confidences) / len(confidences)) if confidences else 0.0,
                "processing_time_ms": processing_time,
            }

            logger.info(f"Tesseract extracted {len(text_blocks)} words from {image_path}")
            logger.info(f"Raw text: {result['raw_text'][:300]}")
            logger.info(f"Average confidence: {result['confidence_avg']:.2f}")

            return True, result, ""

        except Exception as e:
            logger.error(f"OCR extraction error: {str(e)}", exc_info=True)
            return False, {}, str(e)

    def extract_text_with_regions(self, image_path: str) -> Tuple[bool, List[Dict[str, Any]], str]:
        """Extract text and return with bounding-box regions for visualisation."""
        success, result, error = self.extract_text(image_path)
        if not success:
            return False, [], error
        return True, result.get("text_blocks", []), ""


# Singleton instance
ocr_service = OCRService()
