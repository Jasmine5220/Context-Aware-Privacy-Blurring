import os
import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import json

# Get database connection string from environment variable
DATABASE_URL = os.environ.get('DATABASE_URL')

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    """User table for storing user profiles and preferences"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    settings = relationship("UserSetting", back_populates="user", cascade="all, delete-orphan")
    detection_sessions = relationship("DetectionSession", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(username='{self.username}')>"

class UserSetting(Base):
    """User settings for privacy preferences"""
    __tablename__ = 'user_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    setting_name = Column(String(50), nullable=False)
    setting_value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="settings")
    
    def __repr__(self):
        return f"<UserSetting(setting_name='{self.setting_name}')>"

class DetectionSession(Base):
    """Records of detection sessions"""
    __tablename__ = 'detection_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Relationships
    user = relationship("User", back_populates="detection_sessions")
    detections = relationship("Detection", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DetectionSession(id={self.id}, start_time='{self.start_time}')>"

class Detection(Base):
    """Individual object detections during a session"""
    __tablename__ = 'detections'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('detection_sessions.id'), nullable=False)
    object_type = Column(String(50), nullable=False)  # face, document, credit_card, license_plate, screen, text
    blur_method = Column(String(50))  # pixelate, gaussian, edge_preserving, none
    confidence = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    session = relationship("DetectionSession", back_populates="detections")
    
    def __repr__(self):
        return f"<Detection(object_type='{self.object_type}', blur_method='{self.blur_method}')>"

class BlurRule(Base):
    """Predefined blur rules for different contexts"""
    __tablename__ = 'blur_rules'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    rules = Column(JSON, nullable=False)  # JSON object mapping object_types to blur_methods
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_default = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<BlurRule(name='{self.name}')>"

class SensitiveKeywordList(Base):
    """Lists of sensitive keywords to detect"""
    __tablename__ = 'sensitive_keyword_lists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    keywords = Column(JSON, nullable=False)  # JSON array of keywords
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    is_default = Column(Boolean, default=False)
    
    def __repr__(self):
        return f"<SensitiveKeywordList(name='{self.name}')>"

class DatabaseManager:
    """Database manager class for handling common operations"""
    
    def __init__(self):
        """Initialize the database manager"""
        self.engine = engine
        self.Session = Session
        self.session = None
    
    def init_db(self):
        """Create all tables if they don't exist"""
        Base.metadata.create_all(self.engine)
    
    def drop_db(self):
        """Drop all tables - USE WITH CAUTION"""
        Base.metadata.drop_all(self.engine)
    
    def get_session(self):
        """Get a new database session"""
        if self.session is None:
            self.session = self.Session()
        return self.session
    
    def close_session(self):
        """Close the current session"""
        if self.session is not None:
            self.session.close()
            self.session = None
    
    def create_default_blur_rules(self):
        """Create default blur rules if they don't exist"""
        session = self.get_session()
        
        # Check if default rules already exist
        default_rule = session.query(BlurRule).filter_by(name="Default Privacy").first()
        if default_rule is None:
            # Create default rule
            default_rules = {
                'face': 'pixelate',
                'document': 'gaussian',
                'credit_card': 'pixelate',
                'license_plate': 'pixelate',
                'screen': 'edge_preserving',
                'text': 'gaussian'
            }
            
            default_rule = BlurRule(
                name="Default Privacy",
                description="Default privacy settings for general use",
                rules=default_rules,
                is_default=True
            )
            session.add(default_rule)
            
            # Create high privacy rule
            high_privacy_rules = {
                'face': 'pixelate',
                'document': 'pixelate',
                'credit_card': 'pixelate',
                'license_plate': 'pixelate',
                'screen': 'pixelate',
                'text': 'pixelate'
            }
            
            high_privacy_rule = BlurRule(
                name="High Privacy",
                description="Maximum privacy settings with pixelation for all objects",
                rules=high_privacy_rules,
                is_default=False
            )
            session.add(high_privacy_rule)
            
            # Create professional call rule
            professional_rules = {
                'face': 'none',
                'document': 'gaussian',
                'credit_card': 'pixelate',
                'license_plate': 'pixelate',
                'screen': 'edge_preserving',
                'text': 'gaussian'
            }
            
            professional_rule = BlurRule(
                name="Professional Call",
                description="Settings for professional video calls with face visible",
                rules=professional_rules,
                is_default=False
            )
            session.add(professional_rule)
            
            session.commit()
    
    def create_default_keyword_lists(self):
        """Create default sensitive keyword lists if they don't exist"""
        session = self.get_session()
        
        # Check if default list already exists
        default_list = session.query(SensitiveKeywordList).filter_by(name="Standard Keywords").first()
        if default_list is None:
            # Create default keyword list
            standard_keywords = [
                "confidential", "private", "secret", "password", 
                "visa", "mastercard", "american express", "cvv", 
                "ssn", "social security", "classified"
            ]
            
            default_list = SensitiveKeywordList(
                name="Standard Keywords",
                description="Standard set of sensitive keywords",
                keywords=standard_keywords,
                is_default=True
            )
            session.add(default_list)
            
            # Create financial keywords list
            financial_keywords = [
                "account number", "routing number", "pin", "balance", 
                "statement", "credit score", "loan", "mortgage", "investment",
                "tax id", "ein", "w2", "w-2", "1099", "bank account"
            ]
            
            financial_list = SensitiveKeywordList(
                name="Financial Keywords",
                description="Keywords related to financial information",
                keywords=financial_keywords,
                is_default=False
            )
            session.add(financial_list)
            
            # Create healthcare keywords list
            healthcare_keywords = [
                "patient", "diagnosis", "medical record", "prescription", 
                "treatment", "symptoms", "health insurance", "hipaa", 
                "doctor", "hospital", "medical id", "medication"
            ]
            
            healthcare_list = SensitiveKeywordList(
                name="Healthcare Keywords",
                description="Keywords related to healthcare information (HIPAA)",
                keywords=healthcare_keywords,
                is_default=False
            )
            session.add(healthcare_list)
            
            session.commit()
    
    def get_all_blur_rules(self):
        """Get all blur rules"""
        session = self.get_session()
        return session.query(BlurRule).all()
    
    def get_default_blur_rule(self):
        """Get the default blur rule"""
        session = self.get_session()
        return session.query(BlurRule).filter_by(is_default=True).first()
    
    def get_all_keyword_lists(self):
        """Get all sensitive keyword lists"""
        session = self.get_session()
        return session.query(SensitiveKeywordList).all()
    
    def get_default_keyword_list(self):
        """Get the default keyword list"""
        session = self.get_session()
        return session.query(SensitiveKeywordList).filter_by(is_default=True).first()
    
    def start_detection_session(self, user_id=None):
        """Start a new detection session"""
        session = self.get_session()
        
        # If no user_id provided, use anonymous user
        if user_id is None:
            anonymous_user = session.query(User).filter_by(username="anonymous").first()
            if anonymous_user is None:
                anonymous_user = User(username="anonymous")
                session.add(anonymous_user)
                session.commit()
            user_id = anonymous_user.id
        
        # Create new detection session
        detection_session = DetectionSession(user_id=user_id)
        session.add(detection_session)
        session.commit()
        
        return detection_session.id
    
    def log_detection(self, session_id, object_type, blur_method, confidence=None):
        """Log a detection during a session"""
        session = self.get_session()
        
        detection = Detection(
            session_id=session_id,
            object_type=object_type,
            blur_method=blur_method,
            confidence=confidence
        )
        session.add(detection)
        session.commit()
    
    def end_detection_session(self, session_id):
        """End a detection session and calculate duration"""
        session = self.get_session()
        
        detection_session = session.query(DetectionSession).get(session_id)
        if detection_session:
            end_time = datetime.datetime.utcnow()
            detection_session.end_time = end_time
            
            # Calculate duration in seconds
            duration = (end_time - detection_session.start_time).total_seconds()
            detection_session.duration_seconds = duration
            
            session.commit()
            
            return duration
        return None
    
    def get_detection_stats(self, session_id):
        """Get statistics for a detection session"""
        session = self.get_session()
        
        # Get all detections for the session
        detections = session.query(Detection).filter_by(session_id=session_id).all()
        
        # Count by object type
        stats = {}
        for detection in detections:
            obj_type = detection.object_type
            if obj_type not in stats:
                stats[obj_type] = 0
            stats[obj_type] += 1
        
        return stats

# Initialize database
def init_database():
    """Initialize the database with default values"""
    db_manager = DatabaseManager()
    db_manager.init_db()
    db_manager.create_default_blur_rules()
    db_manager.create_default_keyword_lists()
    db_manager.close_session()
    return db_manager

# Get a database manager instance
def get_db_manager():
    """Get a database manager instance"""
    return DatabaseManager()

# Check if this module is run directly
if __name__ == "__main__":
    print("Initializing database...")
    init_database()
    print("Database initialized successfully.")