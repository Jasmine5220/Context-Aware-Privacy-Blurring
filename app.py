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

# Load custom CSS
def load_css(file_path):
    with open(file_path, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# Try to load CSS, handle if file doesn't exist yet
try:
    load_css("assets/style.css")
except FileNotFoundError:
    st.warning("Custom styling not found. Using default styling.")

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
    
    # Add a version info and credits container that will be placed at the bottom
    footer_container = st.container()
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Controls")
        
        # Camera controls
        st.subheader("Camera")
        webcam_toggle = st.toggle("Activate Webcam", value=st.session_state.is_webcam_active, 
                                 help="Start your webcam to process real-time video")
        
        if not webcam_toggle:
            st.info("👆 Toggle the switch above to activate your webcam and start privacy protection", icon="📹")
        
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
        
        # Metrics/stats in a nice card format
        st.markdown("### Performance Metrics")
        metrics_container = st.container()
        metrics_container.markdown("""
        <style>
        .metric-card {
            border-radius: 10px;
            padding: 15px;
            background-color: #f0f2f6;
            margin-bottom: 10px;
            box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        }
        </style>
        """, unsafe_allow_html=True)
        
        with metrics_container:
            metrics_placeholder = st.empty()
    
    with col2:
        # Create tabbed interface for organization
        tab1, tab2, tab3 = st.tabs(["Detection Results", "How It Works", "Privacy Settings"])
        
        with tab1:
            # Detection results section
            detections_placeholder = st.empty()
        
        with tab2:
            # How it works section
            st.markdown("""
            ### Context-Aware Privacy Blurring System
            
            #### Step 1: Capture and Preprocess Video
            - Captures video stream from webcam
            - Applies preprocessing: grayscale, noise reduction, edge enhancement
            
            #### Step 2: Detect Sensitive Objects
            - Uses advanced object detection to identify:
              - 👤 Faces
              - 📄 Documents
              - 💳 Credit Cards / IDs
              - 🚘 License Plates
              - 🖥️ Screens
            
            #### Step 3: Text Analysis
            - Extracts text via Tesseract OCR
            - Analyzes it using NLP
            - Looks for sensitive keywords to trigger blurring
            
            #### Step 4: Adaptive Blurring
            - Applies blur based on customizable rules:
              - 🌫️ Gaussian Blur: good for documents
              - 🔲 Pixelation: best for faces, card numbers
              - 🖼️ Edge-Preserving Blur: preserves important details
            
            #### Step 5: Return the Stream
            - Streams the processed video back in real time
            - Updates statistics and detection counts
            """)
            
        with tab3:
            # Settings and privacy info
            st.markdown("### Privacy Information")
            st.info("""
            **Privacy Guarantee:** All video processing happens locally in your browser.
            No video data is sent to external servers or stored in any way.
            """)
            
            st.markdown("### Blur Types Explained")
            blur_types = {
                "Gaussian Blur": "Applies a smooth blur effect, good for documents",
                "Pixelation": "Creates a mosaic/pixel effect, good for faces",
                "Edge-Preserving": "Blurs while preserving important edges and details"
            }
            
            for blur_name, blur_desc in blur_types.items():
                st.markdown(f"**{blur_name}**: {blur_desc}")
                
            st.markdown("### Recommended Settings")
            st.markdown("""
            - **Faces**: Pixelate (preserves identity while hiding details)
            - **Documents**: Gaussian (completely obscures text)
            - **Credit Cards**: Pixelate or Gaussian (hides numbers)
            - **License Plates**: Pixelate (most effective for alphanumeric data)
            - **Screens**: Edge-Preserving (maintains UI elements while hiding content)
            """)
    
    # Video processing loop
    if st.session_state.is_webcam_active:
        # Start webcam with OpenCV
        cap = cv2.VideoCapture(0)
        
        if not cap.isOpened():
            st.error("Failed to connect to webcam. Please check your camera connection.", icon="🚫")
            # Add troubleshooting tips
            with st.expander("Camera Troubleshooting Tips"):
                st.markdown("""
                #### Troubleshooting Camera Connection:
                1. **Browser Permissions**: Ensure your browser has permission to access the camera
                2. **Connection**: Make sure your webcam is properly connected
                3. **Other Applications**: Close other applications that might be using the camera
                4. **Refresh**: Try refreshing the browser page
                5. **Device Selection**: If you have multiple cameras, try a different one
                """)
            # Show error image
            error_img = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_img, "Camera Connection Failed", (100, 240), cv2.FONT_HERSHEY_SIMPLEX, 
                        1, (255, 255, 255), 2)
            video_placeholder.image(error_img, channels="BGR", use_container_width=True)
            # Set session state to inactive so we don't keep trying
            st.session_state.is_webcam_active = False
            st.rerun()
            return
        
        # Set lower resolution for faster processing
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Add a success message
        st.sidebar.success("Camera connected successfully!", icon="✅")
        
        # Performance metrics
        frame_count = 0
        start_time = time.time()
        fps = 0
        processing_time = 0
        
        try:
            while st.session_state.is_webcam_active:
                # Read frame from webcam
                ret, frame = cap.read()
                
                if not ret:
                    st.error("Failed to get frame from webcam.", icon="🚫")
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
                video_placeholder.image(processed_frame, channels="BGR", use_container_width=True)
                
                # Display metrics
                metrics_cols = metrics_placeholder.columns(3)
                metrics_cols[0].metric("FPS", f"{fps:.1f}")
                metrics_cols[1].metric("Processing Time", f"{processing_time*1000:.1f} ms")
                
                # Count detected objects
                total_detected = 0
                for obj_list in detections.values():
                    total_detected += len(obj_list)
                
                metrics_cols[2].metric("Objects Detected", total_detected)
                
                # Display detections
                detection_text = "### Detected Objects:\n"
                if detections:
                    detection_items = []
                    for obj_type, obj_boxes in detections.items():
                        if len(obj_boxes) > 0:
                            icon = "👤" if obj_type == "face" else "📄" if obj_type == "document" else "💳" if obj_type == "credit_card" else "🚘" if obj_type == "license_plate" else "🖥️" if obj_type == "screen" else "📝"
                            detection_items.append(f"{icon} **{obj_type.title()}**: {len(obj_boxes)}")
                    
                    if detection_items:
                        detection_text += "\n".join(detection_items)
                    else:
                        detection_text += "No sensitive objects detected"
                else:
                    detection_text += "No sensitive objects detected"
                
                detections_placeholder.markdown(detection_text)
                
                # Small delay to reduce CPU usage
                time.sleep(0.01)
                
        except Exception as e:
            st.error(f"Error in video processing: {e}", icon="⚠️")
        
        finally:
            # Release webcam when done
            cap.release()
    else:
        # Display placeholder when webcam is not active
        placeholder_img = np.zeros((480, 640, 3), dtype=np.uint8)
        # Add gradient background
        for y in range(480):
            for x in range(640):
                placeholder_img[y, x] = [0, int(40 + (y/480)*30), int(70 + (y/480)*50)]
                
        # Add text
        cv2.putText(placeholder_img, "Context-Aware Privacy Blurring", (120, 200), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        cv2.putText(placeholder_img, "Activate webcam to start", (180, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (200, 200, 200), 2)
                   
        video_placeholder.image(placeholder_img, channels="BGR", use_container_width=True)
        
        # Display empty detection status
        detections_placeholder.markdown("""
        ### Waiting for webcam
        
        Toggle the switch in the sidebar to activate your webcam and start privacy protection.
        
        The system will detect and protect:
        - 👤 Faces
        - 📄 Documents
        - 💳 Credit Cards
        - 🚘 License Plates
        - 🖥️ Screens
        """)

    # Add application footer with version info and credits
    with footer_container:
        st.markdown("""---""")
        cols = st.columns([1, 2, 1])
        with cols[1]:
            st.markdown("""
            <div style="text-align: center; color: #666;">
                <p>
                    <b>Context-Aware Privacy Blurring</b><br>
                    Version 1.0.0 | © 2025<br>
                    Built with OpenCV, Streamlit, and Python
                </p>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
