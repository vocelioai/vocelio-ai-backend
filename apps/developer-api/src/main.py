"""
Developer API Service - Vocelio AI Call Center
API management, developer tools, documentation, and third-party integrations
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
import hashlib
import secrets
import time
from collections import defaultdict
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

# Developer API Models
class APIKeyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"

class APIKeyScope(str, Enum):
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"
    WEBHOOK = "webhook"
    FULL_ACCESS = "full_access"

class RateLimitPeriod(str, Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"

class DeveloperTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"

class APIKey(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    key: str = Field(default_factory=lambda: f"voc_{secrets.token_urlsafe(32)}")
    secret: str = Field(default_factory=lambda: secrets.token_urlsafe(48))
    
    # Ownership
    developer_id: str
    developer_email: str
    organization: Optional[str] = None
    
    # Configuration
    status: APIKeyStatus = APIKeyStatus.ACTIVE
    scopes: List[APIKeyScope] = [APIKeyScope.READ]
    tier: DeveloperTier = DeveloperTier.FREE
    
    # Rate limiting
    rate_limit_requests: int = 1000  # requests per period
    rate_limit_period: RateLimitPeriod = RateLimitPeriod.HOUR
    
    # Permissions
    allowed_endpoints: List[str] = []  # Empty = all allowed
    blocked_endpoints: List[str] = []
    allowed_ips: List[str] = []  # Empty = all IPs allowed
    
    # Tracking
    created_at: datetime = Field(default_factory=datetime.now)
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    usage_count: int = 0
    quota_used: int = 0
    quota_limit: Optional[int] = None
    
    # Metadata
    webhook_url: Optional[str] = None
    metadata: Dict[str, Any] = {}
    tags: List[str] = []

class APIUsage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    api_key_id: str
    developer_id: str
    
    # Request details
    method: str
    endpoint: str
    user_agent: Optional[str] = None
    ip_address: str
    
    # Response details
    status_code: int
    response_time_ms: float
    response_size_bytes: int
    
    # Timing
    timestamp: datetime = Field(default_factory=datetime.now)
    
    # Additional data
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = {}

class RateLimit(BaseModel):
    api_key_id: str
    period: RateLimitPeriod
    requests_made: int = 0
    requests_limit: int
    window_start: datetime = Field(default_factory=datetime.now)
    blocked: bool = False

class WebhookEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4))
    api_key_id: str
    event_type: str
    payload: Dict[str, Any]
    
    # Delivery tracking
    webhook_url: str
    status: str = "pending"  # "pending", "delivered", "failed"
    attempts: int = 0
    max_attempts: int = 3
    next_attempt: Optional[datetime] = None
    
    # Timing
    created_at: datetime = Field(default_factory=datetime.now)
    delivered_at: Optional[datetime] = None
    
    # Response details
    response_status: Optional[int] = None
    response_body: Optional[str] = None
    error_message: Optional[str] = None

class APIEndpoint(BaseModel):
    path: str
    method: str
    description: str
    category: str
    requires_auth: bool = True
    required_scopes: List[APIKeyScope] = []
    rate_limit_override: Optional[int] = None
    deprecated: bool = False
    version: str = "1.0"

# Sample data
SAMPLE_API_KEYS = [
    APIKey(
        name="Production API Key",
        description="Main API key for production environment",
        developer_id="dev_001",
        developer_email="developer@techcorp.com",
        organization="TechCorp Solutions",
        scopes=[APIKeyScope.READ, APIKeyScope.WRITE],
        tier=DeveloperTier.PRO,
        rate_limit_requests=10000,
        usage_count=8420,
        quota_used=8420,
        quota_limit=100000,
        last_used_at=datetime.now() - timedelta(minutes=5),
        tags=["production", "high-volume"]
    ),
    APIKey(
        name="Development Testing",
        description="API key for development and testing purposes",
        developer_id="dev_002", 
        developer_email="dev@startup.com",
        organization="Startup Inc",
        scopes=[APIKeyScope.READ],
        tier=DeveloperTier.BASIC,
        rate_limit_requests=5000,
        usage_count=1247,
        quota_used=1247,
        quota_limit=10000,
        last_used_at=datetime.now() - timedelta(hours=2),
        tags=["development", "testing"]
    ),
    APIKey(
        name="Webhook Integration",
        description="API key for webhook event delivery",
        developer_id="dev_003",
        developer_email="webhooks@enterprise.com", 
        organization="Enterprise Corp",
        scopes=[APIKeyScope.WEBHOOK, APIKeyScope.WRITE],
        tier=DeveloperTier.ENTERPRISE,
        rate_limit_requests=50000,
        webhook_url="https://api.enterprise.com/webhooks/vocelio",
        usage_count=15690,
        quota_used=15690,
        last_used_at=datetime.now() - timedelta(minutes=1),
        tags=["webhook", "enterprise", "real-time"]
    )
]

SAMPLE_ENDPOINTS = [
    APIEndpoint(path="/api/v1/calls", method="GET", description="List calls", category="Calls", required_scopes=[APIKeyScope.READ]),
    APIEndpoint(path="/api/v1/calls", method="POST", description="Create call", category="Calls", required_scopes=[APIKeyScope.WRITE]),
    APIEndpoint(path="/api/v1/contacts", method="GET", description="List contacts", category="Contacts", required_scopes=[APIKeyScope.READ]),
    APIEndpoint(path="/api/v1/contacts", method="POST", description="Create contact", category="Contacts", required_scopes=[APIKeyScope.WRITE]),
    APIEndpoint(path="/api/v1/agents", method="GET", description="List agents", category="Agents", required_scopes=[APIKeyScope.READ]),
    APIEndpoint(path="/api/v1/analytics", method="GET", description="Get analytics", category="Analytics", required_scopes=[APIKeyScope.READ]),
    APIEndpoint(path="/api/v1/webhooks", method="POST", description="Create webhook", category="Webhooks", required_scopes=[APIKeyScope.WEBHOOK]),
]

# Global storage
api_keys: List[APIKey] = []
api_usage: List[APIUsage] = []
rate_limits: Dict[str, RateLimit] = {}
webhook_events: List[WebhookEvent] = []
endpoints: List[APIEndpoint] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global api_keys, endpoints
    
    api_keys.extend(SAMPLE_API_KEYS)
    endpoints.extend(SAMPLE_ENDPOINTS)
    
    logger.info("Sample developer API data initialized successfully")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    yield
    
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="Developer API Service", 
    description="API management, developer tools, documentation, and third-party integrations for Vocelio AI Call Center",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Rate limiting helper
async def check_rate_limit(api_key: APIKey, endpoint: str) -> bool:
    """Check if request is within rate limits"""
    now = datetime.now()
    key = f"{api_key.id}_{api_key.rate_limit_period.value}"
    
    if key not in rate_limits:
        rate_limits[key] = RateLimit(
            api_key_id=api_key.id,
            period=api_key.rate_limit_period,
            requests_limit=api_key.rate_limit_requests,
            window_start=now
        )
    
    rate_limit = rate_limits[key]
    
    # Check if we need to reset the window
    if api_key.rate_limit_period == RateLimitPeriod.MINUTE:
        window_duration = timedelta(minutes=1)
    elif api_key.rate_limit_period == RateLimitPeriod.HOUR:
        window_duration = timedelta(hours=1)
    elif api_key.rate_limit_period == RateLimitPeriod.DAY:
        window_duration = timedelta(days=1)
    else:  # MONTH
        window_duration = timedelta(days=30)
    
    if now - rate_limit.window_start >= window_duration:
        rate_limit.requests_made = 0
        rate_limit.window_start = now
        rate_limit.blocked = False
    
    # Check limit
    if rate_limit.requests_made >= rate_limit.requests_limit:
        rate_limit.blocked = True
        return False
    
    rate_limit.requests_made += 1
    return True

# Authentication helper
async def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)) -> APIKey:
    """Verify API key from Authorization header"""
    api_key = next((k for k in api_keys if k.key == credentials.credentials), None)
    
    if not api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    if api_key.status != APIKeyStatus.ACTIVE:
        raise HTTPException(status_code=401, detail="API key is not active")
    
    if api_key.expires_at and api_key.expires_at < datetime.now():
        raise HTTPException(status_code=401, detail="API key has expired")
    
    return api_key

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "developer-api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# API Key Management Endpoints
@app.get("/api-keys", response_model=List[APIKey])
async def get_api_keys(
    status: Optional[APIKeyStatus] = None,
    tier: Optional[DeveloperTier] = None,
    developer_id: Optional[str] = None
):
    """Get all API keys with optional filtering"""
    filtered_keys = api_keys
    
    if status:
        filtered_keys = [k for k in filtered_keys if k.status == status]
    
    if tier:
        filtered_keys = [k for k in filtered_keys if k.tier == tier]
        
    if developer_id:
        filtered_keys = [k for k in filtered_keys if k.developer_id == developer_id]
    
    return filtered_keys

@app.get("/api-keys/{api_key_id}", response_model=APIKey)
async def get_api_key(api_key_id: str):
    """Get specific API key details"""
    api_key = next((k for k in api_keys if k.id == api_key_id), None)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    return api_key

@app.post("/api-keys", response_model=APIKey)
async def create_api_key(api_key_data: APIKey):
    """Create a new API key"""
    api_keys.append(api_key_data)
    logger.info(f"Created new API key: {api_key_data.name} for {api_key_data.developer_email}")
    return api_key_data

@app.put("/api-keys/{api_key_id}", response_model=APIKey)
async def update_api_key(api_key_id: str, updates: Dict[str, Any]):
    """Update an existing API key"""
    api_key = next((k for k in api_keys if k.id == api_key_id), None)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    for field, value in updates.items():
        if hasattr(api_key, field):
            setattr(api_key, field, value)
    
    logger.info(f"Updated API key: {api_key.name}")
    return api_key

@app.delete("/api-keys/{api_key_id}")
async def revoke_api_key(api_key_id: str):
    """Revoke an API key"""
    api_key = next((k for k in api_keys if k.id == api_key_id), None)
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")
    
    api_key.status = APIKeyStatus.REVOKED
    logger.info(f"Revoked API key: {api_key.name}")
    return {"message": "API key revoked successfully"}

# API Usage and Analytics
@app.get("/usage/stats")
async def get_usage_stats(
    api_key_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get API usage statistics"""
    filtered_usage = api_usage
    
    if api_key_id:
        filtered_usage = [u for u in filtered_usage if u.api_key_id == api_key_id]
    
    if start_date:
        filtered_usage = [u for u in filtered_usage if u.timestamp >= start_date]
        
    if end_date:
        filtered_usage = [u for u in filtered_usage if u.timestamp <= end_date]
    
    # Calculate statistics
    total_requests = len(filtered_usage)
    successful_requests = len([u for u in filtered_usage if 200 <= u.status_code < 300])
    failed_requests = total_requests - successful_requests
    
    avg_response_time = 0
    if filtered_usage:
        avg_response_time = sum(u.response_time_ms for u in filtered_usage) / len(filtered_usage)
    
    # Endpoint usage
    endpoint_stats = defaultdict(int)
    for usage in filtered_usage:
        endpoint_stats[f"{usage.method} {usage.endpoint}"] += 1
    
    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
        "average_response_time_ms": round(avg_response_time, 2),
        "endpoint_usage": dict(endpoint_stats),
        "period": {
            "start": start_date.isoformat() if start_date else None,
            "end": end_date.isoformat() if end_date else None
        }
    }

