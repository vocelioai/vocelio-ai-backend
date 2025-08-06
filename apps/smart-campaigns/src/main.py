"""
Smart Campaigns Service - Vocelio Backend
Handles campaign management, A/B testing, and campaign optimization
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import logging
import json
import uuid
import os
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CampaignType(str, Enum):
    OUTBOUND = "outbound"
    INBOUND = "inbound"
    FOLLOW_UP = "follow_up"
    NURTURE = "nurture"
    SURVEY = "survey"

class ABTestStatus(str, Enum):
    DRAFT = "draft"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"

# Pydantic Models
class CampaignSettings(BaseModel):
    max_concurrent_calls: int = 10
    call_retry_attempts: int = 3
    call_timeout: int = 60
    working_hours_start: str = "09:00"
    working_hours_end: str = "17:00"
    time_zone: str = "UTC"
    call_interval_minutes: int = 5
    voicemail_detection: bool = True
    call_recording: bool = True
    compliance_checks: bool = True

class CampaignScript(BaseModel):
    intro: str
    main_pitch: str
    objection_handling: List[Dict[str, str]] = []
    closing: str
    voicemail_script: Optional[str] = None

class ABTestVariant(BaseModel):
    id: str = None
    name: str
    script: CampaignScript
    voice_id: str
    traffic_percentage: float
    is_control: bool = False
    
    def __init__(self, **data):
        if data.get('id') is None:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)

class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    type: CampaignType
    agent_id: str
    phone_number_id: str
    target_audience: Dict[str, Any] = {}
    script: CampaignScript
    settings: CampaignSettings = CampaignSettings()
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    tags: List[str] = []

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    script: Optional[CampaignScript] = None
    settings: Optional[CampaignSettings] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    tags: Optional[List[str]] = None

class ABTestCreate(BaseModel):
    campaign_id: str
    name: str
    description: Optional[str] = None
    variants: List[ABTestVariant]
    test_duration_days: int = 7
    confidence_level: float = 0.95
    primary_metric: str = "conversion_rate"
    
    @validator('variants')
    def validate_variants(cls, v):
        if len(v) < 2:
            raise ValueError('At least 2 variants required for A/B test')
        
        total_traffic = sum(variant.traffic_percentage for variant in v)
        if abs(total_traffic - 100.0) > 0.01:
            raise ValueError('Total traffic percentage must equal 100%')
        
        control_count = sum(1 for variant in v if variant.is_control)
        if control_count != 1:
            raise ValueError('Exactly one variant must be marked as control')
        
        return v

class CampaignResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    type: CampaignType
    status: CampaignStatus
    agent_id: str
    phone_number_id: str
    target_audience: Dict[str, Any]
    script: CampaignScript
    settings: CampaignSettings
    created_at: datetime
    updated_at: datetime
    scheduled_start: Optional[datetime]
    scheduled_end: Optional[datetime]
    tags: List[str]
    statistics: Dict[str, Any] = {}

class ABTestResponse(BaseModel):
    id: str
    campaign_id: str
    name: str
    description: Optional[str]
    status: ABTestStatus
    variants: List[ABTestVariant]
    test_duration_days: int
    confidence_level: float
    primary_metric: str
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    results: Dict[str, Any] = {}

class CampaignMetrics(BaseModel):
    campaign_id: str
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    conversion_rate: float = 0.0
    average_call_duration: float = 0.0
    cost_per_call: float = 0.0
    revenue_generated: float = 0.0
    roi: float = 0.0
    last_updated: datetime

# Global state (In production, use proper database)
campaigns_db = {}
ab_tests_db = {}
campaign_metrics_db = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Smart Campaigns Service starting up...")
    
    # Initialize sample data
    await initialize_sample_campaigns()
    
    yield
    
    logger.info("💤 Smart Campaigns Service shutting down...")

app = FastAPI(
    title="Smart Campaigns Service",
    description="AI-powered campaign management with A/B testing and optimization",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Authentication dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token"""
    # In production, implement proper JWT validation
    if credentials.credentials == "demo-token":
        return {"id": "user123", "email": "demo@vocelio.com"}
    return {"id": "user123", "email": "demo@vocelio.com"}  # Demo mode

