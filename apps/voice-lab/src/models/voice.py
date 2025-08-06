"""
Voice Lab - Database Models
SQLAlchemy models for voice lab data structures
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()


class Voice(Base):
    """Voice model for storing voice configurations and metadata"""
    __tablename__ = "voices"
    
    voice_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    language = Column(String(10), nullable=False, default="en")
    gender = Column(String(10), nullable=False)  # male, female
    age = Column(String(20), nullable=False, default="young")  # young, middle_aged, elderly
    accent = Column(String(50), nullable=False, default="american")
    use_case = Column(String(50), nullable=False, default="general")
    category = Column(String(20), nullable=False, default="premade")  # premade, cloned, custom
    quality_score = Column(Float, nullable=False, default=85.0)
    settings = Column(JSON, nullable=False, default=lambda: {"stability": 0.7, "similarity_boost": 0.8, "style": 0.2})
    preview_url = Column(String(255))
    cost_per_char = Column(Float, nullable=False, default=0.00018)
    available_for_tiers = Column(JSON, nullable=False, default=lambda: ["free", "starter", "pro", "enterprise"])
    
    # Cloning specific fields
    clone_id = Column(String, nullable=True)  # Reference to cloning job
    source_audio_path = Column(String(500), nullable=True)
    training_data_path = Column(String(500), nullable=True)
    
    # Metadata
    created_by = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)
    
    # Relationships
    generations = relationship("Generation", back_populates="voice")
    tests = relationship("VoiceTest", back_populates="voice")
    usage_stats = relationship("VoiceUsage", back_populates="voice")
    feedback = relationship("VoiceFeedback", back_populates="voice")


class Generation(Base):
    """Generation model for tracking text-to-speech generations"""
    __tablename__ = "generations"
    
    generation_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    voice_id = Column(String, ForeignKey("voices.voice_id"), nullable=False)
    text = Column(Text, nullable=False)
    audio_file_path = Column(String(500), nullable=True)
    audio_url = Column(String(500), nullable=True)
    
    # Generation parameters
    settings = Column(JSON, nullable=True)
    format = Column(String(10), default="mp3")
    sample_rate = Column(Integer, default=22050)
    
    # Metrics
    character_count = Column(Integer, nullable=False)
    generation_time = Column(Float, nullable=True)  # Seconds
    cost = Column(Float, nullable=False, default=0.0)
    quality_score = Column(Float, nullable=True)
    
    # Status and metadata
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    voice = relationship("Voice", back_populates="generations")


class VoiceCloningJob(Base):
    """Voice cloning job tracking"""
    __tablename__ = "voice_cloning_jobs"
    
    clone_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    voice_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    language = Column(String(10), nullable=False, default="en")
    gender = Column(String(10), nullable=False)
    use_case = Column(String(50), nullable=False, default="general")
    
    # File paths
    audio_file_path = Column(String(500), nullable=False)
    processed_audio_path = Column(String(500), nullable=True)
    model_file_path = Column(String(500), nullable=True)
    
    # Processing status
    status = Column(String(20), default="processing")  # processing, completed, failed, cancelled
    progress = Column(Integer, default=0)  # 0-100
    current_step = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Results
    voice_id = Column(String, nullable=True)  # Generated voice ID
    quality_metrics = Column(JSON, nullable=True)
    similarity_score = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    estimated_completion = Column(DateTime, nullable=True)


class VoiceTest(Base):
    """Voice quality testing results"""
    __tablename__ = "voice_tests"
    
    test_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    voice_id = Column(String, ForeignKey("voices.voice_id"), nullable=False)
    user_id = Column(String, nullable=False)
    test_type = Column(String(50), nullable=False)  # quality, performance, ab_test, stress
    
    # Test configuration
    test_phrases = Column(JSON, nullable=False)
    metrics = Column(JSON, nullable=False)
    settings = Column(JSON, nullable=True)
    
    # Results
    results = Column(JSON, nullable=True)
    overall_score = Column(Float, nullable=True)
    clarity = Column(Float, nullable=True)
    naturalness = Column(Float, nullable=True)
    consistency = Column(Float, nullable=True)
    emotion_range = Column(Float, nullable=True)
    generation_time = Column(Float, nullable=True)
    
    # Status and metadata
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    recommendation = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    voice = relationship("Voice", back_populates="tests")


class BatchTest(Base):
    """Batch testing jobs"""
    __tablename__ = "batch_tests"
    
    batch_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    test_type = Column(String(50), nullable=False)  # batch_quality, ab_test, benchmark
    
    # Configuration
    voice_ids = Column(JSON, nullable=False)
    test_phrases = Column(JSON, nullable=False)
    metrics = Column(JSON, nullable=False)
    settings = Column(JSON, nullable=True)
    
    # Progress tracking
    status = Column(String(20), default="processing")
    total_voices = Column(Integer, nullable=False)
    completed_voices = Column(Integer, default=0)
    failed_voices = Column(Integer, default=0)
    progress = Column(Float, default=0.0)  # 0-100
    
    # Results
    results = Column(JSON, nullable=True)
    summary = Column(JSON, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)


class VoiceUsage(Base):
    """Voice usage statistics"""
    __tablename__ = "voice_usage"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    voice_id = Column(String, ForeignKey("voices.voice_id"), nullable=False)
    user_id = Column(String, nullable=False)
    
    # Usage metrics
    total_characters = Column(Integer, default=0)
    total_generations = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    avg_generation_time = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True)
    
    # Time tracking
    first_used = Column(DateTime, nullable=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    voice = relationship("Voice", back_populates="usage_stats")


class VoiceFeedback(Base):
    """User feedback and ratings for voices"""
    __tablename__ = "voice_feedback"
    
    feedback_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    voice_id = Column(String, ForeignKey("voices.voice_id"), nullable=False)
    user_id = Column(String, nullable=False)
    generation_id = Column(String, nullable=True)  # Optional link to specific generation
    
    # Feedback data
    rating = Column(Integer, nullable=False)  # 1-5 stars
    sentiment = Column(Float, nullable=True)  # -1 to 1
    feedback_text = Column(Text, nullable=True)
    categories = Column(JSON, nullable=True)  # ["quality", "naturalness", "suitability"]
    
    # Context
    use_case = Column(String(50), nullable=True)
    text_sample = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    is_anonymous = Column(Boolean, default=False)
    
    # Relationships
    voice = relationship("Voice", back_populates="feedback")


class VoiceAnalytics(Base):
    """Aggregated analytics data"""
    __tablename__ = "voice_analytics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    voice_id = Column(String, nullable=True)  # Null for global analytics
    user_id = Column(String, nullable=True)  # Null for system-wide analytics
    date = Column(DateTime, nullable=False)
    period = Column(String(20), nullable=False)  # daily, weekly, monthly
    
    # Usage metrics
    generations_count = Column(Integer, default=0)
    characters_count = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    total_cost = Column(Float, default=0.0)
    
    # Performance metrics
    avg_generation_time = Column(Float, nullable=True)
    avg_quality_score = Column(Float, nullable=True)
    success_rate = Column(Float, nullable=True)
    avg_rating = Column(Float, nullable=True)
    
    # Trend data
    growth_rate = Column(Float, nullable=True)
    trend_direction = Column(String(10), nullable=True)  # up, down, stable
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemSettings(Base):
    """System-wide settings and configuration"""
    __tablename__ = "system_settings"
    
    setting_id = Column(String, primary_key=True)
    category = Column(String(50), nullable=False)  # voice_lab, generation, cloning, etc.
    key = Column(String(100), nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String, nullable=True)


class UserPreferences(Base):
    """User-specific preferences for voice lab"""
    __tablename__ = "user_preferences"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, unique=True)
    
    # Preferences
    preferred_voices = Column(JSON, default=lambda: [])
    default_language = Column(String(10), default="en")
    default_voice_settings = Column(JSON, default=lambda: {"stability": 0.7, "similarity_boost": 0.8, "style": 0.2})
    auto_optimize = Column(Boolean, default=True)
    quality_threshold = Column(Float, default=85.0)
    
    # Notifications
    notification_settings = Column(JSON, default=lambda: {
        "generation_complete": True,
        "cloning_complete": True,
        "quality_alerts": True,
        "cost_alerts": True
    })
    
    # UI preferences
    ui_settings = Column(JSON, default=lambda: {
        "theme": "auto",
        "layout": "grid",
        "items_per_page": 20
    })
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class APIUsage(Base):
    """API usage tracking for billing and analytics"""
    __tablename__ = "api_usage"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False)
    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)
    
    # Request details
    voice_id = Column(String, nullable=True)
    generation_id = Column(String, nullable=True)
    characters_processed = Column(Integer, nullable=True)
    
    # Response details
    status_code = Column(Integer, nullable=False)
    response_time = Column(Float, nullable=True)  # Milliseconds
    cost = Column(Float, default=0.0)
    
    # Metadata
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)


class ErrorLog(Base):
    """Error logging for debugging and monitoring"""
    __tablename__ = "error_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=True)
    service = Column(String(50), default="voice-lab")
    endpoint = Column(String(200), nullable=True)
    
    # Error details
    error_type = Column(String(100), nullable=False)
    error_message = Column(Text, nullable=False)
    stack_trace = Column(Text, nullable=True)
    context = Column(JSON, nullable=True)
    
    # Severity and status
    severity = Column(String(20), default="error")  # info, warning, error, critical
    status = Column(String(20), default="open")  # open, investigating, resolved
    
    # Metadata
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String, nullable=True)


# Database helper functions
def create_tables(engine):
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def drop_tables(engine):
    """Drop all tables"""
    Base.metadata.drop_all(bind=engine)

def get_table_names():
    """Get list of all table names"""
    return [table.name for table in Base.metadata.tables.values()]