@app.get("/endpoints", response_model=List[APIEndpoint])
async def get_api_endpoints(category: Optional[str] = None):
    """Get available API endpoints documentation"""
    filtered_endpoints = endpoints
    
    if category:
        filtered_endpoints = [e for e in filtered_endpoints if e.category.lower() == category.lower()]
    
    return filtered_endpoints

@app.get("/documentation")
async def get_api_documentation():
    """Get comprehensive API documentation"""
    categories = {}
    for endpoint in endpoints:
        if endpoint.category not in categories:
            categories[endpoint.category] = []
        categories[endpoint.category].append({
            "path": endpoint.path,
            "method": endpoint.method,
            "description": endpoint.description,
            "requires_auth": endpoint.requires_auth,
            "required_scopes": endpoint.required_scopes,
            "deprecated": endpoint.deprecated
        })
    
    return {
        "title": "Vocelio AI Call Center API",
        "version": "1.0.0",
        "description": "Comprehensive API for managing AI-powered call center operations",
        "base_url": "https://api.vocelio.com",
        "authentication": {
            "type": "Bearer Token",
            "header": "Authorization: Bearer voc_your_api_key_here"
        },
        "rate_limits": {
            "free": "1,000 requests/hour",
            "basic": "5,000 requests/hour", 
            "pro": "10,000 requests/hour",
            "enterprise": "50,000 requests/hour"
        },
        "categories": categories,
        "total_endpoints": len(endpoints)
    }

