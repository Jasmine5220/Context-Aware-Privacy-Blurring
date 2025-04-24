import cv2
import numpy as np
from .object_detector import ObjectDetector
from .text_analyzer import TextAnalyzer
from .blur_techniques import BlurTechniques

class VideoProcessor:
    def __init__(self, object_detector, text_analyzer, blur_techniques):
        """
        Initialize the VideoProcessor with the required components.
        
        Args:
            object_detector: Instance of ObjectDetector for detecting sensitive objects
            text_analyzer: Instance of TextAnalyzer for extracting and analyzing text
            blur_techniques: Instance of BlurTechniques for applying different blur methods
        """
        self.object_detector = object_detector
        self.text_analyzer = text_analyzer
        self.blur_techniques = blur_techniques
        self.detection_confidence = 0.5
        self.blur_rules = {
            'face': 'pixelate',
            'document': 'gaussian',
            'credit_card': 'pixelate',
            'license_plate': 'pixelate',
            'screen': 'edge_preserving',
            'text': 'gaussian'
        }
        self.sensitive_keywords = [
            'confidential', 'private', 'secret', 'password', 
            'visa', 'mastercard', 'american express', 'cvv', 'ssn', 'social security'
        ]
    
    def set_detection_confidence(self, confidence):
        """Set the detection confidence threshold."""
        self.detection_confidence = confidence
        self.object_detector.set_confidence(confidence)
    
    def set_blur_rules(self, rules):
        """Set the blur rules for different object types."""
        self.blur_rules = rules
    
    def set_sensitive_keywords(self, keywords):
        """Set the list of sensitive keywords to look for in text."""
        self.sensitive_keywords = keywords
        self.text_analyzer.set_sensitive_keywords(keywords)
    
    def preprocess_frame(self, frame):
        """
        Preprocess the video frame for better detection.
        
        Args:
            frame: Input video frame
            
        Returns:
            Preprocessed frame
        """
        # Convert to grayscale for text detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply slight Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Apply adaptive thresholding to enhance text
        thresh = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY_INV, 11, 2
        )
        
        return frame, gray, thresh
    
    def process_frame(self, frame):
        """
        Process a video frame to detect and blur sensitive content.
        
        Args:
            frame: Input video frame
            
        Returns:
            Processed frame with sensitive content blurred,
            Dictionary with detection counts
        """
        # Make a copy of the frame to avoid modifying the original
        processed_frame = frame.copy()
        
        # Preprocess the frame
        _, gray, thresh = self.preprocess_frame(frame)
        
        # Detect objects in the frame
        detected_objects = self.object_detector.detect(frame, self.detection_confidence)
        
        # Extract text from the frame
        text_regions = self.text_analyzer.extract_text(gray)
        
        # Dictionary to track detection counts
        detection_counts = {}
        
        # Process detected objects
        for obj_type, boxes in detected_objects.items():
            detection_counts[obj_type] = len(boxes)
            
            # Skip if blur is set to "none"
            if self.blur_rules.get(obj_type, 'none') == 'none':
                continue
            
            # Apply appropriate blur for each detected object
            for box in boxes:
                x1, y1, x2, y2 = box
                region = processed_frame[y1:y2, x1:x2]
                
                if region.size == 0:  # Skip empty regions
                    continue
                
                # Apply the blur method specified in the rules
                blur_method = self.blur_rules.get(obj_type, 'gaussian')
                
                if blur_method == 'gaussian':
                    blurred = self.blur_techniques.gaussian_blur(region)
                elif blur_method == 'pixelate':
                    blurred = self.blur_techniques.pixelate(region)
                elif blur_method == 'edge_preserving':
                    blurred = self.blur_techniques.edge_preserving_blur(region)
                else:
                    blurred = region  # No blur
                
                # Replace the region with the blurred version
                processed_frame[y1:y2, x1:x2] = blurred
        
        # Process text regions for sensitive information
        sensitive_text_found = False
        for (text, box) in text_regions:
            if self.text_analyzer.is_sensitive_text(text):
                sensitive_text_found = True
                
                x, y, w, h = box
                text_region = processed_frame[y:y+h, x:x+w]
                
                if text_region.size == 0:  # Skip empty regions
                    continue
                
                # Apply the blur method specified for text
                blur_method = self.blur_rules.get('text', 'gaussian')
                
                if blur_method == 'gaussian':
                    blurred = self.blur_techniques.gaussian_blur(text_region)
                elif blur_method == 'pixelate':
                    blurred = self.blur_techniques.pixelate(text_region)
                elif blur_method == 'edge_preserving':
                    blurred = self.blur_techniques.edge_preserving_blur(text_region)
                else:
                    blurred = text_region  # No blur
                
                # Replace the region with the blurred version
                processed_frame[y:y+h, x:x+w] = blurred
        
        detection_counts['sensitive_text'] = 1 if sensitive_text_found else 0
        
        return processed_frame, detection_counts
