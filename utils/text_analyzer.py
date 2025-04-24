import cv2
import numpy as np
import pytesseract
import re
import spacy
from spacy.lang.en import English

class TextAnalyzer:
    def __init__(self):
        """
        Initialize the text analyzer with OCR and NLP capabilities.
        """
        # Initialize Tesseract OCR
        try:
            # Test Tesseract availability
            pytesseract.get_tesseract_version()
            self.tesseract_available = True
        except Exception as e:
            print(f"Tesseract not available: {e}")
            self.tesseract_available = False
        
        # Initialize Spacy NLP
        try:
            self.nlp = spacy.blank("en")
            # Add the pipeline components
            self.nlp.add_pipe("sentencizer")
            self.nlp_available = True
        except Exception as e:
            print(f"Spacy NLP not available: {e}")
            self.nlp_available = False
            # Fallback to simple regex
            self.nlp = None
        
        # Sensitive keywords to look for
        self.sensitive_keywords = [
            'confidential', 'private', 'secret', 'password', 
            'visa', 'mastercard', 'american express', 'cvv', 'ssn', 'social security'
        ]
        
        # Regex patterns for sensitive information
        self.patterns = {
            'credit_card': r'\b(?:\d{4}[-\s]?){3}\d{4}\b',  # Credit card number pattern
            'ssn': r'\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b',  # SSN pattern
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email pattern
            'phone': r'\b(?:\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',  # Phone pattern
            'date': r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}\b'  # Date pattern
        }
    
    def set_sensitive_keywords(self, keywords):
        """Set the list of sensitive keywords to look for."""
        self.sensitive_keywords = keywords
    
    def extract_text(self, gray_frame):
        """
        Extract text from the frame using OCR.
        
        Args:
            gray_frame: Grayscale image
            
        Returns:
            List of tuples containing (text, bounding_box)
        """
        text_regions = []
        
        if not self.tesseract_available:
            return text_regions
        
        try:
            # Improve image for OCR
            # Apply adaptive thresholding to handle different lighting conditions
            thresh = cv2.adaptiveThreshold(
                gray_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 2
            )
            
            # OCR configuration for better text detection
            custom_config = r'--oem 3 --psm 11'
            
            # Get OCR data including bounding boxes
            ocr_data = pytesseract.image_to_data(thresh, config=custom_config, output_type=pytesseract.Output.DICT)
            
            # Process OCR results
            n_boxes = len(ocr_data['text'])
            for i in range(n_boxes):
                # Filter out empty results and low-confidence detections
                if int(ocr_data['conf'][i]) > 60 and ocr_data['text'][i].strip() != '':
                    # Extract bounding box
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    
                    # Store text and its bounding box
                    text_regions.append((ocr_data['text'][i], (x, y, w, h)))
            
        except Exception as e:
            print(f"Error in OCR: {e}")
        
        return text_regions
    
    def is_sensitive_text(self, text):
        """
        Analyze if the text contains sensitive information.
        
        Args:
            text: Text to analyze
            
        Returns:
            Boolean indicating if the text is sensitive
        """
        if not text or len(text) < 3:
            return False
        
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Check for sensitive keywords
        for keyword in self.sensitive_keywords:
            if keyword in text_lower:
                return True
        
        # Check for patterns of sensitive information
        for pattern_name, pattern in self.patterns.items():
            if re.search(pattern, text):
                return True
        
        # If NLP is available, use it for more sophisticated analysis
        if self.nlp_available:
            doc = self.nlp(text)
            
            # Check for named entities that might be sensitive
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "GPE"]:
                    return True
        
        return False