@app.get("/rate-limits")
async def get_rate_limit_status(api_key: APIKey = Depends(verify_api_key)):
    """Get current rate limit status for the authenticated API key"""
    key = f"{api_key.id}_{api_key.rate_limit_period.value}"
    rate_limit = rate_limits.get(key)
    
    if not rate_limit:
        return {
            "requests_made": 0,
            "requests_limit": api_key.rate_limit_requests,
            "requests_remaining": api_key.rate_limit_requests,
            "period": api_key.rate_limit_period.value,
            "window_start": datetime.now().isoformat(),
            "blocked": False
        }
    
    return {
        "requests_made": rate_limit.requests_made,
        "requests_limit": rate_limit.requests_limit,
        "requests_remaining": max(0, rate_limit.requests_limit - rate_limit.requests_made),
        "period": rate_limit.period.value,
        "window_start": rate_limit.window_start.isoformat(),
        "blocked": rate_limit.blocked
    }

# Developer Dashboard
@app.get("/dashboard")
async def get_developer_dashboard():
    """Get developer dashboard overview"""
    total_keys = len(api_keys)
    active_keys = len([k for k in api_keys if k.status == APIKeyStatus.ACTIVE])
    
    # Tier distribution
    tier_stats = {}
    for tier in DeveloperTier:
        tier_stats[tier.value] = len([k for k in api_keys if k.tier == tier])
    
    # Recent usage
    recent_usage = [u for u in api_usage if u.timestamp > datetime.now() - timedelta(hours=24)]
    
    return {
        "overview": {
            "total_api_keys": total_keys,
            "active_api_keys": active_keys,
            "total_endpoints": len(endpoints),
            "requests_24h": len(recent_usage)
        },
        "tier_distribution": tier_stats,
        "top_endpoints": [
            {"endpoint": "/api/v1/calls", "requests": 3420},
            {"endpoint": "/api/v1/contacts", "requests": 1890},
            {"endpoint": "/api/v1/analytics", "requests": 1205},
            {"endpoint": "/api/v1/agents", "requests": 876},
            {"endpoint": "/api/v1/webhooks", "requests": 543}
        ],
        "health_status": "operational",
        "uptime_percentage": 99.9
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8008)
