import streamlit as st
import cv2
import numpy as np
import time
import json
from utils.video_processor import VideoProcessor
from utils.object_detector import ObjectDetector
from utils.text_analyzer import TextAnalyzer
from utils.blur_techniques import BlurTechniques
from utils.database import get_db_manager
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

# Initialize database manager
if 'db_manager' not in st.session_state:
    st.session_state.db_manager = get_db_manager()

# Initialize session state
if 'processor' not in st.session_state:
    object_detector = ObjectDetector()
    text_analyzer = TextAnalyzer()
    blur_techniques = BlurTechniques()
    st.session_state.processor = VideoProcessor(object_detector, text_analyzer, blur_techniques)

if 'is_webcam_active' not in st.session_state:
    st.session_state.is_webcam_active = False

if 'detection_session_id' not in st.session_state:
    st.session_state.detection_session_id = None

if 'blur_rules' not in st.session_state:
    # Get default blur rules from database
    try:
        default_rule = st.session_state.db_manager.get_default_blur_rule()
        if default_rule:
            st.session_state.blur_rules = default_rule.rules
        else:
            # Fallback to hardcoded defaults if database doesn't have them
            st.session_state.blur_rules = {
                'face': 'pixelate',
                'document': 'gaussian',
                'credit_card': 'pixelate',
                'license_plate': 'pixelate',
                'screen': 'edge_preserving',
                'text': 'gaussian'
            }
    except Exception as e:
        st.warning(f"Failed to load blur rules from database: {e}. Using defaults.")
        st.session_state.blur_rules = {
            'face': 'pixelate',
            'document': 'gaussian',
            'credit_card': 'pixelate',
            'license_plate': 'pixelate',
            'screen': 'edge_preserving',
            'text': 'gaussian'
        }

