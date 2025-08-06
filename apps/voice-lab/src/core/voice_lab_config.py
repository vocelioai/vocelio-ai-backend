"""
Voice Lab - Core Configuration
Environment variables and service settings
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings from environment variables"""
    
    # Service Configuration
    SERVICE_NAME: str = "voice-lab"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = Field(default="development", env="ENVIRONMENT")
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    HOST: str = Field(default="0.0.0.0", env="HOST")
    PORT: int = Field(default=8000, env="PORT")
    
    # Database Configuration
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=10, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    
    # Supabase Configuration
    SUPABASE_URL: str = Field(..., env="SUPABASE_URL")
    SUPABASE_KEY: str = Field(..., env="SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY: str = Field(..., env="SUPABASE_SERVICE_ROLE_KEY")
    
    # Authentication
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # External Services
    ELEVENLABS_API_KEY: str = Field(..., env="ELEVENLABS_API_KEY")
    ELEVENLABS_BASE_URL: str = Field(default="https://api.elevenlabs.io/v1", env="ELEVENLABS_BASE_URL")
    
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    
    # Internal Services
    AI_BRAIN_SERVICE_URL: str = Field(default="http://ai-brain:8000", env="AI_BRAIN_SERVICE_URL")
    API_GATEWAY_URL: str = Field(default="http://api-gateway:8000", env="API_GATEWAY_URL")
    
    # File Storage
    STATIC_FILES_PATH: str = Field(default="static", env="STATIC_FILES_PATH")
    MAX_FILE_SIZE: int = Field(default=10485760, env="MAX_FILE_SIZE")  # 10MB
    ALLOWED_AUDIO_FORMATS: List[str] = Field(default=["mp3", "wav", "m4a", "ogg"], env="ALLOWED_AUDIO_FORMATS")
    
    # Voice Generation Limits
    MAX_TEXT_LENGTH: int = Field(default=5000, env="MAX_TEXT_LENGTH")
    MAX_CONCURRENT_GENERATIONS: int = Field(default=10, env="MAX_CONCURRENT_GENERATIONS")
    GENERATION_TIMEOUT: int = Field(default=300, env="GENERATION_TIMEOUT")  # 5 minutes
    
    # Voice Cloning Configuration
    CLONING_ENABLED: bool = Field(default=True, env="CLONING_ENABLED")
    MIN_CLONING_DURATION: int = Field(default=60, env="MIN_CLONING_DURATION")  # seconds
    MAX_CLONING_DURATION: int = Field(default=600, env="MAX_CLONING_DURATION")  # 10 minutes
    CLONING_TIMEOUT: int = Field(default=1800, env="CLONING_TIMEOUT")  # 30 minutes
    
    # Quality and Performance
    DEFAULT_QUALITY_THRESHOLD: float = Field(default=85.0, env="DEFAULT_QUALITY_THRESHOLD")
    AUTO_OPTIMIZE_VOICES: bool = Field(default=True, env="AUTO_OPTIMIZE_VOICES")
    CACHE_GENERATED_AUDIO: bool = Field(default=True, env="CACHE_GENERATED_AUDIO")
    CACHE_DURATION_HOURS: int = Field(default=24, env="CACHE_DURATION_HOURS")
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, env="RATE_LIMIT_ENABLED")
    RATE_LIMIT_REQUESTS: int = Field(default=100, env="RATE_LIMIT_REQUESTS")
    RATE_LIMIT_WINDOW: int = Field(default=3600, env="RATE_LIMIT_WINDOW")  # 1 hour
    
    # Monitoring and Logging
    LOG_LEVEL: str = Field(default="INFO", env="LOG_LEVEL")
    ENABLE_METRICS: bool = Field(default=True, env="ENABLE_METRICS")
    METRICS_PORT: int = Field(default=9090, env="METRICS_PORT")
    
    # Redis Configuration (for caching and queues)
    REDIS_URL: str = Field(default="redis://localhost:6379", env="REDIS_URL")
    REDIS_DB: int = Field(default=0, env="REDIS_DB")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Webhook Configuration
    WEBHOOK_SECRET: str = Field(..., env="WEBHOOK_SECRET")
    WEBHOOK_TIMEOUT: int = Field(default=30, env="WEBHOOK_TIMEOUT")
    WEBHOOK_RETRY_ATTEMPTS: int = Field(default=3, env="WEBHOOK_RETRY_ATTEMPTS")
    
    # Email Configuration
    SMTP_HOST: str = Field(default="smtp.gmail.com", env="SMTP_HOST")
    SMTP_PORT: int = Field(default=587, env="SMTP_PORT")
    SMTP_USERNAME: str = Field(..., env="SMTP_USERNAME")
    SMTP_PASSWORD: str = Field(..., env="SMTP_PASSWORD")
    EMAIL_FROM: str = Field(..., env="EMAIL_FROM")
    
    # Notification Settings
    ENABLE_NOTIFICATIONS: bool = Field(default=True, env="ENABLE_NOTIFICATIONS")
    NOTIFICATION_CHANNELS: List[str] = Field(default=["email", "webhook"], env="NOTIFICATION_CHANNELS")
    
    # Security Settings
    CORS_ORIGINS: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    ALLOWED_HOSTS: List[str] = Field(default=["*"], env="ALLOWED_HOSTS")
    ENABLE_HTTPS_ONLY: bool = Field(default=False, env="ENABLE_HTTPS_ONLY")
    
    # Feature Flags
    ENABLE_VOICE_CLONING: bool = Field(default=True, env="ENABLE_VOICE_CLONING")
    ENABLE_BATCH_OPERATIONS: bool = Field(default=True, env="ENABLE_BATCH_OPERATIONS")
    ENABLE_ANALYTICS: bool = Field(default=True, env="ENABLE_ANALYTICS")
    ENABLE_AB_TESTING: bool = Field(default=True, env="ENABLE_AB_TESTING")
    ENABLE_VOICE_MARKETPLACE: bool = Field(default=True, env="ENABLE_VOICE_MARKETPLACE")
    
    # Performance Settings
    WORKER_PROCESSES: int = Field(default=1, env="WORKER_PROCESSES")
    WORKER_CONNECTIONS: int = Field(default=1000, env="WORKER_CONNECTIONS")
    KEEP_ALIVE: int = Field(default=2, env="KEEP_ALIVE")
    
    # Cost Management
    DEFAULT_COST_PER_CHAR: float = Field(default=0.00018, env="DEFAULT_COST_PER_CHAR")
    PREMIUM_COST_MULTIPLIER: float = Field(default=1.5, env="PREMIUM_COST_MULTIPLIER")
    CLONED_VOICE_COST_MULTIPLIER: float = Field(default=2.0, env="CLONED_VOICE_COST_MULTIPLIER")
    COST_ALERT_THRESHOLD: float = Field(default=100.0, env="COST_ALERT_THRESHOLD")
    
    # Audio Processing
    DEFAULT_SAMPLE_RATE: int = Field(default=22050, env="DEFAULT_SAMPLE_RATE")
    DEFAULT_BITRATE: int = Field(default=128, env="DEFAULT_BITRATE")
    AUDIO_COMPRESSION_QUALITY: int = Field(default=5, env="AUDIO_COMPRESSION_QUALITY")  # 0-9
    
    # Backup and Recovery
    BACKUP_ENABLED: bool = Field(default=True, env="BACKUP_ENABLED")
    BACKUP_SCHEDULE: str = Field(default="0 2 * * *", env="BACKUP_SCHEDULE")  # Daily at 2 AM
    BACKUP_RETENTION_DAYS: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class VoiceLabConfig:
    """Voice Lab specific configuration constants"""
    
    # Supported voice providers
    VOICE_PROVIDERS = {
        "elevenlabs": {
            "name": "ElevenLabs",
            "api_base": "https://api.elevenlabs.io/v1",
            "features": ["tts", "cloning", "voice_design"],
            "max_chars": 5000,
            "supported_languages": ["en", "es", "fr", "de", "it", "pt", "pl", "hi", "ar"],
            "quality_levels": ["standard", "premium"]
        },
        "openai": {
            "name": "OpenAI",
            "api_base": "https://api.openai.com/v1",
            "features": ["tts"],
            "max_chars": 4096,
            "supported_languages": ["en"],
            "models": ["tts-1", "tts-1-hd"]
        },
        "azure": {
            "name": "Azure Cognitive Services",
            "api_base": "https://api.cognitive.microsoft.com",
            "features": ["tts", "neural_voices"],
            "max_chars": 10000,
            "supported_languages": ["en", "es", "fr", "de", "it", "pt", "zh", "ja", "ko"]
        }
    }
    
    # Default voice settings
    DEFAULT_VOICE_SETTINGS = {
        "stability": 0.7,
        "similarity_boost": 0.8,
        "style": 0.2,
        "use_speaker_boost": True
    }
    
    # Quality metrics thresholds
    QUALITY_THRESHOLDS = {
        "excellent": 95.0,
        "good": 85.0,
        "fair": 75.0,
        "poor": 60.0
    }
    
    # Voice categories and their characteristics
    VOICE_CATEGORIES = {
        "premade": {
            "name": "Pre-made Voices",
            "description": "Professional voices ready to use",
            "cost_multiplier": 1.0,
            "available_tiers": ["free", "starter", "pro", "enterprise"]
        },
        "cloned": {
            "name": "Cloned Voices",
            "description": "Custom voices cloned from audio samples",
            "cost_multiplier": 2.0,
            "available_tiers": ["enterprise"]
        },
        "custom": {
            "name": "Custom Voices",
            "description": "Voices created with specific parameters",
            "cost_multiplier": 1.5,
            "available_tiers": ["pro", "enterprise"]
        }
    }
    
    # Use case configurations
    USE_CASES = {
        "business": {
            "name": "Business Calls",
            "recommended_settings": {
                "stability": 0.8,
                "similarity_boost": 0.7,
                "style": 0.1
            },
            "voice_characteristics": ["professional", "clear", "authoritative"]
        },
        "sales": {
            "name": "Sales Calls",
            "recommended_settings": {
                "stability": 0.6,
                "similarity_boost": 0.8,
                "style": 0.4
            },
            "voice_characteristics": ["friendly", "engaging", "persuasive"]
        },
        "executive": {
            "name": "Executive Communications",
            "recommended_settings": {
                "stability": 0.9,
                "similarity_boost": 0.6,
                "style": 0.2
            },
            "voice_characteristics": ["authoritative", "confident", "professional"]
        },
        "multilingual": {
            "name": "Multilingual Campaigns",
            "recommended_settings": {
                "stability": 0.7,
                "similarity_boost": 0.9,
                "style": 0.3
            },
            "voice_characteristics": ["natural", "accent-appropriate", "clear"]
        }
    }
    
    # Audio format specifications
    AUDIO_FORMATS = {
        "mp3": {
            "mime_type": "audio/mpeg",
            "extension": ".mp3",
            "compression": "lossy",
            "quality": "good",
            "file_size": "small"
        },
        "wav": {
            "mime_type": "audio/wav",
            "extension": ".wav",
            "compression": "none",
            "quality": "excellent",
            "file_size": "large"
        },
        "ogg": {
            "mime_type": "audio/ogg",
            "extension": ".ogg",
            "compression": "lossy",
            "quality": "good",
            "file_size": "small"
        },
        "m4a": {
            "mime_type": "audio/mp4",
            "extension": ".m4a",
            "compression": "lossy",
            "quality": "good",
            "file_size": "small"
        }
    }
    
    # Testing configurations
    TEST_PHRASES = {
        "standard": [
            "Hello, this is a test of voice quality and clarity.",
            "The quick brown fox jumps over the lazy dog.",
            "Please confirm your appointment for tomorrow at 3 PM.",
            "We appreciate your business and look forward to serving you.",
            "Your satisfaction is our top priority."
        ],
        "business": [
            "Good morning, I'm calling to discuss your recent inquiry.",
            "We have exciting opportunities that might interest you.",
            "Let me transfer you to our specialist for further assistance.",
            "Thank you for choosing our services.",
            "Is this a convenient time to talk?"
        ],
        "sales": [
            "Hi there! I hope you're having a great day.",
            "I'm excited to share this limited-time opportunity with you.",
            "What would be the best time to schedule a quick call?",
            "This could save you hundreds of dollars annually.",
            "Would you like to hear more about how this works?"
        ],
        "technical": [
            "Supercalifragilisticexpialidocious",
            "The sixth sick sheik's sixth sheep's sick.",
            "Red leather, yellow leather.",
            "How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
            "She sells seashells by the seashore."
        ]
    }
    
    # Error codes and messages
    ERROR_CODES = {
        "VOICE_NOT_FOUND": {
            "code": "VL001",
            "message": "Voice not found or not accessible",
            "http_status": 404
        },
        "GENERATION_FAILED": {
            "code": "VL002", 
            "message": "Voice generation failed",
            "http_status": 500
        },
        "CLONING_FAILED": {
            "code": "VL003",
            "message": "Voice cloning failed",
            "http_status": 500
        },
        "INVALID_AUDIO": {
            "code": "VL004",
            "message": "Invalid audio file format or quality",
            "http_status": 400
        },
        "QUOTA_EXCEEDED": {
            "code": "VL005",
            "message": "Usage quota exceeded",
            "http_status": 429
        },
        "TEXT_TOO_LONG": {
            "code": "VL006",
            "message": "Text exceeds maximum length",
            "http_status": 400
        },
        "UNAUTHORIZED": {
            "code": "VL007",
            "message": "Unauthorized access to voice resource",
            "http_status": 403
        }
    }


# Initialize settings instance
settings = Settings()

# Export commonly used configurations
VOICE_PROVIDERS = VoiceLabConfig.VOICE_PROVIDERS
DEFAULT_VOICE_SETTINGS = VoiceLabConfig.DEFAULT_VOICE_SETTINGS
QUALITY_THRESHOLDS = VoiceLabConfig.QUALITY_THRESHOLDS
USE_CASES = VoiceLabConfig.USE_CASES
AUDIO_FORMATS = VoiceLabConfig.AUDIO_FORMATS
TEST_PHRASES = VoiceLabConfig.TEST_PHRASES
ERROR_CODES = VoiceLabConfig.ERROR_CODES