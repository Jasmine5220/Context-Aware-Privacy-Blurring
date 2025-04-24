import streamlit as st
import cv2
import numpy as np
import time
from utils.video_processor import VideoProcessor
from utils.object_detector import ObjectDetector
from utils.text_analyzer import TextAnalyzer
from utils.blur_techniques import BlurTechniques
import os

# Page configuration
st.set_page_config(
    page_title="Context-Aware Privacy Blurring",
    page_icon="🔒",
    layout="wide"
)

# Initialize session state
if 'processor' not in st.session_state:
    object_detector = ObjectDetector()
    text_analyzer = TextAnalyzer()
    blur_techniques = BlurTechniques()
    st.session_state.processor = VideoProcessor(object_detector, text_analyzer, blur_techniques)

if 'is_webcam_active' not in st.session_state:
    st.session_state.is_webcam_active = False

if 'blur_rules' not in st.session_state:
    # Default blur rules (object_type: blur_type)
    st.session_state.blur_rules = {
        'face': 'pixelate',
        'document': 'gaussian',
        'credit_card': 'pixelate',
        'license_plate': 'pixelate',
        'screen': 'edge_preserving',
        'text': 'gaussian'
    }

def main():
    # Title and description
    st.title("Context-Aware Privacy Blurring")
    st.markdown("AI-Driven Adaptive Privacy Protection in Real Time")
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Controls")
        
        # Camera controls
        st.subheader("Camera")
        webcam_toggle = st.toggle("Activate Webcam", value=st.session_state.is_webcam_active)
        
        if webcam_toggle != st.session_state.is_webcam_active:
            st.session_state.is_webcam_active = webcam_toggle
            st.rerun()
        
        # Detection settings
        st.subheader("Detection Settings")
        detection_confidence = st.slider("Detection Confidence", 0.0, 1.0, 0.5, 0.05)
        st.session_state.processor.set_detection_confidence(detection_confidence)
        
        # Blur settings
        st.subheader("Blur Settings")
        
        # Object blur methods
        st.session_state.blur_rules['face'] = st.selectbox(
            "Face Blur Method",
            options=["pixelate", "gaussian", "edge_preserving", "none"],
            index=0
        )
        
        st.session_state.blur_rules['document'] = st.selectbox(
            "Document Blur Method",
            options=["gaussian", "pixelate", "edge_preserving", "none"],
            index=0
        )
        
        st.session_state.blur_rules['credit_card'] = st.selectbox(
            "Credit Card Blur Method",
            options=["pixelate", "gaussian", "edge_preserving", "none"],
            index=0
        )
        
        st.session_state.blur_rules['license_plate'] = st.selectbox(
            "License Plate Blur Method",
            options=["pixelate", "gaussian", "edge_preserving", "none"],
            index=0
        )
        
        st.session_state.blur_rules['screen'] = st.selectbox(
            "Screen Blur Method",
            options=["edge_preserving", "gaussian", "pixelate", "none"],
            index=0
        )
        
        st.session_state.blur_rules['text'] = st.selectbox(
            "Sensitive Text Blur Method",
            options=["gaussian", "pixelate", "edge_preserving", "none"],
            index=0
        )
        
        # Update blur rules
        st.session_state.processor.set_blur_rules(st.session_state.blur_rules)
        
        # Text detection settings
        st.subheader("Text Detection")
        sensitive_keywords = st.text_area(
            "Sensitive Keywords (comma separated)",
            "confidential,private,secret,password,visa,mastercard,american express,cvv,ssn,social security"
        )
        st.session_state.processor.set_sensitive_keywords([kw.strip() for kw in sensitive_keywords.lower().split(',')])
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Video display
        st.header("Privacy-Protected Video Stream")
        video_placeholder = st.empty()
        
        # Metrics/stats
        metrics_placeholder = st.empty()
    
    with col2:
        # Detection results and information
        st.header("Detection Results")
        detections_placeholder = st.empty()
        
        # How it works section
        with st.expander("How It Works", expanded=False):
            st.markdown("""
            ### Context-Aware Privacy Blurring System
            
            #### Step 1: Capture and Preprocess Video
            - Captures video stream from webcam
            - Applies preprocessing: grayscale, noise reduction, edge enhancement
            
            #### Step 2: Detect Sensitive Objects
            - Uses YOLOv8 + OpenCV to detect:
              - Faces
              - Documents
              - Credit Cards / IDs
              - License Plates
              - Screens
            
            #### Step 3: Text Analysis
            - Extracts text via Tesseract OCR
            - Analyzes it using NLP
            - Looks for sensitive keywords to trigger blurring
            
            #### Step 4: Adaptive Blurring
            - Applies blur based on rules:
              - Gaussian Blur: documents
              - Pixelation: faces, card numbers
              - Edge-Preserving Blur: video calls
            
            #### Step 5: Return the Stream
            - Streams the processed video back in real time
            """)
    
    # Video processing loop
    if st.session_state.is_webcam_active:
        # Start webcam
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("Failed to open webcam. Please check your camera connection.")
            return
        
        # Set lower resolution for faster processing
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Performance metrics
        frame_count = 0
        start_time = time.time()
        fps = 0
        processing_time = 0
        
        try:
            while st.session_state.is_webcam_active:
                # Read frame
                ret, frame = cap.read()
                if not ret:
                    st.error("Failed to get frame from webcam.")
                    break
                
                # Process frame
                frame_processing_start = time.time()
                processed_frame, detections = st.session_state.processor.process_frame(frame)
                frame_processing_end = time.time()
                
                # Update metrics
                frame_count += 1
                processing_time = frame_processing_end - frame_processing_start
                
                if frame_count % 10 == 0:  # Update FPS every 10 frames
                    current_time = time.time()
                    elapsed = current_time - start_time
                    if elapsed > 0:
                        fps = frame_count / elapsed
                
                # Display processed frame
                video_placeholder.image(processed_frame, channels="BGR", use_column_width=True)
                
                # Display metrics
                metrics_placeholder.columns(3)[0].metric("FPS", f"{fps:.1f}")
                metrics_placeholder.columns(3)[1].metric("Processing Time", f"{processing_time*1000:.1f} ms")
                metrics_placeholder.columns(3)[2].metric("Objects Detected", len(detections))
                
                # Display detections
                detection_text = "### Detected Objects:\n"
                if detections:
                    for obj_type, count in detections.items():
                        if count > 0:
                            detection_text += f"- {obj_type.title()}: {count}\n"
                else:
                    detection_text += "No sensitive objects detected"
                
                detections_placeholder.markdown(detection_text)
                
                # Small delay to reduce CPU usage
                time.sleep(0.01)
                
        except Exception as e:
            st.error(f"Error in video processing: {e}")
        
        finally:
            # Release webcam when done
            cap.release()
    else:
        # Display placeholder when webcam is not active
        video_placeholder.image(np.zeros((480, 640, 3), dtype=np.uint8), channels="BGR", use_column_width=True)
        detections_placeholder.markdown("### Activate the webcam to start detecting and blurring sensitive content")

if __name__ == "__main__":
    main()
