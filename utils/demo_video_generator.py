import cv2
import numpy as np
import os

class DemoVideoGenerator:
    def __init__(self):
        """
        Initialize the demo video generator with default parameters.
        """
        self.width = 640
        self.height = 480
        self.frame_count = 0
        
        # Create assets directory if it doesn't exist
        if not os.path.exists('assets'):
            os.makedirs('assets')
            
        # Try to load face image
        self.face_img = None
        try:
            face_path = 'assets/face.png'
            if not os.path.exists(face_path):
                # Create a simple face placeholder
                self.face_img = self._create_face_placeholder()
            else:
                self.face_img = cv2.imread(face_path, cv2.IMREAD_UNCHANGED)
                if self.face_img.shape[2] == 4:  # If has alpha channel
                    # Convert RGBA to RGB
                    alpha = self.face_img[:, :, 3] / 255.0
                    self.face_img = self.face_img[:, :, :3]
                    for c in range(3):
                        self.face_img[:, :, c] = self.face_img[:, :, c] * alpha
        except Exception as e:
            print(f"Error loading face image: {e}")
            self.face_img = self._create_face_placeholder()
            
        # Create document placeholder
        self.document_img = self._create_document_placeholder()
        
        # Create credit card placeholder
        self.card_img = self._create_credit_card_placeholder()
        
        # Create screen placeholder
        self.screen_img = self._create_screen_placeholder()
        
        # Animation parameters
        self.face_pos = [50, 100]
        self.face_direction = [1, 1]  # Direction of movement
        self.face_speed = [2, 1]
        
        self.document_pos = [300, 200]
        self.card_pos = [400, 300]
        self.screen_pos = [100, 300]
    
    def _create_face_placeholder(self):
        """Create a simple face placeholder"""
        face = np.zeros((100, 100, 3), dtype=np.uint8)
        face.fill(200)  # Light gray background
        
        # Draw a simple face
        cv2.circle(face, (50, 50), 40, (0, 0, 255), -1)  # Face
        cv2.circle(face, (35, 35), 5, (255, 255, 255), -1)  # Left eye
        cv2.circle(face, (65, 35), 5, (255, 255, 255), -1)  # Right eye
        cv2.ellipse(face, (50, 65), (20, 10), 0, 0, 180, (255, 255, 255), -1)  # Mouth
        
        return face
    
    def _create_document_placeholder(self):
        """Create a document placeholder with text"""
        doc = np.ones((150, 220, 3), dtype=np.uint8) * 255  # White background
        
        # Add header
        cv2.rectangle(doc, (0, 0), (220, 30), (230, 230, 230), -1)
        cv2.putText(doc, "CONFIDENTIAL DOCUMENT", (10, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        # Add lines of "text"
        for i in range(6):
            y = 50 + i * 15
            cv2.line(doc, (10, y), (210, y), (200, 200, 200), 1)
        
        # Add footer with sensitive info
        cv2.rectangle(doc, (0, 120), (220, 150), (230, 230, 230), -1)
        cv2.putText(doc, "SSN: 123-45-6789", (10, 135), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        return doc
    
    def _create_credit_card_placeholder(self):
        """Create a credit card placeholder"""
        card = np.ones((85, 130, 3), dtype=np.uint8) * 230  # Light blue background
        
        # Card border
        cv2.rectangle(card, (0, 0), (129, 84), (0, 0, 0), 1)
        
        # Bank logo
        cv2.rectangle(card, (10, 10), (50, 30), (0, 120, 255), -1)
        
        # Chip
        cv2.rectangle(card, (10, 40), (30, 50), (255, 215, 0), -1)
        
        # Card number
        cv2.putText(card, "XXXX XXXX XXXX 1234", (10, 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)
        
        return card
    
    def _create_screen_placeholder(self):
        """Create a screen/monitor placeholder"""
        screen = np.zeros((120, 160, 3), dtype=np.uint8)
        
        # Monitor frame
        cv2.rectangle(screen, (0, 0), (159, 99), (120, 120, 120), 2)
        
        # Screen content - blue background
        cv2.rectangle(screen, (2, 2), (157, 97), (255, 200, 0), -1)
        
        # Add some "content"
        cv2.putText(screen, "PRIVATE", (50, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        # Add text lines
        for i in range(3):
            y = 50 + i * 15
            cv2.line(screen, (20, y), (140, y), (255, 255, 255), 1)
        
        # Add stand
        cv2.rectangle(screen, (70, 100), (90, 119), (80, 80, 80), -1)
        
        return screen
    
    def get_frame(self):
        """
        Generate a frame for the demo video.
        
        Returns:
            Synthetic frame with animated objects
        """
        # Create background
        frame = np.ones((self.height, self.width, 3), dtype=np.uint8) * 240  # Light gray background
        
        # Animate face position
        self.face_pos[0] += self.face_speed[0] * self.face_direction[0]
        self.face_pos[1] += self.face_speed[1] * self.face_direction[1]
        
        # Bounce off edges
        if self.face_pos[0] <= 0 or self.face_pos[0] >= self.width - self.face_img.shape[1]:
            self.face_direction[0] *= -1
        if self.face_pos[1] <= 0 or self.face_pos[1] >= self.height - self.face_img.shape[0]:
            self.face_direction[1] *= -1
        
        # Place objects on the frame
        self._place_object(frame, self.face_img, self.face_pos)
        self._place_object(frame, self.document_img, self.document_pos)
        self._place_object(frame, self.card_img, self.card_pos)
        self._place_object(frame, self.screen_img, self.screen_pos)
        
        # Add frame counter
        self.frame_count += 1
        cv2.putText(frame, f"Demo Video Frame #{self.frame_count}", (10, 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return frame
    
    def _place_object(self, frame, obj, pos):
        """Place an object on the frame at the specified position"""
        x, y = pos
        h, w = obj.shape[:2]
        
        # Ensure the object is within frame boundaries
        x_end = min(x + w, frame.shape[1])
        y_end = min(y + h, frame.shape[0])
        w = x_end - x
        h = y_end - y
        
        if w <= 0 or h <= 0 or x >= frame.shape[1] or y >= frame.shape[0]:
            return  # Object is outside the frame
        
        # Place the object on the frame
        frame[y:y+h, x:x+w] = obj[:h, :w]
    
    def release(self):
        """Clean up resources"""
        pass  # No resources to clean up for the demo generator