"""
Voice Lab Service - Vocelio AI Call Center
Advanced voice cloning, synthesis, custom voice training, and voice quality optimization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
import base64
import hashlib
from pathlib import Path
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Voice Lab Models
class VoiceQuality(str, Enum):
    DRAFT = "draft"
    GOOD = "good"
    EXCELLENT = "excellent"
    PROFESSIONAL = "professional"
    STUDIO = "studio"

class VoiceGender(str, Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"

class VoiceAge(str, Enum):
    CHILD = "child"
    YOUNG_ADULT = "young_adult"
    ADULT = "adult"
    MIDDLE_AGED = "middle_aged"
    SENIOR = "senior"

class VoiceAccent(str, Enum):
    AMERICAN = "american"
    BRITISH = "british"
    AUSTRALIAN = "australian"
    CANADIAN = "canadian"
    IRISH = "irish"
    SCOTTISH = "scottish"
    SOUTH_AFRICAN = "south_african"
    INDIAN = "indian"
    NEUTRAL = "neutral"

class VoiceEmotion(str, Enum):
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    CONFIDENT = "confident"
    FRIENDLY = "friendly"
    PROFESSIONAL = "professional"
    EMPATHETIC = "empathetic"
    AUTHORITATIVE = "authoritative"

class TrainingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    TRAINING = "training"
    OPTIMIZING = "optimizing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class VoiceStyle(BaseModel):
    speaking_rate: float = Field(default=1.0, ge=0.5, le=2.0)  # 0.5x to 2.0x speed
    pitch: float = Field(default=0.0, ge=-20.0, le=20.0)  # semitones
    volume_gain: float = Field(default=0.0, ge=-10.0, le=10.0)  # dB
    emphasis: float = Field(default=1.0, ge=0.0, le=2.0)  # emphasis level
    pause_length: float = Field(default=1.0, ge=0.1, le=3.0)  # pause multiplier
    breath_sounds: bool = True
    filler_words: bool = False
    pronunciation_style: str = "standard"  # "standard", "casual", "formal"

class VoiceMetrics(BaseModel):
    clarity_score: float = Field(ge=0.0, le=10.0)
    naturalness_score: float = Field(ge=0.0, le=10.0)
    emotion_accuracy: float = Field(ge=0.0, le=100.0)
    pronunciation_accuracy: float = Field(ge=0.0, le=100.0)
    consistency_score: float = Field(ge=0.0, le=10.0)
    background_noise_level: float = Field(ge=0.0, le=100.0)
    signal_to_noise_ratio: float = Field(ge=0.0, le=100.0)
    frequency_response: Dict[str, float] = {}
    dynamic_range: float = Field(ge=0.0, le=100.0)

class VoiceModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    original_speaker: str
    gender: VoiceGender
    age: VoiceAge
    accent: VoiceAccent
    primary_emotion: VoiceEmotion
    quality: VoiceQuality
    style: VoiceStyle = Field(default_factory=VoiceStyle)
    metrics: Optional[VoiceMetrics] = None
    training_status: TrainingStatus
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    trained_at: Optional[datetime] = None
    model_version: str = "1.0.0"
    training_duration_minutes: Optional[int] = None
    training_samples_count: int = 0
    usage_count: int = 0
    average_rating: float = 0.0
    file_size_mb: Optional[float] = None
    supported_languages: List[str] = ["en-US"]
    tags: List[str] = []
    is_public: bool = False
    license_type: str = "standard"  # "standard", "commercial", "enterprise"
    cost_per_minute: float = 0.0

class TrainingSample(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    voice_model_id: str
    text_content: str
    audio_file_path: str
    duration_seconds: float
    quality_score: float = Field(ge=0.0, le=10.0)
    emotion_tags: List[VoiceEmotion] = []
    phoneme_coverage: float = Field(ge=0.0, le=100.0)
    background_noise: bool = False
    uploaded_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}

class VoiceCloneRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    original_speaker: str
    target_quality: VoiceQuality
    training_samples: List[str] = []  # Sample IDs
    custom_style: Optional[VoiceStyle] = None
    requested_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: TrainingStatus
    progress_percentage: float = 0.0
    estimated_completion: Optional[datetime] = None
    error_message: Optional[str] = None
    result_model_id: Optional[str] = None

class SynthesisRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    voice_model_id: str
    text_content: str
    emotion: VoiceEmotion = VoiceEmotion.NEUTRAL
    style_overrides: Optional[VoiceStyle] = None
    output_format: str = "mp3"  # "mp3", "wav", "ogg"
    sample_rate: int = 22050
    bit_depth: int = 16
    requested_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    status: str = "pending"  # "pending", "processing", "completed", "failed"
    output_file_path: Optional[str] = None
    duration_seconds: Optional[float] = None
    file_size_bytes: Optional[int] = None
    processing_time_ms: Optional[float] = None
    cost: float = 0.0

class VoiceOptimization(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    voice_model_id: str
    optimization_type: str  # "clarity", "naturalness", "emotion", "speed"
    parameters: Dict[str, Any] = {}
    before_metrics: Optional[VoiceMetrics] = None
    after_metrics: Optional[VoiceMetrics] = None
    improvement_score: Optional[float] = None
    applied_at: datetime = Field(default_factory=datetime.now)
    applied_by: str

class VoiceAnalytics(BaseModel):
    voice_model_id: str
    total_synthesis_requests: int
    successful_syntheses: int
    failed_syntheses: int
    average_processing_time_ms: float
    total_audio_generated_minutes: float
    most_common_emotions: List[Dict[str, Any]]
    quality_trend: List[Dict[str, Any]]
    usage_by_day: List[Dict[str, Any]]
    cost_analysis: Dict[str, float]
    performance_metrics: Dict[str, float]

# Sample Voice Models
SAMPLE_VOICE_MODELS = [
    VoiceModel(
        name="Emma Professional",
        description="Professional female voice perfect for customer service and sales calls",
        original_speaker="Emma Thompson",
        gender=VoiceGender.FEMALE,
        age=VoiceAge.ADULT,
        accent=VoiceAccent.AMERICAN,
        primary_emotion=VoiceEmotion.PROFESSIONAL,
        quality=VoiceQuality.PROFESSIONAL,
        style=VoiceStyle(
            speaking_rate=1.1,
            pitch=2.0,
            emphasis=1.2,
            breath_sounds=True,
            pronunciation_style="formal"
        ),
        metrics=VoiceMetrics(
            clarity_score=9.2,
            naturalness_score=8.8,
            emotion_accuracy=92.5,
            pronunciation_accuracy=96.8,
            consistency_score=9.0,
            background_noise_level=2.1,
            signal_to_noise_ratio=87.3,
            dynamic_range=78.5
        ),
        training_status=TrainingStatus.COMPLETED,
        created_by="voicelab@vocelio.com",
        trained_at=datetime.now() - timedelta(days=5),
        training_duration_minutes=240,
        training_samples_count=450,
        usage_count=1247,
        average_rating=4.8,
        file_size_mb=125.7,
        supported_languages=["en-US", "en-GB"],
        tags=["professional", "customer-service", "female", "clear"],
        is_public=True,
        cost_per_minute=0.25
    ),
    VoiceModel(
        name="Marcus Confident",
        description="Confident male voice ideal for sales and leadership calls",
        original_speaker="Marcus Johnson",
        gender=VoiceGender.MALE,
        age=VoiceAge.ADULT,
        accent=VoiceAccent.AMERICAN,
        primary_emotion=VoiceEmotion.CONFIDENT,
        quality=VoiceQuality.EXCELLENT,
        style=VoiceStyle(
            speaking_rate=1.0,
            pitch=-1.5,
            emphasis=1.4,
            breath_sounds=True,
            pronunciation_style="standard"
        ),
        metrics=VoiceMetrics(
            clarity_score=9.0,
            naturalness_score=9.1,
            emotion_accuracy=89.2,
            pronunciation_accuracy=94.5,
            consistency_score=8.8,
            background_noise_level=1.8,
            signal_to_noise_ratio=89.1,
            dynamic_range=82.3
        ),
        training_status=TrainingStatus.COMPLETED,
        created_by="voicelab@voicelio.com",
        trained_at=datetime.now() - timedelta(days=3),
        training_duration_minutes=180,
        training_samples_count=320,
        usage_count=892,
        average_rating=4.6,
        file_size_mb=98.4,
        supported_languages=["en-US"],
        tags=["confident", "sales", "male", "authoritative"],
        is_public=True,
        cost_per_minute=0.22
    ),
    VoiceModel(
        name="Sarah Empathetic",
        description="Warm, empathetic female voice perfect for support and care calls",
        original_speaker="Sarah Williams",
        gender=VoiceGender.FEMALE,
        age=VoiceAge.YOUNG_ADULT,
        accent=VoiceAccent.BRITISH,
        primary_emotion=VoiceEmotion.EMPATHETIC,
        quality=VoiceQuality.EXCELLENT,
        style=VoiceStyle(
            speaking_rate=0.95,
            pitch=1.0,
            emphasis=1.1,
            pause_length=1.2,
            breath_sounds=True,
            pronunciation_style="standard"
        ),
        metrics=VoiceMetrics(
            clarity_score=8.9,
            naturalness_score=9.3,
            emotion_accuracy=94.1,
            pronunciation_accuracy=95.2,
            consistency_score=9.1,
            background_noise_level=1.5,
            signal_to_noise_ratio=91.2,
            dynamic_range=75.8
        ),
        training_status=TrainingStatus.COMPLETED,
        created_by="voicelab@voicelio.com",
        trained_at=datetime.now() - timedelta(days=7),
        training_duration_minutes=300,
        training_samples_count=520,
        usage_count=654,
        average_rating=4.9,
        file_size_mb=142.3,
        supported_languages=["en-US", "en-GB", "en-AU"],
        tags=["empathetic", "support", "female", "warm", "british"],
        is_public=True,
        cost_per_minute=0.28
    )
]

# Global storage
voice_models: List[VoiceModel] = []
training_samples: List[TrainingSample] = []
clone_requests: List[VoiceCloneRequest] = []
synthesis_requests: List[SynthesisRequest] = []
optimizations: List[VoiceOptimization] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global voice_models
    
    voice_models.extend(SAMPLE_VOICE_MODELS)
    
    logger.info("Sample voice lab data initialized successfully")

async def analyze_voice_quality(audio_data: bytes) -> VoiceMetrics:
    """Analyze voice quality from audio data"""
    # Mock voice analysis - in production, this would use AI/ML models
    await asyncio.sleep(1)  # Simulate processing time
    
    return VoiceMetrics(
        clarity_score=8.5 + (hash(audio_data) % 15) / 10,
        naturalness_score=8.0 + (hash(audio_data) % 20) / 10,
        emotion_accuracy=85.0 + (hash(audio_data) % 15),
        pronunciation_accuracy=90.0 + (hash(audio_data) % 10),
        consistency_score=8.0 + (hash(audio_data) % 20) / 10,
        background_noise_level=1.0 + (hash(audio_data) % 5),
        signal_to_noise_ratio=80.0 + (hash(audio_data) % 20),
        frequency_response={"low": 0.8, "mid": 1.0, "high": 0.9},
        dynamic_range=70.0 + (hash(audio_data) % 20)
    )

async def clone_voice_model(request: VoiceCloneRequest) -> VoiceModel:
    """Process voice cloning request"""
    logger.info(f"Starting voice cloning for: {request.name}")
    
    # Update status to processing
    request.status = TrainingStatus.PROCESSING
    request.started_at = datetime.now()
    request.estimated_completion = datetime.now() + timedelta(hours=2)
    
    # Simulate training process
    for progress in [10, 25, 50, 75, 90, 100]:
        request.progress_percentage = progress
        await asyncio.sleep(0.5)  # Simulate processing time
        
        if progress == 50:
            request.status = TrainingStatus.TRAINING
        elif progress == 90:
            request.status = TrainingStatus.OPTIMIZING
    
    # Create the new voice model
    new_model = VoiceModel(
        name=request.name,
        description=request.description,
        original_speaker=request.original_speaker,
        gender=VoiceGender.FEMALE,  # Mock - would be detected from samples
        age=VoiceAge.ADULT,
        accent=VoiceAccent.AMERICAN,
        primary_emotion=VoiceEmotion.NEUTRAL,
        quality=request.target_quality,
        style=request.custom_style or VoiceStyle(),
        training_status=TrainingStatus.COMPLETED,
        created_by=request.requested_by,
        trained_at=datetime.now(),
        training_duration_minutes=120,
        training_samples_count=len(request.training_samples),
        file_size_mb=85.0 + len(request.training_samples) * 2.5
    )
    
    # Mock voice quality analysis
    new_model.metrics = VoiceMetrics(
        clarity_score=8.0 + (hash(request.name) % 20) / 10,
        naturalness_score=7.5 + (hash(request.name) % 25) / 10,
        emotion_accuracy=80.0 + (hash(request.name) % 20),
        pronunciation_accuracy=85.0 + (hash(request.name) % 15),
        consistency_score=7.5 + (hash(request.name) % 25) / 10,
        background_noise_level=2.0 + (hash(request.name) % 3),
        signal_to_noise_ratio=75.0 + (hash(request.name) % 25),
        dynamic_range=65.0 + (hash(request.name) % 30)
    )
    
    voice_models.append(new_model)
    request.status = TrainingStatus.COMPLETED
    request.completed_at = datetime.now()
    request.result_model_id = new_model.id
    
    logger.info(f"Voice cloning completed for: {request.name}")
    return new_model

async def synthesize_speech(request: SynthesisRequest) -> str:
    """Synthesize speech from text using voice model"""
    voice_model = next((v for v in voice_models if v.id == request.voice_model_id), None)
    if not voice_model:
        raise ValueError("Voice model not found")
    
    logger.info(f"Synthesizing speech with voice: {voice_model.name}")
    
    # Update status
    request.status = "processing"
    start_time = datetime.now()
    
    # Simulate synthesis process
    text_length = len(request.text_content)
    estimated_duration = text_length / 150 * 60  # ~150 words per minute
    
    await asyncio.sleep(min(2.0, estimated_duration / 10))  # Simulate processing
    
    # Mock output file
    output_filename = f"synthesis_{request.id}.{request.output_format}"
    output_path = f"/voice_lab/outputs/{output_filename}"
    
    processing_time = (datetime.now() - start_time).total_seconds() * 1000
    
    # Update request with results
    request.status = "completed"
    request.processed_at = datetime.now()
    request.output_file_path = output_path
    request.duration_seconds = estimated_duration
    request.file_size_bytes = int(estimated_duration * 32000)  # Mock file size
    request.processing_time_ms = processing_time
    request.cost = estimated_duration / 60 * voice_model.cost_per_minute
    
    # Update voice model usage
    voice_model.usage_count += 1
    
    logger.info(f"Speech synthesis completed: {output_filename}")
    return output_path

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    yield
    
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="Voice Lab Service",
    description="Advanced voice cloning, synthesis, custom voice training, and voice quality optimization for Vocelio AI Call Center",
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
        "service": "voice-lab",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Voice Model Management Endpoints
@app.get("/voices", response_model=List[VoiceModel])
async def get_voice_models(
    gender: Optional[VoiceGender] = None,
    age: Optional[VoiceAge] = None,
    accent: Optional[VoiceAccent] = None,
    emotion: Optional[VoiceEmotion] = None,
    quality: Optional[VoiceQuality] = None,
    is_public: Optional[bool] = None,
    search: Optional[str] = None
):
    """Get all voice models with optional filtering"""
    filtered_voices = voice_models
    
    if gender:
        filtered_voices = [v for v in filtered_voices if v.gender == gender]
    
    if age:
        filtered_voices = [v for v in filtered_voices if v.age == age]
    
    if accent:
        filtered_voices = [v for v in filtered_voices if v.accent == accent]
    
    if emotion:
        filtered_voices = [v for v in filtered_voices if v.primary_emotion == emotion]
    
    if quality:
        filtered_voices = [v for v in filtered_voices if v.quality == quality]
    
    if is_public is not None:
        filtered_voices = [v for v in filtered_voices if v.is_public == is_public]
    
    if search:
        search_lower = search.lower()
        filtered_voices = [
            v for v in filtered_voices
            if search_lower in v.name.lower() or search_lower in v.description.lower()
        ]
    
    return filtered_voices

@app.get("/voices/{voice_id}", response_model=VoiceModel)
async def get_voice_model(voice_id: str):
    """Get a specific voice model by ID"""
    voice = next((v for v in voice_models if v.id == voice_id), None)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice model not found")
    return voice

@app.post("/voices", response_model=VoiceModel)
async def create_voice_model(voice_data: VoiceModel):
    """Create a new voice model"""
    voice_models.append(voice_data)
    logger.info(f"Created new voice model: {voice_data.name}")
    return voice_data

@app.put("/voices/{voice_id}", response_model=VoiceModel)
async def update_voice_model(voice_id: str, voice_data: VoiceModel):
    """Update an existing voice model"""
    voice = next((v for v in voice_models if v.id == voice_id), None)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice model not found")
    
    # Update fields
    for field, value in voice_data.dict(exclude_unset=True).items():
        if field != "id":
            setattr(voice, field, value)
    
    voice.updated_at = datetime.now()
    logger.info(f"Updated voice model: {voice.name}")
    return voice

@app.delete("/voices/{voice_id}")
async def delete_voice_model(voice_id: str):
    """Delete a voice model"""
    global voice_models
    voice = next((v for v in voice_models if v.id == voice_id), None)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice model not found")
    
    voice_models = [v for v in voice_models if v.id != voice_id]
    logger.info(f"Deleted voice model: {voice.name}")
    return {"message": "Voice model deleted successfully"}

# Voice Cloning Endpoints
@app.post("/clone", response_model=VoiceCloneRequest)
async def create_clone_request(
    name: str = Form(...),
    description: str = Form(...),
    original_speaker: str = Form(...),
    target_quality: VoiceQuality = Form(...),
    requested_by: str = Form(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    audio_files: List[UploadFile] = File(...)
):
    """Create a voice cloning request with audio samples"""
    
    if len(audio_files) < 3:
        raise HTTPException(status_code=400, detail="At least 3 audio samples are required for voice cloning")
    
    # Create training samples from uploaded files
    sample_ids = []
    for audio_file in audio_files:
        if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
            raise HTTPException(status_code=400, detail=f"File {audio_file.filename} is not an audio file")
        
        # Read audio data
        audio_data = await audio_file.read()
        
        # Create training sample
        sample = TrainingSample(
            voice_model_id="pending",  # Will be updated when clone is processed
            text_content=f"Sample text for {audio_file.filename}",
            audio_file_path=f"/voice_lab/samples/{audio_file.filename}",
            duration_seconds=len(audio_data) / 44100,  # Mock duration
            quality_score=8.0 + (hash(audio_data) % 20) / 10,
            emotion_tags=[VoiceEmotion.NEUTRAL],
            phoneme_coverage=75.0 + (hash(audio_data) % 25)
        )
        
        training_samples.append(sample)
        sample_ids.append(sample.id)
    
    # Create clone request
    clone_request = VoiceCloneRequest(
        name=name,
        description=description,
        original_speaker=original_speaker,
        target_quality=target_quality,
        training_samples=sample_ids,
        requested_by=requested_by,
        status=TrainingStatus.PENDING
    )
    
    clone_requests.append(clone_request)
    
    # Start cloning process in background
    background_tasks.add_task(clone_voice_model, clone_request)
    
    logger.info(f"Voice cloning request created: {name}")
    return clone_request

@app.get("/clone/{request_id}", response_model=VoiceCloneRequest)
async def get_clone_request(request_id: str):
    """Get status of a voice cloning request"""
    request = next((r for r in clone_requests if r.id == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Clone request not found")
    return request

@app.get("/clone", response_model=List[VoiceCloneRequest])
async def get_clone_requests(requested_by: Optional[str] = None, status: Optional[TrainingStatus] = None):
    """Get all voice cloning requests with optional filtering"""
    filtered_requests = clone_requests
    
    if requested_by:
        filtered_requests = [r for r in filtered_requests if r.requested_by == requested_by]
    
    if status:
        filtered_requests = [r for r in filtered_requests if r.status == status]
    
    return filtered_requests

# Speech Synthesis Endpoints
@app.post("/synthesize", response_model=SynthesisRequest)
async def create_synthesis_request(
    voice_model_id: str,
    text_content: str,
    emotion: VoiceEmotion = VoiceEmotion.NEUTRAL,
    output_format: str = "mp3",
    requested_by: str = "api_user",
    style_overrides: Optional[VoiceStyle] = None,
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """Create a speech synthesis request"""
    
    # Validate voice model exists
    voice_model = next((v for v in voice_models if v.id == voice_model_id), None)
    if not voice_model:
        raise HTTPException(status_code=404, detail="Voice model not found")
    
    if voice_model.training_status != TrainingStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Voice model is not ready for synthesis")
    
    # Create synthesis request
    synthesis_request = SynthesisRequest(
        voice_model_id=voice_model_id,
        text_content=text_content,
        emotion=emotion,
        style_overrides=style_overrides,
        output_format=output_format,
        requested_by=requested_by
    )
    
    synthesis_requests.append(synthesis_request)
    
    # Start synthesis in background
    background_tasks.add_task(synthesize_speech, synthesis_request)
    
    logger.info(f"Speech synthesis request created for voice: {voice_model.name}")
    return synthesis_request

@app.get("/synthesize/{request_id}", response_model=SynthesisRequest)
async def get_synthesis_request(request_id: str):
    """Get status of a speech synthesis request"""
    request = next((r for r in synthesis_requests if r.id == request_id), None)
    if not request:
        raise HTTPException(status_code=404, detail="Synthesis request not found")
    return request

@app.get("/synthesize", response_model=List[SynthesisRequest])
async def get_synthesis_requests(
    voice_model_id: Optional[str] = None,
    requested_by: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50
):
    """Get speech synthesis requests with optional filtering"""
    filtered_requests = synthesis_requests
    
    if voice_model_id:
        filtered_requests = [r for r in filtered_requests if r.voice_model_id == voice_model_id]
    
    if requested_by:
        filtered_requests = [r for r in filtered_requests if r.requested_by == requested_by]
    
    if status:
        filtered_requests = [r for r in filtered_requests if r.status == status]
    
    # Sort by creation time, most recent first
    filtered_requests.sort(key=lambda x: x.created_at, reverse=True)
    
    return filtered_requests[:limit]

# Voice Quality Analysis Endpoints
@app.post("/analyze")
async def analyze_voice_sample(audio_file: UploadFile = File(...)):
    """Analyze voice quality from an audio sample"""
    
    if not audio_file.content_type or not audio_file.content_type.startswith('audio/'):
        raise HTTPException(status_code=400, detail="File must be an audio file")
    
    # Read audio data
    audio_data = await audio_file.read()
    
    # Analyze voice quality
    metrics = await analyze_voice_quality(audio_data)
    
    return {
        "filename": audio_file.filename,
        "file_size_bytes": len(audio_data),
        "analysis_timestamp": datetime.now().isoformat(),
        "metrics": metrics.dict(),
        "overall_score": round((metrics.clarity_score + metrics.naturalness_score) / 2, 1),
        "recommendations": [
            "Consider reducing background noise" if metrics.background_noise_level > 5 else "Good audio quality",
            "Excellent clarity" if metrics.clarity_score > 8 else "Consider improving recording environment",
            "Natural sounding voice" if metrics.naturalness_score > 8 else "Voice may benefit from training"
        ]
    }

# Voice Optimization Endpoints
@app.post("/voices/{voice_id}/optimize")
async def optimize_voice_model(
    voice_id: str,
    optimization_type: str,
    parameters: Dict[str, Any],
    applied_by: str
):
    """Apply optimization to a voice model"""
    
    voice_model = next((v for v in voice_models if v.id == voice_id), None)
    if not voice_model:
        raise HTTPException(status_code=404, detail="Voice model not found")
    
    # Store before metrics
    before_metrics = voice_model.metrics
    
    # Apply optimization (mock implementation)
    if optimization_type == "clarity":
        if voice_model.metrics:
            voice_model.metrics.clarity_score = min(10.0, voice_model.metrics.clarity_score + 0.5)
    elif optimization_type == "naturalness":
        if voice_model.metrics:
            voice_model.metrics.naturalness_score = min(10.0, voice_model.metrics.naturalness_score + 0.3)
    elif optimization_type == "emotion":
        if voice_model.metrics:
            voice_model.metrics.emotion_accuracy = min(100.0, voice_model.metrics.emotion_accuracy + 2.0)
    
    # Create optimization record
    optimization = VoiceOptimization(
        voice_model_id=voice_id,
        optimization_type=optimization_type,
        parameters=parameters,
        before_metrics=before_metrics,
        after_metrics=voice_model.metrics,
        improvement_score=1.5,  # Mock improvement
        applied_by=applied_by
    )
    
    optimizations.append(optimization)
    voice_model.updated_at = datetime.now()
    
    logger.info(f"Voice optimization applied: {optimization_type} for {voice_model.name}")
    return optimization

@app.get("/voices/{voice_id}/optimizations", response_model=List[VoiceOptimization])
async def get_voice_optimizations(voice_id: str):
    """Get optimization history for a voice model"""
    voice_optimizations = [o for o in optimizations if o.voice_model_id == voice_id]
    voice_optimizations.sort(key=lambda x: x.applied_at, reverse=True)
    return voice_optimizations

# Analytics Endpoints
@app.get("/voices/{voice_id}/analytics", response_model=VoiceAnalytics)
async def get_voice_analytics(voice_id: str):
    """Get analytics for a specific voice model"""
    voice_model = next((v for v in voice_models if v.id == voice_id), None)
    if not voice_model:
        raise HTTPException(status_code=404, detail="Voice model not found")
    
    voice_syntheses = [s for s in synthesis_requests if s.voice_model_id == voice_id]
    
    total_requests = len(voice_syntheses)
    successful_requests = len([s for s in voice_syntheses if s.status == "completed"])
    failed_requests = len([s for s in voice_syntheses if s.status == "failed"])
    
    avg_processing_time = 0
    total_audio_minutes = 0
    
    if voice_syntheses:
        processing_times = [s.processing_time_ms for s in voice_syntheses if s.processing_time_ms]
        avg_processing_time = sum(processing_times) / len(processing_times) if processing_times else 0
        
        durations = [s.duration_seconds for s in voice_syntheses if s.duration_seconds]
        total_audio_minutes = sum(durations) / 60 if durations else 0
    
    # Mock emotion distribution
    emotion_counts = {}
    for synthesis in voice_syntheses:
        emotion = synthesis.emotion.value
        emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
    
    most_common_emotions = [
        {"emotion": emotion, "count": count, "percentage": round(count / total_requests * 100, 1)}
        for emotion, count in emotion_counts.items()
    ]
    most_common_emotions.sort(key=lambda x: x["count"], reverse=True)
    
    return VoiceAnalytics(
        voice_model_id=voice_id,
        total_synthesis_requests=total_requests,
        successful_syntheses=successful_requests,
        failed_syntheses=failed_requests,
        average_processing_time_ms=avg_processing_time,
        total_audio_generated_minutes=total_audio_minutes,
        most_common_emotions=most_common_emotions[:5],
        quality_trend=[
            {"date": "2025-08-01", "score": 8.2},
            {"date": "2025-08-02", "score": 8.4},
            {"date": "2025-08-03", "score": 8.6},
            {"date": "2025-08-04", "score": 8.5},
            {"date": "2025-08-05", "score": 8.7}
        ],
        usage_by_day=[
            {"date": "2025-08-01", "requests": 45},
            {"date": "2025-08-02", "requests": 52},
            {"date": "2025-08-03", "requests": 38},
            {"date": "2025-08-04", "requests": 61},
            {"date": "2025-08-05", "requests": 47}
        ],
        cost_analysis={
            "total_cost": total_audio_minutes * voice_model.cost_per_minute,
            "cost_per_request": (total_audio_minutes * voice_model.cost_per_minute) / total_requests if total_requests > 0 else 0,
            "monthly_projection": total_audio_minutes * voice_model.cost_per_minute * 30
        },
        performance_metrics={
            "success_rate": round(successful_requests / total_requests * 100, 1) if total_requests > 0 else 0,
            "average_quality_score": round((voice_model.metrics.clarity_score + voice_model.metrics.naturalness_score) / 2, 1) if voice_model.metrics else 0,
            "user_satisfaction": voice_model.average_rating
        }
    )

@app.get("/analytics/overview")
async def get_voice_lab_overview():
    """Get overall voice lab analytics and metrics"""
    total_voices = len(voice_models)
    public_voices = len([v for v in voice_models if v.is_public])
    completed_voices = len([v for v in voice_models if v.training_status == TrainingStatus.COMPLETED])
    
    total_syntheses = len(synthesis_requests)
    successful_syntheses = len([s for s in synthesis_requests if s.status == "completed"])
    
    # Voice quality distribution
    quality_distribution = {}
    for quality in VoiceQuality:
        count = len([v for v in voice_models if v.quality == quality])
        if count > 0:
            quality_distribution[quality.value] = count
    
    # Gender distribution
    gender_distribution = {}
    for gender in VoiceGender:
        count = len([v for v in voice_models if v.gender == gender])
        if count > 0:
            gender_distribution[gender.value] = count
    
    # Recent activity
    recent_clones = len([c for c in clone_requests if c.created_at > datetime.now() - timedelta(hours=24)])
    recent_syntheses = len([s for s in synthesis_requests if s.created_at > datetime.now() - timedelta(hours=24)])
    
    return {
        "total_voice_models": total_voices,
        "public_voice_models": public_voices,
        "private_voice_models": total_voices - public_voices,
        "completed_voice_models": completed_voices,
        "voice_model_success_rate": round(completed_voices / total_voices * 100, 1) if total_voices > 0 else 0,
        "total_synthesis_requests": total_syntheses,
        "successful_syntheses": successful_syntheses,
        "synthesis_success_rate": round(successful_syntheses / total_syntheses * 100, 1) if total_syntheses > 0 else 0,
        "quality_distribution": quality_distribution,
        "gender_distribution": gender_distribution,
        "activity_24h": {
            "new_voice_clones": recent_clones,
            "synthesis_requests": recent_syntheses,
            "voice_optimizations": len([o for o in optimizations if o.applied_at > datetime.now() - timedelta(hours=24)])
        },
        "performance_metrics": {
            "average_clone_time_minutes": 150,
            "average_synthesis_time_ms": 2450,
            "average_voice_quality_score": 8.6,
            "storage_used_gb": sum(v.file_size_mb for v in voice_models if v.file_size_mb) / 1024
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8015)