if 'sensitive_keywords' not in st.session_state:
    # Get default keywords from database
    try:
        default_list = st.session_state.db_manager.get_default_keyword_list()
        if default_list:
            st.session_state.sensitive_keywords = default_list.keywords
        else:
            # Fallback to hardcoded defaults
            st.session_state.sensitive_keywords = [
                "confidential", "private", "secret", "password", 
                "visa", "mastercard", "american express", "cvv", 
                "ssn", "social security", "classified"
            ]
    except Exception as e:
        st.warning(f"Failed to load sensitive keywords from database: {e}. Using defaults.")
        st.session_state.sensitive_keywords = [
            "confidential", "private", "secret", "password", 
            "visa", "mastercard", "american express", "cvv", 
            "ssn", "social security", "classified"
        ]

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
        
        # Get predefined blur rules from database
        blur_rules = st.session_state.db_manager.get_all_blur_rules()
        blur_rule_names = [rule.name for rule in blur_rules]
        default_rule = st.session_state.db_manager.get_default_blur_rule()
        default_index = 0
        if default_rule and default_rule.name in blur_rule_names:
            default_index = blur_rule_names.index(default_rule.name)
        
        # Add a profile selector for predefined blur settings
        selected_rule_name = st.selectbox(
            "Blur Profile",
            options=blur_rule_names,
            index=default_index,
            help="Select a predefined blur profile or customize below"
        )
        
        # Update blur rules based on selection
        selected_rule = next((rule for rule in blur_rules if rule.name == selected_rule_name), None)
        if selected_rule:
            st.session_state.blur_rules = selected_rule.rules
            
            # Show a description if available
            if selected_rule.description:
                st.info(selected_rule.description)
        
        # Object blur methods with values from selected profile
        st.markdown("#### Customize Blur Methods")
        with st.expander("Customize Individual Blur Settings"):
            # Face blur
            face_options = ["pixelate", "gaussian", "edge_preserving", "none"]
            face_index = 0
            if 'face' in st.session_state.blur_rules:
                if st.session_state.blur_rules['face'] in face_options:
                    face_index = face_options.index(st.session_state.blur_rules['face'])
            
            st.session_state.blur_rules['face'] = st.selectbox(
                "Face Blur Method",
                options=face_options,
                index=face_index
            )
            
            # Document blur
            doc_options = ["gaussian", "pixelate", "edge_preserving", "none"]
            doc_index = 0
            if 'document' in st.session_state.blur_rules:
                if st.session_state.blur_rules['document'] in doc_options:
                    doc_index = doc_options.index(st.session_state.blur_rules['document'])
                    
            st.session_state.blur_rules['document'] = st.selectbox(
                "Document Blur Method",
                options=doc_options,
                index=doc_index
            )
            
            # Credit card blur
            cc_options = ["pixelate", "gaussian", "edge_preserving", "none"]
            cc_index = 0
            if 'credit_card' in st.session_state.blur_rules:
                if st.session_state.blur_rules['credit_card'] in cc_options:
                    cc_index = cc_options.index(st.session_state.blur_rules['credit_card'])
                    
            st.session_state.blur_rules['credit_card'] = st.selectbox(
                "Credit Card Blur Method",
                options=cc_options,
                index=cc_index
            )
            
            # License plate blur
            lp_options = ["pixelate", "gaussian", "edge_preserving", "none"]
            lp_index = 0
            if 'license_plate' in st.session_state.blur_rules:
                if st.session_state.blur_rules['license_plate'] in lp_options:
                    lp_index = lp_options.index(st.session_state.blur_rules['license_plate'])
                    
            st.session_state.blur_rules['license_plate'] = st.selectbox(
                "License Plate Blur Method",
                options=lp_options,
                index=lp_index
            )
            
            # Screen blur
            screen_options = ["edge_preserving", "gaussian", "pixelate", "none"]
            screen_index = 0
            if 'screen' in st.session_state.blur_rules:
                if st.session_state.blur_rules['screen'] in screen_options:
                    screen_index = screen_options.index(st.session_state.blur_rules['screen'])
                    
            st.session_state.blur_rules['screen'] = st.selectbox(
                "Screen Blur Method",
                options=screen_options,
                index=screen_index
            )
            
            # Text blur
            text_options = ["gaussian", "pixelate", "edge_preserving", "none"]
            text_index = 0
            if 'text' in st.session_state.blur_rules:
                if st.session_state.blur_rules['text'] in text_options:
                    text_index = text_options.index(st.session_state.blur_rules['text'])
                    
            st.session_state.blur_rules['text'] = st.selectbox(
                "Sensitive Text Blur Method",
                options=text_options,
                index=text_index
            )
        
        # Update blur rules
        st.session_state.processor.set_blur_rules(st.session_state.blur_rules)
        
        # Text detection settings
        st.subheader("Text Detection")
        
        # Show dropdown to select a keyword list from database
        keyword_lists = st.session_state.db_manager.get_all_keyword_lists()
        keyword_list_names = [kl.name for kl in keyword_lists]
        default_keyword_list = st.session_state.db_manager.get_default_keyword_list()
        default_index = 0
        if default_keyword_list and default_keyword_list.name in keyword_list_names:
            default_index = keyword_list_names.index(default_keyword_list.name)
        
        selected_keyword_list = st.selectbox(
            "Keyword List",
            options=keyword_list_names,
            index=default_index,
            help="Select a predefined list of sensitive keywords to detect"
        )
        
        # Get selected keyword list
        selected_list = next((kl for kl in keyword_lists if kl.name == selected_keyword_list), None)
        if selected_list:
            # Show keywords as comma-separated in text area
            keyword_str = ", ".join(selected_list.keywords)
            sensitive_keywords = st.text_area(
                "Sensitive Keywords (comma separated)",
                value=keyword_str,
                help="Add or remove keywords as needed. These will be detected in text content."
            )
            # Update processor with the keywords
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
        
        # Start a new detection session in the database
        if not st.session_state.detection_session_id:
            try:
                st.session_state.detection_session_id = st.session_state.db_manager.start_detection_session()
                st.sidebar.success(f"Started new detection session (ID: {st.session_state.detection_session_id})", icon="🔄")
            except Exception as e:
                st.sidebar.warning(f"Could not start database session: {e}")
        
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
                
                # Log detections to database (every 10 frames to reduce DB load)
                if frame_count % 10 == 0 and st.session_state.detection_session_id:
                    try:
                        for obj_type, obj_boxes in detections.items():
                            if len(obj_boxes) > 0:
                                # Get blur method used for this object type
                                blur_method = st.session_state.blur_rules.get(obj_type, 'none')
                                
                                # Log each detection
                                for _ in range(len(obj_boxes)):
                                    st.session_state.db_manager.log_detection(
                                        st.session_state.detection_session_id,
                                        obj_type,
                                        blur_method
                                    )
                    except Exception as e:
                        # Silently ignore database errors to keep processing frames
                        pass
                
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
            
            # End detection session in database
            if st.session_state.detection_session_id:
                try:
                    duration = st.session_state.db_manager.end_detection_session(st.session_state.detection_session_id)
                    st.sidebar.success(f"Detection session completed ({duration:.1f} seconds)", icon="✅")
                    
                    # Get detection stats
                    stats = st.session_state.db_manager.get_detection_stats(st.session_state.detection_session_id)
                    if stats:
                        st.sidebar.info(f"**Detection Summary:**\n" + "\n".join([f"- {k}: {v}" for k, v in stats.items()]))
                    
                    # Reset session ID for next time
                    st.session_state.detection_session_id = None
                except Exception as e:
                    st.sidebar.warning(f"Could not finalize database session: {e}")
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
