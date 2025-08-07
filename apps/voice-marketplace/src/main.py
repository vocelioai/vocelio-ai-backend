"""
Voice Marketplace Service - Vocelio AI Call Center
Manages voice providers, pricing, quality metrics, and optimization recommendations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import aiohttp
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Voice Provider Models
class VoiceProviderStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    TESTING = "testing"

class VoiceQuality(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class VoiceProvider(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    api_endpoint: str
    pricing_per_minute: float
    currency: str = "USD"
    quality_rating: VoiceQuality
    latency_ms: int
    supported_languages: List[str]
    supported_voices: List[str]
    status: VoiceProviderStatus
    api_key_required: bool
    webhook_support: bool
    real_time_streaming: bool
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    monthly_usage_minutes: int = 0
    monthly_cost: float = 0.0
    success_rate: float = 100.0
    error_rate: float = 0.0

class VoiceProviderCreate(BaseModel):
    name: str
    description: str
    api_endpoint: str
    pricing_per_minute: float
    currency: str = "USD"
    quality_rating: VoiceQuality
    latency_ms: int
    supported_languages: List[str]
    supported_voices: List[str]
    api_key_required: bool = True
    webhook_support: bool = False
    real_time_streaming: bool = False

class VoiceProviderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    api_endpoint: Optional[str] = None
    pricing_per_minute: Optional[float] = None
    quality_rating: Optional[VoiceQuality] = None
    latency_ms: Optional[int] = None
    supported_languages: Optional[List[str]] = None
    supported_voices: Optional[List[str]] = None
    status: Optional[VoiceProviderStatus] = None
    webhook_support: Optional[bool] = None
    real_time_streaming: Optional[bool] = None

# Voice Configuration Models
class VoiceConfiguration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    provider_id: str
    voice_id: str
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0
    emotion: Optional[str] = None
    accent: Optional[str] = None
    language: str = "en-US"
    sample_rate: int = 22050
    bit_depth: int = 16
    format: str = "mp3"
    is_default: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    usage_count: int = 0
    average_rating: float = 0.0

class VoiceConfigurationCreate(BaseModel):
    name: str
    provider_id: str
    voice_id: str
    speed: float = 1.0
    pitch: float = 1.0
    volume: float = 1.0
    emotion: Optional[str] = None
    accent: Optional[str] = None
    language: str = "en-US"
    sample_rate: int = 22050
    bit_depth: int = 16
    format: str = "mp3"
    is_default: bool = False

# Usage Analytics Models
class VoiceUsageRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    provider_id: str
    configuration_id: Optional[str] = None
    call_id: str
    duration_minutes: float
    cost: float
    quality_score: float
    latency_ms: int
    success: bool
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class VoiceAnalytics(BaseModel):
    provider_id: str
    total_usage_minutes: float
    total_cost: float
    average_quality_score: float
    average_latency_ms: float
    success_rate: float
    error_rate: float
    cost_per_minute: float
    usage_trend: List[Dict[str, Any]]
    quality_trend: List[Dict[str, Any]]

# Optimization Models
class OptimizationRecommendation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # "cost", "quality", "latency", "reliability"
    title: str
    description: str
    current_provider: str
    recommended_provider: str
    estimated_savings: Optional[float] = None
    quality_improvement: Optional[float] = None
    latency_improvement: Optional[int] = None
    confidence_score: float
    impact: str  # "high", "medium", "low"
    created_at: datetime = Field(default_factory=datetime.now)

class MarketplaceMetrics(BaseModel):
    total_providers: int
    active_providers: int
    total_configurations: int
    monthly_usage_minutes: float
    monthly_cost: float
    average_cost_per_minute: float
    best_quality_provider: str
    most_cost_effective_provider: str
    fastest_provider: str
    most_reliable_provider: str

# Sample Data
SAMPLE_PROVIDERS = [
    VoiceProvider(
        name="ElevenLabs",
        description="Premium AI voice synthesis with natural sounding voices",
        api_endpoint="https://api.elevenlabs.io/v1",
        pricing_per_minute=0.35,
        quality_rating=VoiceQuality.EXCELLENT,
        latency_ms=150,
        supported_languages=["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "it-IT", "pt-BR"],
        supported_voices=["Rachel", "Drew", "Clyde", "Paul", "Domi", "Dave", "Fin", "Sarah"],
        status=VoiceProviderStatus.ACTIVE,
        api_key_required=True,
        webhook_support=True,
        real_time_streaming=True,
        monthly_usage_minutes=1250,
        monthly_cost=437.50,
        success_rate=99.8,
        error_rate=0.2
    ),
    VoiceProvider(
        name="Ramble.AI",
        description="Fast and affordable AI voice generation",
        api_endpoint="https://api.ramble.ai/v2",
        pricing_per_minute=0.18,
        quality_rating=VoiceQuality.GOOD,
        latency_ms=95,
        supported_languages=["en-US", "en-GB", "es-ES", "fr-FR", "de-DE"],
        supported_voices=["Alex", "Emma", "Brian", "Amy", "Joanna", "Matthew", "Ivy"],
        status=VoiceProviderStatus.ACTIVE,
        api_key_required=True,
        webhook_support=False,
        real_time_streaming=True,
        monthly_usage_minutes=2150,
        monthly_cost=387.00,
        success_rate=98.5,
        error_rate=1.5
    ),
    VoiceProvider(
        name="Piper TTS",
        description="Open-source neural text-to-speech with local processing",
        api_endpoint="http://localhost:59125/api",
        pricing_per_minute=0.08,
        quality_rating=VoiceQuality.FAIR,
        latency_ms=80,
        supported_languages=["en-US", "en-GB", "es-ES", "fr-FR"],
        supported_voices=["en_US-lessac-high", "en_US-ryan-high", "en_GB-alan-medium"],
        status=VoiceProviderStatus.ACTIVE,
        api_key_required=False,
        webhook_support=False,
        real_time_streaming=False,
        monthly_usage_minutes=890,
        monthly_cost=71.20,
        success_rate=97.2,
        error_rate=2.8
    ),
    VoiceProvider(
        name="Azure Cognitive Services",
        description="Microsoft's enterprise-grade speech synthesis",
        api_endpoint="https://cognitiveservices.azure.com/sts/v1.0",
        pricing_per_minute=0.25,
        quality_rating=VoiceQuality.EXCELLENT,
        latency_ms=120,
        supported_languages=["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "ja-JP", "zh-CN"],
        supported_voices=["Aria", "Davis", "Guy", "Jane", "Jason", "Jenny", "Nancy", "Sara"],
        status=VoiceProviderStatus.TESTING,
        api_key_required=True,
        webhook_support=True,
        real_time_streaming=True,
        monthly_usage_minutes=450,
        monthly_cost=112.50,
        success_rate=99.9,
        error_rate=0.1
    ),
    VoiceProvider(
        name="Google Cloud Text-to-Speech",
        description="Google's high-quality neural voices",
        api_endpoint="https://texttospeech.googleapis.com/v1",
        pricing_per_minute=0.22,
        quality_rating=VoiceQuality.GOOD,
        latency_ms=110,
        supported_languages=["en-US", "en-GB", "es-ES", "fr-FR", "de-DE", "ja-JP", "hi-IN"],
        supported_voices=["en-US-Standard-A", "en-US-Standard-B", "en-US-Wavenet-A", "en-US-Neural2-A"],
        status=VoiceProviderStatus.INACTIVE,
        api_key_required=True,
        webhook_support=False,
        real_time_streaming=True,
        monthly_usage_minutes=0,
        monthly_cost=0.0,
        success_rate=99.6,
        error_rate=0.4
    )
]

SAMPLE_CONFIGURATIONS = [
    VoiceConfiguration(
        name="Professional Female - English",
        provider_id=SAMPLE_PROVIDERS[0].id,  # ElevenLabs
        voice_id="Rachel",
        speed=1.0,
        pitch=1.0,
        volume=0.9,
        emotion="professional",
        language="en-US",
        is_default=True,
        usage_count=542,
        average_rating=4.8
    ),
    VoiceConfiguration(
        name="Friendly Male - Support",
        provider_id=SAMPLE_PROVIDERS[1].id,  # Ramble.AI
        voice_id="Alex",
        speed=0.95,
        pitch=0.9,
        volume=1.0,
        emotion="friendly",
        language="en-US",
        usage_count=387,
        average_rating=4.6
    ),
    VoiceConfiguration(
        name="Budget Option - Basic",
        provider_id=SAMPLE_PROVIDERS[2].id,  # Piper TTS
        voice_id="en_US-lessac-high",
        speed=1.1,
        pitch=1.0,
        volume=0.95,
        language="en-US",
        usage_count=234,
        average_rating=4.2
    )
]

SAMPLE_USAGE_RECORDS = [
    VoiceUsageRecord(
        provider_id=SAMPLE_PROVIDERS[0].id,
        configuration_id=SAMPLE_CONFIGURATIONS[0].id,
        call_id="call_001",
        duration_minutes=2.5,
        cost=0.875,
        quality_score=9.2,
        latency_ms=145,
        success=True
    ),
    VoiceUsageRecord(
        provider_id=SAMPLE_PROVIDERS[1].id,
        configuration_id=SAMPLE_CONFIGURATIONS[1].id,
        call_id="call_002",
        duration_minutes=4.2,
        cost=0.756,
        quality_score=8.7,
        latency_ms=92,
        success=True
    ),
    VoiceUsageRecord(
        provider_id=SAMPLE_PROVIDERS[2].id,
        configuration_id=SAMPLE_CONFIGURATIONS[2].id,
        call_id="call_003",
        duration_minutes=1.8,
        cost=0.144,
        quality_score=7.8,
        latency_ms=78,
        success=True
    )
]

# Global storage
voice_providers: List[VoiceProvider] = []
voice_configurations: List[VoiceConfiguration] = []
usage_records: List[VoiceUsageRecord] = []
optimization_recommendations: List[OptimizationRecommendation] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global voice_providers, voice_configurations, usage_records, optimization_recommendations
    
    voice_providers.extend(SAMPLE_PROVIDERS)
    voice_configurations.extend(SAMPLE_CONFIGURATIONS)
    usage_records.extend(SAMPLE_USAGE_RECORDS)
    
    # Generate optimization recommendations
    optimization_recommendations.extend([
        OptimizationRecommendation(
            type="cost",
            title="Switch to Ramble.AI for Cost Savings",
            description="Save 48% on voice costs by switching from ElevenLabs to Ramble.AI for non-critical calls",
            current_provider="ElevenLabs",
            recommended_provider="Ramble.AI",
            estimated_savings=210.25,
            confidence_score=0.85,
            impact="high"
        ),
        OptimizationRecommendation(
            type="quality",
            title="Use Azure for Premium Calls",
            description="Achieve 99.9% success rate for high-priority calls with Azure Cognitive Services",
            current_provider="Piper TTS",
            recommended_provider="Azure Cognitive Services",
            quality_improvement=2.7,
            confidence_score=0.92,
            impact="medium"
        ),
        OptimizationRecommendation(
            type="latency",
            title="Optimize for Speed with Piper TTS",
            description="Reduce latency by 45ms using Piper TTS for real-time applications",
            current_provider="ElevenLabs",
            recommended_provider="Piper TTS",
            latency_improvement=70,
            confidence_score=0.78,
            impact="medium"
        )
    ])
    
    logger.info("Sample data initialized successfully")

async def update_provider_metrics():
    """Background task to update provider metrics"""
    while True:
        try:
            for provider in voice_providers:
                if provider.status == VoiceProviderStatus.ACTIVE:
                    # Simulate real-time metrics updates
                    provider.monthly_usage_minutes += 0.5
                    provider.monthly_cost = provider.monthly_usage_minutes * provider.pricing_per_minute
                    
            logger.info("Provider metrics updated")
        except Exception as e:
            logger.error(f"Error updating provider metrics: {e}")
        
        await asyncio.sleep(30)  # Update every 30 seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    
    # Start background tasks
    metrics_task = asyncio.create_task(update_provider_metrics())
    
    yield
    
    # Shutdown
    metrics_task.cancel()
    try:
        await metrics_task
    except asyncio.CancelledError:
        pass

# FastAPI app
app = FastAPI(
    title="Voice Marketplace Service",
    description="Manages voice providers, pricing, quality metrics, and optimization recommendations for Vocelio AI Call Center",
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

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "voice-marketplace",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Voice Providers Endpoints
@app.get("/providers", response_model=List[VoiceProvider])
async def get_voice_providers(
    status: Optional[VoiceProviderStatus] = None,
    quality: Optional[VoiceQuality] = None,
    max_price: Optional[float] = None
):
    """Get all voice providers with optional filtering"""
    filtered_providers = voice_providers
    
    if status:
        filtered_providers = [p for p in filtered_providers if p.status == status]
    
    if quality:
        filtered_providers = [p for p in filtered_providers if p.quality_rating == quality]
    
    if max_price:
        filtered_providers = [p for p in filtered_providers if p.pricing_per_minute <= max_price]
    
    return filtered_providers

@app.get("/providers/{provider_id}", response_model=VoiceProvider)
async def get_voice_provider(provider_id: str):
    """Get a specific voice provider by ID"""
    provider = next((p for p in voice_providers if p.id == provider_id), None)
    if not provider:
        raise HTTPException(status_code=404, detail="Voice provider not found")
    return provider

@app.post("/providers", response_model=VoiceProvider)
async def create_voice_provider(provider_data: VoiceProviderCreate):
    """Create a new voice provider"""
    new_provider = VoiceProvider(**provider_data.dict())
    voice_providers.append(new_provider)
    return new_provider

@app.put("/providers/{provider_id}", response_model=VoiceProvider)
async def update_voice_provider(provider_id: str, provider_data: VoiceProviderUpdate):
    """Update a voice provider"""
    provider = next((p for p in voice_providers if p.id == provider_id), None)
    if not provider:
        raise HTTPException(status_code=404, detail="Voice provider not found")
    
    update_data = provider_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(provider, field, value)
    
    provider.updated_at = datetime.now()
    return provider

@app.delete("/providers/{provider_id}")
async def delete_voice_provider(provider_id: str):
    """Delete a voice provider"""
    global voice_providers
    provider = next((p for p in voice_providers if p.id == provider_id), None)
    if not provider:
        raise HTTPException(status_code=404, detail="Voice provider not found")
    
    voice_providers = [p for p in voice_providers if p.id != provider_id]
    return {"message": "Voice provider deleted successfully"}

# Voice Configurations Endpoints
@app.get("/configurations", response_model=List[VoiceConfiguration])
async def get_voice_configurations(provider_id: Optional[str] = None):
    """Get all voice configurations, optionally filtered by provider"""
    if provider_id:
        return [c for c in voice_configurations if c.provider_id == provider_id]
    return voice_configurations

@app.get("/configurations/{config_id}", response_model=VoiceConfiguration)
async def get_voice_configuration(config_id: str):
    """Get a specific voice configuration by ID"""
    config = next((c for c in voice_configurations if c.id == config_id), None)
    if not config:
        raise HTTPException(status_code=404, detail="Voice configuration not found")
    return config

@app.post("/configurations", response_model=VoiceConfiguration)
async def create_voice_configuration(config_data: VoiceConfigurationCreate):
    """Create a new voice configuration"""
    # Verify provider exists
    provider = next((p for p in voice_providers if p.id == config_data.provider_id), None)
    if not provider:
        raise HTTPException(status_code=404, detail="Voice provider not found")
    
    new_config = VoiceConfiguration(**config_data.dict())
    voice_configurations.append(new_config)
    return new_config

@app.delete("/configurations/{config_id}")
async def delete_voice_configuration(config_id: str):
    """Delete a voice configuration"""
    global voice_configurations
    config = next((c for c in voice_configurations if c.id == config_id), None)
    if not config:
        raise HTTPException(status_code=404, detail="Voice configuration not found")
    
    voice_configurations = [c for c in voice_configurations if c.id != config_id]
    return {"message": "Voice configuration deleted successfully"}

# Analytics Endpoints
@app.get("/analytics/providers/{provider_id}", response_model=VoiceAnalytics)
async def get_provider_analytics(provider_id: str):
    """Get analytics for a specific voice provider"""
    provider = next((p for p in voice_providers if p.id == provider_id), None)
    if not provider:
        raise HTTPException(status_code=404, detail="Voice provider not found")
    
    provider_records = [r for r in usage_records if r.provider_id == provider_id]
    
    if not provider_records:
        return VoiceAnalytics(
            provider_id=provider_id,
            total_usage_minutes=0,
            total_cost=0,
            average_quality_score=0,
            average_latency_ms=0,
            success_rate=0,
            error_rate=0,
            cost_per_minute=provider.pricing_per_minute,
            usage_trend=[],
            quality_trend=[]
        )
    
    total_usage = sum(r.duration_minutes for r in provider_records)
    total_cost = sum(r.cost for r in provider_records)
    avg_quality = sum(r.quality_score for r in provider_records) / len(provider_records)
    avg_latency = sum(r.latency_ms for r in provider_records) / len(provider_records)
    success_count = sum(1 for r in provider_records if r.success)
    success_rate = (success_count / len(provider_records)) * 100
    error_rate = 100 - success_rate
    
    return VoiceAnalytics(
        provider_id=provider_id,
        total_usage_minutes=total_usage,
        total_cost=total_cost,
        average_quality_score=avg_quality,
        average_latency_ms=int(avg_latency),
        success_rate=success_rate,
        error_rate=error_rate,
        cost_per_minute=provider.pricing_per_minute,
        usage_trend=[
            {"date": "2024-01-01", "minutes": total_usage * 0.3},
            {"date": "2024-01-02", "minutes": total_usage * 0.7},
            {"date": "2024-01-03", "minutes": total_usage}
        ],
        quality_trend=[
            {"date": "2024-01-01", "score": avg_quality * 0.95},
            {"date": "2024-01-02", "score": avg_quality * 0.98},
            {"date": "2024-01-03", "score": avg_quality}
        ]
    )

@app.get("/analytics/marketplace", response_model=MarketplaceMetrics)
async def get_marketplace_metrics():
    """Get overall marketplace metrics"""
    active_providers = [p for p in voice_providers if p.status == VoiceProviderStatus.ACTIVE]
    
    total_usage = sum(p.monthly_usage_minutes for p in active_providers)
    total_cost = sum(p.monthly_cost for p in active_providers)
    avg_cost = total_cost / total_usage if total_usage > 0 else 0
    
    # Find best providers
    best_quality = max(active_providers, key=lambda p: p.success_rate, default=active_providers[0])
    most_cost_effective = min(active_providers, key=lambda p: p.pricing_per_minute, default=active_providers[0])
    fastest = min(active_providers, key=lambda p: p.latency_ms, default=active_providers[0])
    most_reliable = max(active_providers, key=lambda p: p.success_rate, default=active_providers[0])
    
    return MarketplaceMetrics(
        total_providers=len(voice_providers),
        active_providers=len(active_providers),
        total_configurations=len(voice_configurations),
        monthly_usage_minutes=total_usage,
        monthly_cost=total_cost,
        average_cost_per_minute=avg_cost,
        best_quality_provider=best_quality.name,
        most_cost_effective_provider=most_cost_effective.name,
        fastest_provider=fastest.name,
        most_reliable_provider=most_reliable.name
    )

# Usage Tracking Endpoints
@app.post("/usage/record")
async def record_voice_usage(usage_data: VoiceUsageRecord):
    """Record voice usage for analytics"""
    usage_records.append(usage_data)
    
    # Update provider usage statistics
    provider = next((p for p in voice_providers if p.id == usage_data.provider_id), None)
    if provider:
        provider.monthly_usage_minutes += usage_data.duration_minutes
        provider.monthly_cost += usage_data.cost
    
    return {"message": "Usage recorded successfully"}

@app.get("/usage/records", response_model=List[VoiceUsageRecord])
async def get_usage_records(
    provider_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get usage records with optional filtering"""
    filtered_records = usage_records
    
    if provider_id:
        filtered_records = [r for r in filtered_records if r.provider_id == provider_id]
    
    if start_date:
        filtered_records = [r for r in filtered_records if r.timestamp >= start_date]
    
    if end_date:
        filtered_records = [r for r in filtered_records if r.timestamp <= end_date]
    
    return filtered_records

