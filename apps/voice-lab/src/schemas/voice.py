"""
Voice Lab - Pydantic Schemas
Data validation and serialization models
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum


# Enums
class VoiceGender(str, Enum):
    male = "male"
    female = "female"

class VoiceAge(str, Enum):
    young = "young"
    middle_aged = "middle_aged"
    elderly = "elderly"

class VoiceCategory(str, Enum):
    premade = "premade"
    cloned = "cloned"
    custom = "custom"

class VoiceUseCase(str, Enum):
    business = "business"
    sales = "sales"
    executive = "executive"
    multilingual = "multilingual"
    general = "general"

class GenerationStatus(str, Enum):
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"

class CloningStatus(str, Enum):
    processing = "processing"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


# Voice Schemas
class VoiceSettings(BaseModel):
    stability: float = Field(0.7, ge=0.0, le=1.0, description="Voice stability (0-1)")
    similarity_boost: float = Field(0.8, ge=0.0, le=1.0, description="Similarity boost (0-1)")
    style: float = Field(0.2, ge=0.0, le=1.0, description="Style enhancement (0-1)")

class VoicePerformance(BaseModel):
    usage_count: int = Field(0, description="Total usage count")
    avg_sentiment: float = Field(0.75, description="Average sentiment score")
    success_rate: float = Field(85.0, description="Success rate percentage")

class VoiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Voice name")
    description: str = Field(..., min_length=1, max_length=500, description="Voice description")
    language: str = Field("en", description="Voice language code")
    gender: VoiceGender = Field(..., description="Voice gender")
    age: VoiceAge = Field(VoiceAge.young, description="Voice age category")
    accent: str = Field("american", description="Voice accent")
    use_case: VoiceUseCase = Field(VoiceUseCase.general, description="Primary use case")

class VoiceCreate(VoiceBase):
    settings: Optional[VoiceSettings] = Field(None, description="Voice generation settings")

class VoiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    settings: Optional[VoiceSettings] = None

class VoiceResponse(VoiceBase):
    voice_id: str = Field(..., description="Unique voice identifier")
    category: VoiceCategory = Field(..., description="Voice category")
    quality_score: float = Field(..., ge=0.0, le=100.0, description="Quality score")
    performance: VoicePerformance = Field(..., description="Performance metrics")
    settings: VoiceSettings = Field(..., description="Voice settings")
    preview_url: str = Field(..., description="Preview audio URL")
    cost_per_char: float = Field(..., description="Cost per character")
    available_for_tiers: List[str] = Field(..., description="Available pricing tiers")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class VoiceFilter(BaseModel):
    language: Optional[str] = None
    gender: Optional[str] = None
    category: Optional[str] = None
    use_case: Optional[str] = None
    quality_min: Optional[int] = Field(None, ge=0, le=100)
    search: Optional[str] = None
    limit: int = Field(50, ge=1, le=100)
    offset: int = Field(0, ge=0)

class VoiceComparison(BaseModel):
    sample_text: str = Field(..., description="Text used for comparison")
    voices: List[Dict[str, Any]] = Field(..., description="Compared voices with scores")


# Generation Schemas
class GenerationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Text to generate")
    voice_id: str = Field(..., description="Voice ID to use")
    settings: Optional[VoiceSettings] = Field(None, description="Override voice settings")
    format: str = Field("mp3", description="Output audio format")
    sample_rate: int = Field(22050, description="Audio sample rate")

class GenerationResponse(BaseModel):
    generation_id: str = Field(..., description="Generation job ID")
    voice_id: str = Field(..., description="Voice ID used")
    text: str = Field(..., description="Generated text")
    audio_url: str = Field(..., description="Generated audio URL")
    generation_time: float = Field(..., description="Generation time in seconds")
    character_count: int = Field(..., description="Number of characters")
    cost: float = Field(..., description="Generation cost")
    status: GenerationStatus = Field(..., description="Generation status")
    created_at: Optional[datetime] = None

class BatchGenerationRequest(BaseModel):
    generations: List[GenerationRequest] = Field(..., min_items=1, max_items=50)

class BatchGenerationResponse(BaseModel):
    batch_id: str = Field(..., description="Batch job ID")
    status: str = Field(..., description="Batch status")
    total_items: int = Field(..., description="Total items in batch")
    completed_items: int = Field(0, description="Completed items")
    failed_items: int = Field(0, description="Failed items")
    message: str = Field(..., description="Status message")
    estimated_completion: Optional[str] = None


# Cloning Schemas
class CloningRequest(BaseModel):
    voice_name: str = Field(..., min_length=1, max_length=100, description="Name for cloned voice")
    description: str = Field(..., min_length=1, max_length=500, description="Voice description")
    language: str = Field("en", description="Voice language")
    gender: VoiceGender = Field(..., description="Voice gender")
    use_case: VoiceUseCase = Field(VoiceUseCase.general, description="Intended use case")

class CloningResponse(BaseModel):
    clone_id: str = Field(..., description="Cloning job ID")
    status: CloningStatus = Field(..., description="Cloning status")
    voice_name: str = Field(..., description="Voice name")
    estimated_completion: str = Field(..., description="Estimated completion time")
    message: str = Field(..., description="Status message")

class CloningStatusResponse(BaseModel):
    clone_id: str = Field(..., description="Cloning job ID")
    status: CloningStatus = Field(..., description="Current status")
    progress: int = Field(0, ge=0, le=100, description="Progress percentage")
    current_step: Optional[str] = Field(None, description="Current processing step")
    voice_id: Optional[str] = Field(None, description="Generated voice ID")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Job creation time")
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class CloneValidation(BaseModel):
    is_valid: bool = Field(..., description="Whether audio is valid for cloning")
    duration: float = Field(..., description="Audio duration in seconds")
    sample_rate: int = Field(..., description="Audio sample rate")
    quality_score: float = Field(..., description="Audio quality score")
    recommendations: List[str] = Field(..., description="Improvement recommendations")


# Testing Schemas
class VoiceTestRequest(BaseModel):
    test_phrases: List[str] = Field(..., min_items=1, max_items=20, description="Phrases to test")
    metrics: List[str] = Field(["clarity", "naturalness", "consistency"], description="Metrics to evaluate")

class QualityMetrics(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=100.0, description="Overall quality score")
    clarity: float = Field(..., ge=0.0, le=100.0, description="Clarity score")
    naturalness: float = Field(..., ge=0.0, le=100.0, description="Naturalness score")
    consistency: float = Field(..., ge=0.0, le=100.0, description="Consistency score")
    emotion_range: float = Field(..., ge=0.0, le=100.0, description="Emotional range score")

class VoiceTestResult(BaseModel):
    test_id: str = Field(..., description="Test job ID")
    voice_id: str = Field(..., description="Tested voice ID")
    metrics: QualityMetrics = Field(..., description="Quality metrics")
    recommendation: str = Field(..., description="Usage recommendation")
    tested_phrases: int = Field(..., description="Number of phrases tested")
    generation_time: float = Field(..., description="Average generation time")
    status: str = Field(..., description="Test status")

class BatchTestRequest(BaseModel):
    voice_ids: List[str] = Field(..., min_items=2, max_items=20, description="Voices to test")
    test_phrases: List[str] = Field(..., min_items=1, max_items=10, description="Test phrases")
    metrics: List[str] = Field(["clarity", "naturalness", "consistency"], description="Metrics to evaluate")

class BatchTestResult(BaseModel):
    batch_id: str = Field(..., description="Batch test ID")
    status: str = Field(..., description="Batch status")
    total_voices: int = Field(..., description="Total voices to test")
    total_phrases: int = Field(..., description="Total phrases to test")
    completed_tests: int = Field(0, description="Completed tests")
    estimated_completion: str = Field(..., description="Estimated completion time")

class ABTestRequest(BaseModel):
    voice_ids: List[str] = Field(..., min_items=2, max_items=5, description="Voices to compare")
    test_scenarios: List[str] = Field(..., min_items=1, max_items=10, description="Test scenarios")
    metrics: List[str] = Field(["quality", "preference", "suitability"], description="Comparison metrics")

class ABTestResult(BaseModel):
    test_id: str = Field(..., description="A/B test ID")
    status: str = Field(..., description="Test status")
    voice_count: int = Field(..., description="Number of voices")
    scenario_count: int = Field(..., description="Number of scenarios")
    estimated_completion: str = Field(..., description="Estimated completion time")


# Analytics Schemas
class VoiceAnalytics(BaseModel):
    voice_id: str = Field(..., description="Voice ID")
    voice_name: str = Field(..., description="Voice name")
    period_days: int = Field(..., description="Analysis period in days")
    total_usage: int = Field(..., description="Total usage count")
    total_characters: int = Field(..., description="Total characters generated")
    total_cost: float = Field(..., description="Total cost")
    avg_generation_time: float = Field(..., description="Average generation time")
    success_rate: float = Field(..., description="Success rate percentage")
    quality_score: float = Field(..., description="Voice quality score")
    daily_usage: List[Dict[str, Any]] = Field(..., description="Daily usage statistics")
    performance_metrics: Dict[str, Any] = Field(..., description="Performance metrics")

class UsageReport(BaseModel):
    start_date: datetime = Field(..., description="Report start date")
    end_date: datetime = Field(..., description="Report end date")
    total_generations: int = Field(..., description="Total generations")
    total_characters: int = Field(..., description="Total characters")
    total_cost: float = Field(..., description="Total cost")
    unique_voices: int = Field(..., description="Unique voices used")
    top_voices: List[Dict[str, Any]] = Field(..., description="Top performing voices")
    cost_breakdown: Dict[str, float] = Field(..., description="Cost breakdown by category")
    daily_statistics: List[Dict[str, Any]] = Field(..., description="Daily statistics")

class PerformanceInsights(BaseModel):
    period_days: int = Field(..., description="Analysis period")
    insights: List[Dict[str, Any]] = Field(..., description="Performance insights")
    recommendations: List[str] = Field(..., description="Optimization recommendations")
    trends: Dict[str, Any] = Field(..., description="Performance trends")
    alerts: List[Dict[str, Any]] = Field(..., description="Performance alerts")

class CostAnalysis(BaseModel):
    period_days: int = Field(..., description="Analysis period")
    total_cost: float = Field(..., description="Total cost")
    cost_per_character: float = Field(..., description="Average cost per character")
    cost_by_voice_category: Dict[str, float] = Field(..., description="Cost breakdown by category")
    cost_trends: List[Dict[str, Any]] = Field(..., description="Cost trends over time")
    optimization_potential: float = Field(..., description="Potential cost savings")
    recommendations: List[str] = Field(..., description="Cost optimization recommendations")

class TrendReport(BaseModel):
    metric: str = Field(..., description="Analyzed metric")
    period_days: int = Field(..., description="Analysis period")
    trend_direction: str = Field(..., description="Trend direction (up/down/stable)")
    trend_strength: float = Field(..., description="Trend strength (0-1)")
    data_points: List[Dict[str, Any]] = Field(..., description="Trend data points")
    predictions: List[Dict[str, Any]] = Field(..., description="Future predictions")
    insights: List[str] = Field(..., description="Trend insights")


# Common Response Schemas
class SuccessResponse(BaseModel):
    success: bool = Field(True, description="Operation success status")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")

class ErrorResponse(BaseModel):
    success: bool = Field(False, description="Operation success status")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")

class PaginatedResponse(BaseModel):
    items: List[Any] = Field(..., description="Result items")
    total: int = Field(..., description="Total items count")
    page: int = Field(..., description="Current page")
    per_page: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total pages")
    has_next: bool = Field(..., description="Has next page")
    has_prev: bool = Field(..., description="Has previous page")


# Webhook Schemas
class VoiceWebhookEvent(BaseModel):
    event_type: str = Field(..., description="Event type")
    voice_id: str = Field(..., description="Voice ID")
    user_id: str = Field(..., description="User ID")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")

class GenerationWebhookEvent(BaseModel):
    event_type: str = Field(..., description="Event type")
    generation_id: str = Field(..., description="Generation ID")
    voice_id: str = Field(..., description="Voice ID")
    user_id: str = Field(..., description="User ID")
    status: GenerationStatus = Field(..., description="Generation status")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")

class CloningWebhookEvent(BaseModel):
    event_type: str = Field(..., description="Event type")
    clone_id: str = Field(..., description="Clone ID")
    user_id: str = Field(..., description="User ID")
    status: CloningStatus = Field(..., description="Cloning status")
    progress: int = Field(..., description="Progress percentage")
    timestamp: datetime = Field(..., description="Event timestamp")
    data: Dict[str, Any] = Field(..., description="Event data")


# File Upload Schemas
class AudioFileInfo(BaseModel):
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size in bytes")
    duration: Optional[float] = Field(None, description="Audio duration in seconds")
    format: str = Field(..., description="Audio format")
    sample_rate: Optional[int] = Field(None, description="Sample rate")
    channels: Optional[int] = Field(None, description="Number of channels")
    bitrate: Optional[int] = Field(None, description="Bitrate")

class FileUploadResponse(BaseModel):
    file_id: str = Field(..., description="Uploaded file ID")
    filename: str = Field(..., description="Original filename")
    size: int = Field(..., description="File size")
    url: str = Field(..., description="File access URL")
    info: AudioFileInfo = Field(..., description="Audio file information")


# Settings and Configuration Schemas
class VoiceLabSettings(BaseModel):
    auto_optimize: bool = Field(True, description="Enable automatic optimization")
    quality_threshold: float = Field(85.0, description="Minimum quality threshold")
    cost_alerts: bool = Field(True, description="Enable cost alerts")
    usage_notifications: bool = Field(True, description="Enable usage notifications")
    default_voice_settings: VoiceSettings = Field(..., description="Default voice settings")
    supported_formats: List[str] = Field(["mp3", "wav"], description="Supported audio formats")
    max_text_length: int = Field(5000, description="Maximum text length")
    max_file_size: int = Field(10485760, description="Maximum file size in bytes")

class UserPreferences(BaseModel):
    preferred_voices: List[str] = Field([], description="User's preferred voice IDs")
    default_language: str = Field("en", description="Default language")
    auto_enhance_audio: bool = Field(True, description="Auto-enhance uploaded audio")
    notification_settings: Dict[str, bool] = Field({
        "generation_complete": True,
        "cloning_complete": True,
        "quality_alerts": True,
        "cost_alerts": True
    }, description="Notification preferences")


# Export and Import Schemas
class ExportRequest(BaseModel):
    format: str = Field(..., description="Export format (csv, json, pdf, excel)")
    date_range: Optional[Dict[str, datetime]] = Field(None, description="Date range filter")
    voice_ids: Optional[List[str]] = Field(None, description="Specific voice IDs")
    include_audio: bool = Field(False, description="Include audio files in export")

class ExportResponse(BaseModel):
    export_id: str = Field(..., description="Export job ID")
    format: str = Field(..., description="Export format")
    status: str = Field(..., description="Export status")
    download_url: Optional[str] = Field(None, description="Download URL when ready")
    expires_at: Optional[datetime] = Field(None, description="Download link expiration")
    file_size: Optional[int] = Field(None, description="File size in bytes")

class ImportRequest(BaseModel):
    source: str = Field(..., description="Import source (file, url, service)")
    format: str = Field(..., description="Source format")
    mapping: Dict[str, str] = Field(..., description="Field mapping configuration")
    options: Dict[str, Any] = Field({}, description="Import options")

class ImportResponse(BaseModel):
    import_id: str = Field(..., description="Import job ID")
    status: str = Field(..., description="Import status")
    total_items: int = Field(0, description="Total items to import")
    processed_items: int = Field(0, description="Processed items")
    failed_items: int = Field(0, description="Failed items")
    errors: List[str] = Field([], description="Import errors")


# Real-time Metrics Schemas
class RealTimeMetrics(BaseModel):
    active_generations: int = Field(..., description="Currently active generations")
    queue_length: int = Field(..., description="Generation queue length")
    avg_processing_time: float = Field(..., description="Average processing time")
    system_load: float = Field(..., description="System load percentage")
    error_rate: float = Field(..., description="Current error rate")
    throughput: float = Field(..., description="Generations per minute")
    last_updated: datetime = Field(..., description="Last update timestamp")

class SystemHealth(BaseModel):
    status: str = Field(..., description="Overall system status")
    services: Dict[str, str] = Field(..., description="Service statuses")
    database: str = Field(..., description="Database status")
    storage: str = Field(..., description="Storage status")
    ai_engine: str = Field(..., description="AI engine status")
    uptime: float = Field(..., description="System uptime in hours")
    version: str = Field(..., description="Service version")


# Validation Helpers
@validator('text', pre=True)
def validate_text_content(cls, v):
    """Validate text content for generation"""
    if not v or not v.strip():
        raise ValueError("Text content cannot be empty")
    if len(v) > 5000:
        raise ValueError("Text content too long (max 5000 characters)")
    return v.strip()

@validator('voice_id', pre=True) 
def validate_voice_id(cls, v):
    """Validate voice ID format"""
    if not v:
        raise ValueError("Voice ID is required")
    if not isinstance(v, str):
        raise ValueError("Voice ID must be a string")
    return v

@validator('cost_per_char')
def validate_cost(cls, v):
    """Validate cost values"""
    if v < 0:
        raise ValueError("Cost cannot be negative")
    if v > 1.0:
        raise ValueError("Cost per character too high")
    return v

@validator('quality_score')
def validate_quality_score(cls, v):
    """Validate quality score range"""
    if not 0 <= v <= 100:
        raise ValueError("Quality score must be between 0 and 100")
    return v