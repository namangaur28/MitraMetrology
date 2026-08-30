"""
Advanced image processing service for preprocessing images before OCR
Enhanced with perspective correction, rotation detection, and multi-scale processing
"""
import os
import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional, List
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Handles image validation, resizing, and preprocessing"""
    
    def __init__(self):
        self.max_width = settings.img_max_width
        self.max_height = settings.img_max_height
        self.quality = settings.img_quality
        self.allowed_extensions = settings.allowed_image_extensions.split(",")
        self.max_file_size = settings.max_file_size_mb * 1024 * 1024
    
    def validate_file(self, file_path: str, file_size: int) -> Tuple[bool, str]:
        """
        Validate file size and extension
        Returns: (is_valid, error_message)
        """
        if file_size > self.max_file_size:
            return False, f"File size exceeds {settings.max_file_size_mb}MB limit"
        
        # Check extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lstrip(".").lower()
        if ext not in self.allowed_extensions:
            return False, f"File extension .{ext} not allowed. Allowed: {', '.join(self.allowed_extensions)}"
        
        return True, ""
    
    def validate_image(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate that file is a valid image
        Returns: (is_valid, error_message)
        """
        try:
            img = cv2.imread(file_path)
            if img is None:
                return False, "Invalid or corrupted image file"
            return True, ""
        except Exception as e:
            return False, f"Error reading image: {str(e)}"
    
    def get_image_dimensions(self, file_path: str) -> Tuple[int, int]:
        """Get original image dimensions"""
        try:
            img = cv2.imread(file_path)
            if img is None:
                return 0, 0
            height, width = img.shape[:2]
            return width, height
        except Exception as e:
            logger.error(f"Error getting image dimensions: {str(e)}")
            return 0, 0
    
    def process_image(self, input_path: str, output_path: str) -> Tuple[bool, str, dict]:
        """
        Advanced image processing with rotation and perspective correction
        Returns: (success, error_message, metadata)
        """
        try:
            # Read image
            img = cv2.imread(input_path)
            if img is None:
                return False, "Failed to read image", {}
            
            metadata = {}
            
            # Fix orientation using EXIF data
            img = self._fix_orientation(input_path, img)
            
            # Detect and correct rotation
            angle = self.detect_rotation(img)
            if abs(angle) > 0.5:
                img = self.correct_rotation(img, angle)
                metadata['rotation_corrected'] = angle
            
            # Attempt perspective correction
            img = self.correct_perspective(img)
            metadata['perspective_corrected'] = True
            
            # Analyze readability before enhancement
            readability_before = self.analyze_readability(img)
            metadata['readability_before'] = readability_before
            
            # Resize if necessary
            img = self._resize_image(img)
            
            # Improve contrast and reduce noise
            img = self._enhance_image(img)
            
            # Analyze readability after enhancement
            readability_after = self.analyze_readability(img)
            metadata['readability_after'] = readability_after
            
            # Save processed image
            success = cv2.imwrite(output_path, img, [cv2.IMWRITE_JPEG_QUALITY, self.quality])
            if not success:
                return False, "Failed to save processed image", metadata
            
            return True, "", metadata
        
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return False, f"Image processing error: {str(e)}", {}
    
    def _fix_orientation(self, file_path: str, img: np.ndarray) -> np.ndarray:
        """Fix image orientation based on EXIF data"""
        try:
            pil_image = Image.open(file_path)
            
            # Get EXIF orientation
            try:
                exif = pil_image._getexif()
                if exif is not None:
                    for tag, value in exif:
                        if tag == 274:  # Orientation tag
                            if value == 3:
                                img = cv2.rotate(img, cv2.ROTATE_180)
                            elif value == 6:
                                img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
                            elif value == 8:
                                img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
            except (AttributeError, KeyError, IndexError):
                pass
            
            return img
        except Exception as e:
            logger.debug(f"Could not fix orientation: {str(e)}")
            return img
    
    def _resize_image(self, img: np.ndarray) -> np.ndarray:
        """Resize image if it exceeds max dimensions"""
        height, width = img.shape[:2]
        
        if width > self.max_width or height > self.max_height:
            ratio = min(self.max_width / width, self.max_height / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        
        return img
    
    def _enhance_image(self, img: np.ndarray) -> np.ndarray:
        """Enhance image contrast and reduce noise for better OCR"""
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
        
        # Enhance contrast using CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Convert back to BGR for consistency
        enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        
        return enhanced_bgr
    
    def detect_rotation(self, img: np.ndarray) -> float:
        """Detect rotation angle of text using Hough transform"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            
            lines = cv2.HoughLines(edges, 1, np.pi/180, 100)
            if lines is None:
                return 0
            
            angles = []
            for line in lines[:50]:  # Use first 50 lines
                rho, theta = line[0]
                angle = np.degrees(theta)
                angles.append(angle)
            
            if angles:
                # Get median angle
                median_angle = np.median(angles)
                # Normalize to -45 to 45 range
                if median_angle > 90:
                    median_angle -= 180
                elif median_angle < -90:
                    median_angle += 180
                return median_angle
            return 0
        except Exception as e:
            logger.warning(f"Error detecting rotation: {str(e)}")
            return 0
    
    def correct_rotation(self, img: np.ndarray, angle: float) -> np.ndarray:
        """Correct rotation of image"""
        if abs(angle) < 0.5:  # Small angles don't need correction
            return img
        
        height, width = img.shape[:2]
        center = (width // 2, height // 2)
        
        # Get rotation matrix
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Calculate new dimensions
        cos = np.abs(rotation_matrix[0, 0])
        sin = np.abs(rotation_matrix[0, 1])
        new_width = int((height * sin) + (width * cos))
        new_height = int((height * cos) + (width * sin))
        
        # Adjust the rotation matrix
        rotation_matrix[0, 2] += (new_width / 2) - center[0]
        rotation_matrix[1, 2] += (new_height / 2) - center[1]
        
        # Perform rotation
        rotated = cv2.warpAffine(img, rotation_matrix, (new_width, new_height),
                                borderMode=cv2.BORDER_CONSTANT, borderValue=(255, 255, 255))
        
        return rotated
    
    def correct_perspective(self, img: np.ndarray) -> np.ndarray:
        """Attempt perspective correction using edge detection"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, 50, 150)
            
            # Find contours
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            if not contours:
                return img
            
            # Find largest contour
            largest_contour = max(contours, key=cv2.contourArea)
            peri = cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, 0.02 * peri, True)
            
            if len(approx) == 4:
                # Found rectangle, perform perspective transform
                src_pts = np.float32(approx.reshape(4, 2))
                
                # Order points: top-left, top-right, bottom-right, bottom-left
                rect = self._order_points(src_pts)
                
                # Destination points
                max_width = max(np.linalg.norm(rect[1] - rect[0]), 
                               np.linalg.norm(rect[3] - rect[2]))
                max_height = max(np.linalg.norm(rect[3] - rect[0]),
                                np.linalg.norm(rect[2] - rect[1]))
                
                dst_pts = np.float32([[0, 0], [max_width, 0], 
                                     [max_width, max_height], [0, max_height]])
                
                # Perspective transform
                M = cv2.getPerspectiveTransform(rect, dst_pts)
                warped = cv2.warpPerspective(img, M, (int(max_width), int(max_height)))
                
                return warped
        except Exception as e:
            logger.debug(f"Perspective correction failed: {str(e)}")
        
        return img
    
    def _order_points(self, pts: np.ndarray) -> np.ndarray:
        """Order points in clockwise order starting from top-left"""
        rect = np.zeros((4, 2), dtype="float32")
        
        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]
        
        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]
        
        return rect
    
    def analyze_readability(self, img: np.ndarray) -> dict:
        """Analyze image readability characteristics"""
        try:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calculate Laplacian variance (focus/blur metric)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Calculate contrast
            contrast = gray.std()
            
            # Calculate brightness
            brightness = gray.mean()
            
            # Calculate resolution
            height, width = img.shape[:2]
            dpi_estimate = max(height, width) / 4  # Rough estimate
            
            # Assess readability
            readability_score = 0
            issues = []
            
            if laplacian_var < 100:
                issues.append("Image is blurry")
                readability_score += 20
            elif laplacian_var < 500:
                issues.append("Image could be clearer")
                readability_score += 50
            else:
                readability_score += 100
            
            if contrast < 30:
                issues.append("Low contrast detected")
                readability_score += 20
            elif contrast < 60:
                issues.append("Medium contrast")
                readability_score += 60
            else:
                readability_score += 100
            
            if brightness < 50 or brightness > 200:
                issues.append("Lighting may be too dark or bright")
                readability_score += 30
            else:
                readability_score += 100
            
            # Normalize score to 0-100
            readability_score = min(100, int(readability_score / 3))
            
            return {
                "readability_score": readability_score,
                "laplacian_variance": laplacian_var,
                "contrast": contrast,
                "brightness": brightness,
                "resolution_dpi": dpi_estimate,
                "issues": issues
            }
        except Exception as e:
            logger.error(f"Error analyzing readability: {str(e)}")
            return {
                "readability_score": 0,
                "issues": [f"Error analyzing readability: {str(e)}"]
            }
    
    def create_preview(self, input_path: str, output_path: str, max_preview_size: int = 400) -> Tuple[bool, str]:
        """
        Create a thumbnail preview of the image
        Returns: (success, error_message)
        """
        try:
            img = cv2.imread(input_path)
            if img is None:
                return False, "Failed to read image"
            
            # Resize for preview
            height, width = img.shape[:2]
            ratio = min(max_preview_size / width, max_preview_size / height)
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            preview = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
            
            # Save preview
            success = cv2.imwrite(output_path, preview, [cv2.IMWRITE_JPEG_QUALITY, 85])
            return success, "" if success else "Failed to save preview"
        
        except Exception as e:
            logger.error(f"Error creating preview: {str(e)}")
            return False, f"Preview creation error: {str(e)}"


# Singleton instance
image_processor = ImageProcessor()