# Optimization Endpoints
@app.get("/optimization/recommendations", response_model=List[OptimizationRecommendation])
async def get_optimization_recommendations(recommendation_type: Optional[str] = None):
    """Get optimization recommendations"""
    if recommendation_type:
        return [r for r in optimization_recommendations if r.type == recommendation_type]
    return optimization_recommendations

@app.post("/optimization/analyze")
async def analyze_optimization_opportunities(background_tasks: BackgroundTasks):
    """Analyze current usage and generate optimization recommendations"""
    background_tasks.add_task(generate_optimization_recommendations)
    return {"message": "Optimization analysis started"}

async def generate_optimization_recommendations():
    """Generate new optimization recommendations based on current usage"""
    # This would contain complex optimization logic
    # For now, we'll add a simple recommendation
    new_recommendation = OptimizationRecommendation(
        type="efficiency",
        title="Load Balance Between Providers",
        description="Distribute calls across multiple providers to improve reliability and reduce costs",
        current_provider="Single Provider",
        recommended_provider="Multi-Provider Strategy",
        estimated_savings=156.75,
        confidence_score=0.88,
        impact="high"
    )
    
    optimization_recommendations.append(new_recommendation)
    logger.info("New optimization recommendation generated")

# Testing Endpoints
@app.post("/providers/{provider_id}/test")
async def test_voice_provider(provider_id: str, test_text: str = "Hello, this is a test message"):
    """Test a voice provider with sample text"""
    provider = next((p for p in voice_providers if p.id == provider_id), None)
    if not provider:
        raise HTTPException(status_code=404, detail="Voice provider not found")
    
    # Simulate API call to provider
    await asyncio.sleep(provider.latency_ms / 1000)  # Simulate latency
    
    # Simulate test results
    test_result = {
        "provider_id": provider_id,
        "test_text": test_text,
        "success": True,
        "latency_ms": provider.latency_ms,
        "quality_score": 8.5 + (hash(provider_id) % 10) / 10,
        "audio_url": f"https://example.com/test_audio_{provider_id}.mp3",
        "timestamp": datetime.now().isoformat()
    }
    
    return test_result

# Comparison Endpoints
@app.get("/compare/providers")
async def compare_providers(provider_ids: List[str]):
    """Compare multiple voice providers"""
    providers = [p for p in voice_providers if p.id in provider_ids]
    
    if len(providers) < 2:
        raise HTTPException(status_code=400, detail="At least 2 providers required for comparison")
    
    comparison = {
        "providers": providers,
        "comparison_metrics": {
            "pricing": {p.name: p.pricing_per_minute for p in providers},
            "quality": {p.name: p.quality_rating for p in providers},
            "latency": {p.name: p.latency_ms for p in providers},
            "success_rate": {p.name: p.success_rate for p in providers},
            "languages": {p.name: len(p.supported_languages) for p in providers}
        },
        "recommendation": max(providers, key=lambda p: p.success_rate / p.pricing_per_minute).name
    }
    
    return comparison

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8020)