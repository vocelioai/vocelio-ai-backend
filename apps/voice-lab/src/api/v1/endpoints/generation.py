"""
Voice Lab - Speech Generation Endpoints
Handles text-to-speech generation and audio processing
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional
import asyncio

from services.voice_service import VoiceService
from schemas.generation import (
    GenerationRequest,
    GenerationResponse,
    BatchGenerationRequest,
    BatchGenerationResponse
)
from shared.auth.dependencies import get_current_user
from shared.models.user import User

router = APIRouter()

@router.post("/generate", response_model=GenerationResponse)
async def generate_speech(
    request: GenerationRequest,
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Generate speech from text using specified voice"""
    try:
        result = await voice_service.generate_speech(
            text=request.text,
            voice_id=request.voice_id,
            settings=request.settings,
            user_id=current_user.id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.post("/generate-batch", response_model=BatchGenerationResponse)
async def generate_batch(
    request: BatchGenerationRequest,
    background_tasks: BackgroundTasks,
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Generate multiple audio files in batch"""
    try:
        # Start batch generation in background
        batch_id = await voice_service.start_batch_generation(
            requests=request.generations,
            user_id=current_user.id
        )
        
        # Add background task to process batch
        background_tasks.add_task(
            voice_service.process_batch_generation,
            batch_id,
            current_user.id
        )
        
        return BatchGenerationResponse(
            batch_id=batch_id,
            status="processing",
            total_items=len(request.generations),
            message="Batch generation started"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch generation failed: {str(e)}")

@router.get("/batch/{batch_id}/status")
async def get_batch_status(
    batch_id: str,
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get batch generation status"""
    status = await voice_service.get_batch_status(batch_id, current_user.id)
    if not status:
        raise HTTPException(status_code=404, detail="Batch not found")
    return status

@router.get("/download/{generation_id}")
async def download_audio(
    generation_id: str,
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Download generated audio file"""
    file_path = await voice_service.get_generated_audio(generation_id, current_user.id)
    if not file_path:
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=f"generated_{generation_id}.mp3"
    )

@router.post("/test-voice/{voice_id}")
async def test_voice_generation(
    voice_id: str,
    text: str = "Hello, this is a test of this voice. How does it sound for your calling campaigns?",
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Quick voice test with sample text"""
    try:
        result = await voice_service.test_voice_generation(
            voice_id=voice_id,
            text=text,
            user_id=current_user.id
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice test failed: {str(e)}")

@router.get("/usage/stats")
async def get_usage_stats(
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """Get voice generation usage statistics"""
    stats = await voice_service.get_usage_stats(current_user.id)
    return stats

@router.post("/optimize/{voice_id}")
async def optimize_voice_settings(
    voice_id: str,
    sample_texts: List[str],
    voice_service: VoiceService = Depends(),
    current_user: User = Depends(get_current_user)
):
    """AI-optimize voice settings based on sample texts"""
    try:
        optimized_settings = await voice_service.optimize_voice_settings(
            voice_id=voice_id,
            sample_texts=sample_texts,
            user_id=current_user.id
        )
        return {
            "voice_id": voice_id,
            "optimized_settings": optimized_settings,
            "message": "Voice settings optimized successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization failed: {str(e)}")

@router.get("/formats/supported")
async def get_supported_formats():
    """Get list of supported audio formats"""
    return {
        "input_formats": ["text"],
        "output_formats": ["mp3", "wav", "ogg"],
        "sample_rates": [16000, 22050, 44100, 48000],
        "bitrates": [128, 192, 256, 320],
        "channels": ["mono", "stereo"]
    }
