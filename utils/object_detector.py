import cv2
import numpy as np
import os

class ObjectDetector:
    def __init__(self):
        """
        Initialize the object detector using OpenCV.
        """
        try:
            # Use Haar cascades for face detection
            self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            print("Face detection model loaded successfully")
            self.model = None
        except Exception as e:
            print(f"Error loading face detection model: {e}")
            self.face_cascade = None
            self.model = None
        
        # YOLO class to object type mapping
        self.class_mapping = {
            0: 'person',  # person can be used to detect faces
            57: 'document',  # chair (repurposing as document)
            62: 'screen',  # tv (can be used for screens)
            63: 'laptop',  # laptop (can be used for screens)
            67: 'document',  # cell phone (can detect phones/cards)
            73: 'document'  # book (can be used for documents)
        }
        
        # Confidence threshold
        self.confidence = 0.5
    
    def set_confidence(self, confidence):
        """Set the detection confidence threshold."""
        self.confidence = confidence
    
    def detect(self, frame, confidence=None):
        """
        Detect sensitive objects in the frame.
        
        Args:
            frame: Input video frame
            confidence: Detection confidence threshold
            
        Returns:
            Dictionary mapping object types to bounding boxes
        """
        if confidence is not None:
            self.confidence = confidence
        
        results = {}
        
        # Initialize default object types
        for obj_type in ['face', 'document', 'credit_card', 'license_plate', 'screen']:
            results[obj_type] = []
        
        # If YOLO model is available, use it
        if self.model is not None:
            try:
                # Run YOLOv8 inference on the frame
                detections = self.model(frame, conf=self.confidence)[0]
                
                # Process YOLOv8 detections
                for detection in detections.boxes.data.tolist():
                    x1, y1, x2, y2, conf, class_id = detection
                    
                    if conf < self.confidence:
                        continue
                    
                    # Map YOLO class to our object type
                    obj_type = self.class_mapping.get(int(class_id))
                    
                    if obj_type == 'person':
                        # For persons, extract face region (upper 1/3 of bounding box)
                        face_height = (y2 - y1) // 3
                        results['face'].append([int(x1), int(y1), int(x2), int(y1 + face_height)])
                    elif obj_type:
                        # Store detection in the appropriate category
                        if obj_type == 'document':
                            # Check aspect ratio to differentiate between documents and credit cards
                            width, height = x2 - x1, y2 - y1
                            aspect_ratio = width / height if height > 0 else 0
                            
                            if 1.4 <= aspect_ratio <= 1.7:
                                results['credit_card'].append([int(x1), int(y1), int(x2), int(y2)])
                            else:
                                results['document'].append([int(x1), int(y1), int(x2), int(y2)])
                        else:
                            results[obj_type].append([int(x1), int(y1), int(x2), int(y2)])
                
                # Additional license plate detection using edge detection and contour analysis
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 100, 200)
                contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
                
                for contour in contours:
                    # License plates typically have a rectangular shape
                    peri = cv2.arcLength(contour, True)
                    approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
                    
                    if len(approx) == 4:  # Rectangular shape
                        x, y, w, h = cv2.boundingRect(contour)
                        aspect_ratio = float(w) / h
                        
                        # License plates typically have an aspect ratio around 4.5:1
                        if 2 <= aspect_ratio <= 6 and w > 60 and h > 20:
                            results['license_plate'].append([x, y, x + w, y + h])
            
            except Exception as e:
                print(f"Error in YOLO detection: {e}")
                # Fallback to OpenCV face detection
                self._fallback_face_detection(frame, results)
        else:
            # Fallback to OpenCV face detection if YOLO is not available
            self._fallback_face_detection(frame, results)
            
            # Simple heuristic document detection based on edge detection
            self._detect_documents_and_cards(frame, results)
        
        return results
    
    def _fallback_face_detection(self, frame, results):
        """Fallback method for face detection using OpenCV."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in faces:
            results['face'].append([x, y, x + w, y + h])
    
    def _detect_documents_and_cards(self, frame, results):
        """Simple heuristic-based detection for documents and cards."""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply blur and edge detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Check if contour has 4 corners (rectangular)
            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)
            
            if len(approx) == 4:
                x, y, w, h = cv2.boundingRect(contour)
                
                # Skip small contours
                if w < 50 or h < 50:
                    continue
                
                aspect_ratio = float(w) / h
                
                # Credit card aspect ratio is typically around 1.6:1
                if 1.4 <= aspect_ratio <= 1.7:
                    results['credit_card'].append([x, y, x + w, y + h])
                # Document aspect ratio varies but is usually between 0.7:1 (portrait) and 1.4:1 (landscape)
                elif 0.7 <= aspect_ratio <= 1.4 and w > 100 and h > 100:
                    results['document'].append([x, y, x + w, y + h])
                # Screens typically have wider aspect ratios
                elif 1.7 < aspect_ratio <= 2.5:
                    results['screen'].append([x, y, x + w, y + h])
                # License plates typically have wider aspect ratios
                elif aspect_ratio > 2.5:
                    results['license_plate'].append([x, y, x + w, y + h])
