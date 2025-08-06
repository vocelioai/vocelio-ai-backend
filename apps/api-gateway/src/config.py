# apps/api-gateway/src/config.py
from pydantic import BaseSettings, validator
from typing import List, Optional
import os

class Settings(BaseSettings):
    """API Gateway Configuration"""
    
    # App Settings
    APP_NAME: str = "Vocelio.ai API Gateway"
    VERSION: str = "2.0.0"
    DEBUG: bool = False
    
    # Environment
    ENVIRONMENT: str = "development"
    RAILWAY_ENVIRONMENT: Optional[str] = None
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # Database (if gateway needs direct DB access)
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Redis (for caching and rate limiting)
    REDIS_URL: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 1000  # requests per minute
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Service Timeouts
    SERVICE_TIMEOUT: int = 30  # seconds
    WEBHOOK_TIMEOUT: int = 15  # seconds
    HEALTH_CHECK_TIMEOUT: int = 5  # seconds
    
    # Health Check Settings
    HEALTH_CHECK_INTERVAL: int = 30  # seconds
    UNHEALTHY_THRESHOLD: int = 3  # failed checks before marking unhealthy
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_JSON: bool = False
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Service Discovery
    SERVICE_DISCOVERY_ENABLED: bool = True
    SERVICE_REGISTRY_TTL: int = 300  # seconds
    
    # Circuit Breaker
    CIRCUIT_BREAKER_ENABLED: bool = True
    CIRCUIT_BREAKER_FAILURE_THRESHOLD: int = 5
    CIRCUIT_BREAKER_TIMEOUT: int = 60  # seconds
    
    # Load Balancing
    LOAD_BALANCER_STRATEGY: str = "round_robin"  # round_robin, least_connections, weighted
    
    # Webhook Settings
    WEBHOOK_RETRY_ATTEMPTS: int = 3
    WEBHOOK_RETRY_DELAY: float = 0.5  # seconds
    
    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")
        return v
    
    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Create settings instance
settings = Settings()

# Service-specific configurations
SERVICE_CONFIG = {
    "overview": {
        "name": "Command Center",
        "timeout": 30,
        "retry_attempts": 2,
        "health_check_path": "/health"
    },
    "agents": {
        "name": "AI Agents",
        "timeout": 45,  # AI operations may take longer
        "retry_attempts": 2,
        "health_check_path": "/health"
    },
    "smart-campaigns": {
        "name": "Smart Campaigns", 
        "timeout": 30,
        "retry_attempts": 3,
        "health_check_path": "/health"
    },
    "call-center": {
        "name": "Call Center",
        "timeout": 60,  # Calls may take longer
        "retry_attempts": 1,  # Don't retry calls
        "health_check_path": "/health"
    },
    "phone-numbers": {
        "name": "Phone Numbers",
        "timeout": 20,
        "retry_attempts": 2,
        "health_check_path": "/health"
    },
    "voice-marketplace": {
        "name": "Voice Marketplace",
        "timeout": 30,
        "retry_attempts": 2,
        "health_check_path": "/health"
    },
    "voice-lab": {
        "name": "Voice Lab",
        "timeout": 120,  # Voice generation can be slow
        "retry_attempts": 1,  # Don't retry expensive operations
        "health_check_path": "/health"
    },
    "flow-builder": {
        "name": "Flow Builder",
        "timeout": 30,
        "retry_attempts": 2,
        "health_check_path": "/health"
    },
    "analytics-pro": {
        "name": "Analytics Pro",
        "timeout": 60,  # Analytics queries may be slow
        "retry_attempts": 2,
        "health_check_path": "/health"
    },
    "ai-brain": {
        "name": "AI Brain",
        "timeout": 60,  # AI processing can be slow
        "retry_attempts": 1,  # Don't retry AI operations
        "health_check_path": "/health"
    },
    "integrations": {
        "name": "Integrations",
        "timeout": 30,
        "retry_attempts": 3,
        "health_check_path": "/health"
    },
    "agent-store": {
        "name": "Agent Store",
        "timeout": 30,
        "retry_attempts": 2,
        "health_check_path": "/health"
    },
    "billing-pro": {
        "name": "Billing Pro",
        "timeout": 30,
        "retry_attempts": 3,  # Billing is critical
        "health_check_path": "/health"
    },
    "team-hub": {
        "name": "Team Hub",
        "timeout": 20,
        "retry_attempts": 2,
        "health_check_path": "/health"
    },
    "compliance": {
        "name": "Compliance",
        "timeout": 30,
        "retry_attempts": 3,  # Compliance is critical
        "health_check_path": "/health"
    },
    "white-label": {
        "name": "White Label",
        "timeout": 30,
        "retry_attempts": 2,
        "health_check_path": "/health"
    },
    "developer-api": {
        "name": "Developer API",
        "timeout": 20,
        "retry_attempts": 2,
        "health_check_path": "/health"
    },
    "settings": {
        "name": "Settings",
        "timeout": 20,
        "retry_attempts": 2,
        "health_check_path": "/health"
    }
}

# Environment-specific overrides
if settings.ENVIRONMENT == "production":
    settings.DEBUG = False
    settings.LOG_LEVEL = "WARNING"
    settings.RATE_LIMIT_REQUESTS = 5000  # Higher limits in production
elif settings.ENVIRONMENT == "staging":
    settings.DEBUG = False
    settings.LOG_LEVEL = "INFO"
    settings.RATE_LIMIT_REQUESTS = 2000
elif settings.ENVIRONMENT == "development":
    settings.DEBUG = True
    settings.LOG_LEVEL = "DEBUG"
    settings.RATE_LIMIT_REQUESTS = 100  # Lower limits for development

# Railway-specific configuration
if settings.RAILWAY_ENVIRONMENT:
    settings.ENVIRONMENT = settings.RAILWAY_ENVIRONMENT
    settings.DEBUG = False
    
    # Railway uses dynamic ports
    PORT = int(os.getenv("PORT", 8000))
    
    # Railway provides URLs in specific format
    RAILWAY_STATIC_URL = os.getenv("RAILWAY_STATIC_URL")
    if RAILWAY_STATIC_URL:
        settings.ALLOWED_ORIGINS.append(f"https://{RAILWAY_STATIC_URL}")
        settings.ALLOWED_ORIGINS.append(f"http://{RAILWAY_STATIC_URL}")

# Export settings
__all__ = ["settings", "SERVICE_CONFIG"]