async def initialize_sample_campaigns():
    """Initialize sample campaigns for demonstration"""
    
    # Sample script
    sample_script = CampaignScript(
        intro="Hi, this is Sarah from Vocelio AI. I hope you're having a great day!",
        main_pitch="I'm calling because we've developed an AI voice assistant that's helping businesses like yours increase sales by 40% while reducing customer service costs.",
        objection_handling=[
            {
                "objection": "not_interested",
                "response": "I understand, but what if I told you this could save you 20 hours per week?"
            },
            {
                "objection": "too_expensive", 
                "response": "Actually, most clients save money in the first month. Can I show you how?"
            }
        ],
        closing="Would you like to schedule a quick 15-minute demo to see how this could work for your business?",
        voicemail_script="Hi, this is Sarah from Vocelio AI. I have something that could transform your business communication. Please call me back at your convenience."
    )
    
    # Sample campaign
    campaign_id = str(uuid.uuid4())
    campaigns_db[campaign_id] = {
        "id": campaign_id,
        "name": "Q4 Sales Outreach",
        "description": "End-of-year sales campaign targeting enterprise clients",
        "type": CampaignType.OUTBOUND,
        "status": CampaignStatus.ACTIVE,
        "agent_id": "agent_001",
        "phone_number_id": "phone_001", 
        "target_audience": {
            "industry": ["technology", "finance"],
            "company_size": "51-200 employees",
            "location": "United States",
            "criteria": "Have shown interest in AI solutions"
        },
        "script": sample_script.dict(),
        "settings": CampaignSettings().dict(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "scheduled_start": datetime.utcnow() - timedelta(days=2),
        "scheduled_end": datetime.utcnow() + timedelta(days=28),
        "tags": ["sales", "ai", "enterprise", "q4"]
    }
    
    # Sample metrics
    campaign_metrics_db[campaign_id] = {
        "campaign_id": campaign_id,
        "total_calls": 247,
        "successful_calls": 189,
        "failed_calls": 58,
        "conversion_rate": 12.5,
        "average_call_duration": 187.3,
        "cost_per_call": 2.45,
        "revenue_generated": 15750.00,
        "roi": 285.7,
        "last_updated": datetime.utcnow()
    }
    
    # Sample A/B test
    ab_test_id = str(uuid.uuid4())
    ab_tests_db[ab_test_id] = {
        "id": ab_test_id,
        "campaign_id": campaign_id,
        "name": "Voice Tone Test",
        "description": "Testing professional vs friendly voice tone",
        "status": ABTestStatus.RUNNING,
        "variants": [
            {
                "id": str(uuid.uuid4()),
                "name": "Professional Voice",
                "script": sample_script.dict(),
                "voice_id": "voice_professional_001",
                "traffic_percentage": 50.0,
                "is_control": True
            },
            {
                "id": str(uuid.uuid4()),
                "name": "Friendly Voice", 
                "script": sample_script.dict(),
                "voice_id": "voice_friendly_001",
                "traffic_percentage": 50.0,
                "is_control": False
            }
        ],
        "test_duration_days": 14,
        "confidence_level": 0.95,
        "primary_metric": "conversion_rate",
        "created_at": datetime.utcnow() - timedelta(days=5),
        "started_at": datetime.utcnow() - timedelta(days=5),
        "ended_at": None,
        "results": {
            "professional_voice": {
                "calls": 124,
                "conversions": 18,
                "conversion_rate": 14.5,
                "revenue": 8200.00
            },
            "friendly_voice": {
                "calls": 123,
                "conversions": 13,
                "conversion_rate": 10.6,
                "revenue": 5550.00
            },
            "statistical_significance": 0.87,
            "winner": "professional_voice",
            "confidence": 87.3
        }
    }

# Routes

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "smart-campaigns",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/campaigns", response_model=List[CampaignResponse])
async def get_campaigns(
    status: Optional[CampaignStatus] = None,
    type: Optional[CampaignType] = None,
    limit: int = Query(default=20, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get campaigns with optional filtering"""
    
    campaigns = list(campaigns_db.values())
    
    # Apply filters
    if status:
        campaigns = [c for c in campaigns if c["status"] == status]
    if type:
        campaigns = [c for c in campaigns if c["type"] == type]
    
    # Apply pagination
    total = len(campaigns)
    campaigns = campaigns[offset:offset + limit]
    
    # Add statistics
    for campaign in campaigns:
        campaign_id = campaign["id"]
        if campaign_id in campaign_metrics_db:
            campaign["statistics"] = campaign_metrics_db[campaign_id]
    
    return campaigns

@app.get("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get campaign by ID"""
    
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id].copy()
    
    # Add statistics
    if campaign_id in campaign_metrics_db:
        campaign["statistics"] = campaign_metrics_db[campaign_id]
    
    return campaign

@app.post("/campaigns", response_model=CampaignResponse)
async def create_campaign(
    campaign: CampaignCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create a new campaign"""
    
    campaign_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    campaign_data = {
        "id": campaign_id,
        **campaign.dict(),
        "status": CampaignStatus.DRAFT,
        "created_at": now,
        "updated_at": now
    }
    
    campaigns_db[campaign_id] = campaign_data
    
    # Initialize metrics
    campaign_metrics_db[campaign_id] = CampaignMetrics(
        campaign_id=campaign_id,
        last_updated=now
    ).dict()
    
    # Schedule campaign validation in background
    background_tasks.add_task(validate_campaign, campaign_id)
    
    return campaign_data

@app.put("/campaigns/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: str,
    updates: CampaignUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update campaign"""
    
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    # Apply updates
    update_data = updates.dict(exclude_unset=True)
    campaign.update(update_data)
    campaign["updated_at"] = datetime.utcnow()
    
    return campaign

@app.delete("/campaigns/{campaign_id}")
async def delete_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete campaign"""
    
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Check if campaign is active
    if campaigns_db[campaign_id]["status"] == CampaignStatus.ACTIVE:
        raise HTTPException(
            status_code=400, 
            detail="Cannot delete active campaign. Pause or complete first."
        )
    
    del campaigns_db[campaign_id]
    if campaign_id in campaign_metrics_db:
        del campaign_metrics_db[campaign_id]
    
    return {"message": "Campaign deleted successfully"}

@app.post("/campaigns/{campaign_id}/start")
async def start_campaign(
    campaign_id: str,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Start a campaign"""
    
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    if campaign["status"] not in [CampaignStatus.DRAFT, CampaignStatus.PAUSED]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot start campaign with status: {campaign['status']}"
        )
    
    # Validate campaign before starting
    validation_result = await validate_campaign(campaign_id)
    if not validation_result["valid"]:
        raise HTTPException(
            status_code=400,
            detail=f"Campaign validation failed: {validation_result['errors']}"
        )
    
    campaign["status"] = CampaignStatus.ACTIVE
    campaign["updated_at"] = datetime.utcnow()
    
    # Start campaign execution in background
    background_tasks.add_task(execute_campaign, campaign_id)
    
    return {"message": "Campaign started successfully", "campaign_id": campaign_id}

@app.post("/campaigns/{campaign_id}/pause")
async def pause_campaign(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Pause a campaign"""
    
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign = campaigns_db[campaign_id]
    
    if campaign["status"] != CampaignStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"Can only pause active campaigns"
        )
    
    campaign["status"] = CampaignStatus.PAUSED
    campaign["updated_at"] = datetime.utcnow()
    
    return {"message": "Campaign paused successfully"}

@app.get("/campaigns/{campaign_id}/metrics", response_model=CampaignMetrics)
async def get_campaign_metrics(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get campaign metrics"""
    
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    if campaign_id not in campaign_metrics_db:
        raise HTTPException(status_code=404, detail="Metrics not found")
    
    return campaign_metrics_db[campaign_id]

@app.post("/campaigns/{campaign_id}/ab-test", response_model=ABTestResponse)
async def create_ab_test(
    campaign_id: str,
    ab_test: ABTestCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create A/B test for campaign"""
    
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Validate campaign is active
    campaign = campaigns_db[campaign_id]
    if campaign["status"] != CampaignStatus.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail="Can only create A/B tests for active campaigns"
        )
    
    ab_test_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    ab_test_data = {
        "id": ab_test_id,
        **ab_test.dict(),
        "status": ABTestStatus.DRAFT,
        "created_at": now,
        "started_at": None,
        "ended_at": None,
        "results": {}
    }
    
    ab_tests_db[ab_test_id] = ab_test_data
    
    # Start A/B test in background
    background_tasks.add_task(start_ab_test, ab_test_id)
    
    return ab_test_data

@app.get("/campaigns/{campaign_id}/ab-tests", response_model=List[ABTestResponse])
async def get_campaign_ab_tests(
    campaign_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get A/B tests for campaign"""
    
    if campaign_id not in campaigns_db:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    ab_tests = [
        test for test in ab_tests_db.values() 
        if test["campaign_id"] == campaign_id
    ]
    
    return ab_tests

@app.get("/ab-tests/{ab_test_id}", response_model=ABTestResponse)
async def get_ab_test(
    ab_test_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get A/B test by ID"""
    
    if ab_test_id not in ab_tests_db:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    return ab_tests_db[ab_test_id]

@app.post("/ab-tests/{ab_test_id}/stop")
async def stop_ab_test(
    ab_test_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Stop A/B test"""
    
    if ab_test_id not in ab_tests_db:
        raise HTTPException(status_code=404, detail="A/B test not found")
    
    ab_test = ab_tests_db[ab_test_id]
    
    if ab_test["status"] != ABTestStatus.RUNNING:
        raise HTTPException(
            status_code=400,
            detail="Can only stop running A/B tests"
        )
    
    ab_test["status"] = ABTestStatus.COMPLETED
    ab_test["ended_at"] = datetime.utcnow()
    
    # Calculate final results
    await calculate_ab_test_results(ab_test_id)
    
    return {"message": "A/B test stopped successfully"}

@app.get("/analytics/dashboard")
async def get_dashboard_analytics(
    date_range: int = Query(default=30, description="Days of data to include"),
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard analytics for Smart Campaigns"""
    
    return {
        "overview": {
            "total_campaigns": len(campaigns_db),
            "active_campaigns": len([c for c in campaigns_db.values() if c["status"] == CampaignStatus.ACTIVE]),
            "total_ab_tests": len(ab_tests_db),
            "running_ab_tests": len([t for t in ab_tests_db.values() if t["status"] == ABTestStatus.RUNNING])
        },
        "performance": {
            "total_calls": sum(m.get("total_calls", 0) for m in campaign_metrics_db.values()),
            "successful_calls": sum(m.get("successful_calls", 0) for m in campaign_metrics_db.values()),
            "average_conversion_rate": 12.5,
            "total_revenue": sum(m.get("revenue_generated", 0) for m in campaign_metrics_db.values()),
            "average_roi": 285.7
        },
        "trends": {
            "calls_per_day": [45, 52, 38, 61, 47, 55, 42],
            "conversion_rates": [11.2, 13.1, 9.8, 14.5, 12.3, 13.7, 10.9],
            "revenue_per_day": [2100, 2450, 1890, 2780, 2340, 2610, 2180]
        },
        "top_campaigns": [
            {
                "name": "Q4 Sales Outreach",
                "conversion_rate": 12.5,
                "calls": 247,
                "revenue": 15750.00
            }
        ]
    }

# Background Tasks

async def validate_campaign(campaign_id: str) -> Dict[str, Any]:
    """Validate campaign configuration"""
    
    campaign = campaigns_db.get(campaign_id)
    if not campaign:
        return {"valid": False, "errors": ["Campaign not found"]}
    
    errors = []
    
    # Validate agent exists
    if not campaign.get("agent_id"):
        errors.append("Agent ID is required")
    
    # Validate phone number exists
    if not campaign.get("phone_number_id"):
        errors.append("Phone number ID is required")
    
    # Validate script
    script = campaign.get("script", {})
    if not script.get("intro"):
        errors.append("Campaign script intro is required")
    
    # Validate settings
    settings = campaign.get("settings", {})
    if settings.get("max_concurrent_calls", 0) <= 0:
        errors.append("Max concurrent calls must be greater than 0")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "campaign_id": campaign_id
    }

async def execute_campaign(campaign_id: str):
    """Execute campaign (simulated)"""
    
    logger.info(f"Starting campaign execution for {campaign_id}")
    
    campaign = campaigns_db.get(campaign_id)
    if not campaign:
        return
    
    # Simulate campaign execution
    await asyncio.sleep(2)
    
    # Update metrics (simulated)
    metrics = campaign_metrics_db.get(campaign_id, {})
    metrics["total_calls"] = metrics.get("total_calls", 0) + 1
    metrics["last_updated"] = datetime.utcnow()
    
    # Simulate success/failure
    import random
    if random.random() > 0.2:  # 80% success rate
        metrics["successful_calls"] = metrics.get("successful_calls", 0) + 1
    else:
        metrics["failed_calls"] = metrics.get("failed_calls", 0) + 1
    
    # Update conversion rate
    if metrics["total_calls"] > 0:
        metrics["conversion_rate"] = (metrics["successful_calls"] / metrics["total_calls"]) * 100
    
    campaign_metrics_db[campaign_id] = metrics
    
    logger.info(f"Campaign {campaign_id} execution step completed")

async def start_ab_test(ab_test_id: str):
    """Start A/B test"""
    
    ab_test = ab_tests_db.get(ab_test_id)
    if not ab_test:
        return
    
    ab_test["status"] = ABTestStatus.RUNNING
    ab_test["started_at"] = datetime.utcnow()
    
    logger.info(f"A/B test {ab_test_id} started")

async def calculate_ab_test_results(ab_test_id: str):
    """Calculate A/B test statistical results"""
    
    ab_test = ab_tests_db.get(ab_test_id)
    if not ab_test:
        return
    
    # Simulated statistical calculation
    # In production, implement proper statistical significance testing
    results = {
        "statistical_significance": 0.95,
        "winner": ab_test["variants"][0]["name"],
        "confidence": 95.2,
        "recommendation": "Deploy winning variant to full traffic"
    }
    
    ab_test["results"].update(results)
    
    logger.info(f"A/B test {ab_test_id} results calculated")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=True,
        log_level="info"
    )