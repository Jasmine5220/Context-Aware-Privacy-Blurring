# Context-Aware Privacy Blurring

AI-driven adaptive privacy protection system that automatically detects and selectively blurs sensitive content in real-time video streams.

## Features

- **Real-time Privacy Protection**: Automatically detects and blurs sensitive objects in live webcam feed
- **Multiple Object Detection**: Identifies faces, documents, credit cards, license plates, and screens
- **Adaptive Blurring**: Applies different blur techniques based on object type and context
- **Text Analysis**: Detects sensitive text using OCR and keyword matching
- **Profile-based Settings**: Choose from predefined blur profiles for different privacy needs
- **Statistics Tracking**: Logs detection sessions with detailed statistics
- **Database Storage**: Stores user preferences, blur rules, and detection data

## Requirements

- Python 3.10+
- PostgreSQL database
- Web camera

## Dependencies

- OpenCV
- Streamlit
- SQLAlchemy
- NumPy
- pytesseract
- psycopg2

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/context-aware-privacy-blurring.git
   cd context-aware-privacy-blurring
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up PostgreSQL database and environment variables:
   - Create a PostgreSQL database
   - Set environment variables: DATABASE_URL, PGUSER, PGPASSWORD, PGDATABASE, PGHOST, PGPORT

4. Initialize the database:
   ```
   python init_db.py
   ```

5. Run the application:
   ```
   streamlit run app.py
   ```

## Usage

1. Open the application in your browser
2. Toggle "Activate Webcam" in the sidebar to start the privacy protection
3. Select a blur profile from the dropdown menu
4. Customize individual blur settings as needed
5. Choose a keyword list for sensitive text detection
6. View detection statistics and session data

## Project Structure

- `app.py`: Main Streamlit application
- `init_db.py`: Database initialization script
- `utils/`: Utility modules
  - `blur_techniques.py`: Different blur algorithms
  - `database.py`: Database models and operations
  - `object_detector.py`: Object detection implementation
  - `text_analyzer.py`: Text extraction and analysis
  - `video_processor.py`: Video processing pipeline

## Privacy Note

All processing happens locally on your device. No video data is sent to external servers or stored permanently.

## License

[MIT License](LICENSE)