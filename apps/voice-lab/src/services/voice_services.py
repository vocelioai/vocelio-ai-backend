"""
Voice Lab - Core Services
Business logic for voice management, generation, and processing
"""

from typing import List, Optional, Dict, Any
import asyncio
import uuid
from datetime import datetime, timedelta
import os
from pathlib import Path
import json

from shared.database.client import get_database
from shared.utils.service_client import ServiceClient
from schemas.voice import VoiceResponse, VoiceCreate, VoiceUpdate, VoiceFilter, VoiceComparison
from schemas.generation import GenerationRequest, GenerationResponse
from models.voice import Voice
from models.generation import Generation


class VoiceService:
    """Core voice management service"""
    
    def __init__(self):
        self.db = get_database()
        self.service_client = ServiceClient()
        self.static_path = Path("static")
        
    async def get_voices(self, filter_params: VoiceFilter, user_id: str) -> List[VoiceResponse]:
        """Get filtered list of voices"""
        query = self.db.table("voices").select("*")
        
        # Apply filters
        if filter_params.language:
            query = query.eq("language", filter_params.language)
        if filter_params.gender:
            query = query.eq("gender", filter_params.gender)
        if filter_params.category:
            query = query.eq("category", filter_params.category)
        if filter_params.use_case:
            query = query.eq("use_case", filter_params.use_case)
        if filter_params.quality_min:
            query = query.gte("quality_score", filter_params.quality_min)
        if filter_params.search:
            query = query.or_(
                f"name.ilike.%{filter_params.search}%,"
                f"description.ilike.%{filter_params.search}%"
            )
        
        # Apply pagination
        query = query.range(filter_params.offset, filter_params.offset + filter_params.limit - 1)
        
        result = await query.execute()
        
        # Convert to response models
        voices = []
        for voice_data in result.data:
            # Get performance metrics
            performance = await self._get_voice_performance(voice_data["voice_id"], user_id)
            
            voice = VoiceResponse(
                voice_id=voice_data["voice_id"],
                name=voice_data["name"],
                gender=voice_data["gender"],
                age=voice_data["age"],
                accent=voice_data["accent"],
                language=voice_data["language"],
                description=voice_data["description"],
                use_case=voice_data["use_case"],
                category=voice_data["category"],
                quality_score=voice_data["quality_score"],
                performance=performance,
                settings=voice_data["settings"],
                preview_url=f"/static/previews/{voice_data['voice_id']}.mp3",
                cost_per_char=voice_data["cost_per_char"],
                available_for_tiers=voice_data["available_for_tiers"]
            )
            voices.append(voice)
        
        return voices
    
    async def get_voice(self, voice_id: str, user_id: str) -> Optional[VoiceResponse]:
        """Get specific voice details"""
        result = await self.db.table("voices").select("*").eq("voice_id", voice_id).execute()
        
        if not result.data:
            return None
        
        voice_data = result.data[0]
        performance = await self._get_voice_performance(voice_id, user_id)
        
        return VoiceResponse(
            voice_id=voice_data["voice_id"],
            name=voice_data["name"],
            gender=voice_data["gender"],
            age=voice_data["age"],
            accent=voice_data["accent"],
            language=voice_data["language"],
            description=voice_data["description"],
            use_case=voice_data["use_case"],
            category=voice_data["category"],
            quality_score=voice_data["quality_score"],
            performance=performance,
            settings=voice_data["settings"],
            preview_url=f"/static/previews/{voice_data['voice_id']}.mp3",
            cost_per_char=voice_data["cost_per_char"],
            available_for_tiers=voice_data["available_for_tiers"]
        )
    
    async def create_voice(self, voice_data: VoiceCreate, user_id: str) -> VoiceResponse:
        """Create new custom voice"""
        voice_id = str(uuid.uuid4())
        
        # Insert voice record
        result = await self.db.table("voices").insert({
            "voice_id": voice_id,
            "name": voice_data.name,
            "description": voice_data.description,
            "language": voice_data.language,
            "gender": voice_data.gender,
            "age": voice_data.age,
            "accent": voice_data.accent,
            "use_case": voice_data.use_case,
            "category": "custom",
            "quality_score": 85.0,  # Default for new voices
            "settings": voice_data.settings or {"stability": 0.7, "similarity_boost": 0.8, "style": 0.2},
            "cost_per_char": 0.00025,  # Higher cost for custom voices
            "available_for_tiers": ["pro", "enterprise"],
            "created_by": user_id,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        return await self.get_voice(voice_id, user_id)
    
    async def compare_voices(self, voice_ids: List[str], sample_text: str, user_id: str) -> VoiceComparison:
        """Compare multiple voices"""
        voices = []
        
        for voice_id in voice_ids:
            voice = await self.get_voice(voice_id, user_id)
            if voice:
                # Generate comparison audio
                generation_result = await self.generate_speech(
                    text=sample_text,
                    voice_id=voice_id,
                    user_id=user_id
                )
                
                # Calculate comparison score based on quality metrics
                comparison_score = await self._calculate_comparison_score(voice_id, sample_text)
                
                comparison_voice = {
                    **voice.dict(),
                    "comparison_score": comparison_score,
                    "generation_time": generation_result.generation_time,
                    "audio_url": generation_result.audio_url
                }
                voices.append(comparison_voice)
        
        # Sort by comparison score
        voices.sort(key=lambda x: x["comparison_score"], reverse=True)
        
        return VoiceComparison(
            sample_text=sample_text,
            voices=voices
        )
    
    async def generate_speech(self, text: str, voice_id: str, user_id: str, settings: Optional[Dict] = None) -> GenerationResponse:
        """Generate speech from text"""
        generation_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # Get voice details
            voice = await self.get_voice(voice_id, user_id)
            if not voice:
                raise ValueError("Voice not found")
            
            # Use voice settings or provided settings
            voice_settings = settings or voice.settings
            
            # Call AI service for speech generation
            ai_response = await self.service_client.post(
                "ai-brain/generation/text-to-speech",
                data={
                    "text": text,
                    "voice_id": voice_id,
                    "settings": voice_settings
                }
            )
            
            # Save generation record
            generation_time = (datetime.now() - start_time).total_seconds()
            audio_file_path = f"static/generations/{generation_id}.mp3"
            
            await self.db.table("generations").insert({
                "generation_id": generation_id,
                "user_id": user_id,
                "voice_id": voice_id,
                "text": text,
                "settings": voice_settings,
                "audio_file_path": audio_file_path,
                "generation_time": generation_time,
                "character_count": len(text),
                "cost": len(text) * voice.cost_per_char,
                "created_at": datetime.now().isoformat()
            }).execute()
            
            # Update usage statistics
            await self._update_voice_usage(voice_id, user_id, len(text))
            
            return GenerationResponse(
                generation_id=generation_id,
                voice_id=voice_id,
                text=text,
                audio_url=f"/voice-lab/generation/download/{generation_id}",
                generation_time=generation_time,
                character_count=len(text),
                cost=len(text) * voice.cost_per_char,
                status="completed"
            )
            
        except Exception as e:
            # Log error and return failed response
            await self.db.table("generations").insert({
                "generation_id": generation_id,
                "user_id": user_id,
                "voice_id": voice_id,
                "text": text,
                "status": "failed",
                "error_message": str(e),
                "created_at": datetime.now().isoformat()
            }).execute()
            
            raise e
    
    async def _get_voice_performance(self, voice_id: str, user_id: str) -> Dict:
        """Get voice performance metrics"""
        # Get usage statistics
        usage_result = await self.db.table("generations").select("*").eq("voice_id", voice_id).execute()
        
        usage_count = len(usage_result.data)
        
        # Calculate success rate (non-failed generations)
        successful = [g for g in usage_result.data if g.get("status") != "failed"]
        success_rate = (len(successful) / usage_count * 100) if usage_count > 0 else 0
        
        # Get average sentiment from feedback
        feedback_result = await self.db.table("voice_feedback").select("sentiment").eq("voice_id", voice_id).execute()
        avg_sentiment = sum(f["sentiment"] for f in feedback_result.data) / len(feedback_result.data) if feedback_result.data else 0.75
        
        return {
            "usage_count": usage_count,
            "success_rate": round(success_rate, 1),
            "avg_sentiment": round(avg_sentiment, 2)
        }
    
    async def _calculate_comparison_score(self, voice_id: str, text: str) -> float:
        """Calculate comparison score for voice"""
        # Get voice quality score
        voice = await self.get_voice(voice_id, "system")
        base_score = voice.quality_score if voice else 80.0
        
        # Adjust based on text characteristics
        text_complexity = len(text.split()) / 10  # Simple complexity measure
        score_adjustment = min(text_complexity, 10)  # Cap at 10 points
        
        return min(base_score + score_adjustment, 100.0)
    
    async def _update_voice_usage(self, voice_id: str, user_id: str, character_count: int):
        """Update voice usage statistics"""
        await self.db.table("voice_usage").upsert({
            "voice_id": voice_id,
            "user_id": user_id,
            "total_characters": character_count,
            "last_used": datetime.now().isoformat()
        }).execute()


class CloningService:
    """Voice cloning service"""
    
    def __init__(self):
        self.db = get_database()
        self.service_client = ServiceClient()
    
    async def start_cloning(self, audio_file, request, user_id: str) -> str:
        """Start voice cloning process"""
        clone_id = str(uuid.uuid4())
        
        # Save audio file
        audio_path = f"static/cloning/{clone_id}_input.wav"
        os.makedirs(os.path.dirname(audio_path), exist_ok=True)
        
        with open(audio_path, "wb") as f:
            content = await audio_file.read()
            f.write(content)
        
        # Insert cloning job record
        await self.db.table("voice_cloning_jobs").insert({
            "clone_id": clone_id,
            "user_id": user_id,
            "voice_name": request.voice_name,
            "description": request.description,
            "language": request.language,
            "gender": request.gender,
            "use_case": request.use_case,
            "audio_file_path": audio_path,
            "status": "processing",
            "progress": 0,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        return clone_id
    
    async def process_voice_cloning(self, clone_id: str, user_id: str):
        """Process voice cloning in background"""
        try:
            # Update status to processing
            await self.db.table("voice_cloning_jobs").update({
                "status": "processing",
                "progress": 10,
                "updated_at": datetime.now().isoformat()
            }).eq("clone_id", clone_id).execute()
            
            # Simulate AI processing steps
            processing_steps = [
                ("Audio validation", 20),
                ("Voice analysis", 40),
                ("Model training", 60),
                ("Quality testing", 80),
                ("Voice synthesis", 90),
                ("Final validation", 100)
            ]
            
            for step_name, progress in processing_steps:
                await asyncio.sleep(30)  # Simulate processing time
                await self.db.table("voice_cloning_jobs").update({
                    "progress": progress,
                    "current_step": step_name,
                    "updated_at": datetime.now().isoformat()
                }).eq("clone_id", clone_id).execute()
            
            # Get cloning job details
            job_result = await self.db.table("voice_cloning_jobs").select("*").eq("clone_id", clone_id).execute()
            job = job_result.data[0]
            
            # Create voice entry
            voice_id = f"cloned_{clone_id}"
            await self.db.table("voices").insert({
                "voice_id": voice_id,
                "name": job["voice_name"],
                "description": job["description"],
                "language": job["language"],
                "gender": job["gender"],
                "age": "adult",
                "accent": "custom",
                "use_case": job["use_case"],
                "category": "cloned",
                "quality_score": 87.0,  # Simulated quality score
                "settings": {"stability": 0.75, "similarity_boost": 0.9, "style": 0.25},
                "cost_per_char": 0.00035,  # Higher cost for cloned voices
                "available_for_tiers": ["enterprise"],
                "created_by": user_id,
                "clone_id": clone_id,
                "created_at": datetime.now().isoformat()
            }).execute()
            
            # Update job status to completed
            await self.db.table("voice_cloning_jobs").update({
                "status": "completed",
                "progress": 100,
                "voice_id": voice_id,
                "completed_at": datetime.now().isoformat()
            }).eq("clone_id", clone_id).execute()
            
        except Exception as e:
            # Update job status to failed
            await self.db.table("voice_cloning_jobs").update({
                "status": "failed",
                "error_message": str(e),
                "updated_at": datetime.now().isoformat()
            }).eq("clone_id", clone_id).execute()


class TestingService:
    """Voice testing and quality analysis service"""
    
    def __init__(self):
        self.db = get_database()
        self.service_client = ServiceClient()
    
    async def test_voice_quality(self, voice_id: str, test_phrases: List[str], metrics: List[str], user_id: str):
        """Test voice quality with comprehensive metrics"""
        test_id = str(uuid.uuid4())
        
        # Insert test record
        await self.db.table("voice_tests").insert({
            "test_id": test_id,
            "voice_id": voice_id,
            "user_id": user_id,
            "test_type": "quality",
            "test_phrases": test_phrases,
            "metrics": metrics,
            "status": "processing",
            "created_at": datetime.now().isoformat()
        }).execute()
        
        # Simulate quality testing
        await asyncio.sleep(5)  # Simulate processing time
        
        # Generate test results
        results = {
            "overall_score": 85 + (hash(voice_id) % 15),  # Deterministic but varied
            "clarity": 90 + (hash(voice_id + "clarity") % 10),
            "naturalness": 85 + (hash(voice_id + "natural") % 15),
            "consistency": 88 + (hash(voice_id + "consistent") % 12),
            "emotion_range": 80 + (hash(voice_id + "emotion") % 20),
            "recommendation": "Excellent for professional business calls",
            "tested_phrases": len(test_phrases),
            "generation_time": 2.3 + (hash(voice_id) % 20) / 10
        }
        
        # Update test record with results
        await self.db.table("voice_tests").update({
            "status": "completed",
            "results": results,
            "completed_at": datetime.now().isoformat()
        }).eq("test_id", test_id).execute()
        
        return {
            "test_id": test_id,
            "voice_id": voice_id,
            "results": results,
            "status": "completed"
        }
    
    async def start_batch_test(self, voice_ids: List[str], test_phrases: List[str], metrics: List[str], user_id: str) -> str:
        """Start batch testing of multiple voices"""
        batch_id = str(uuid.uuid4())
        
        await self.db.table("batch_tests").insert({
            "batch_id": batch_id,
            "user_id": user_id,
            "voice_ids": voice_ids,
            "test_phrases": test_phrases,
            "metrics": metrics,
            "status": "processing",
            "total_voices": len(voice_ids),
            "completed_voices": 0,
            "created_at": datetime.now().isoformat()
        }).execute()
        
        return batch_id
    
    async def process_batch_test(self, batch_id: str, user_id: str):
        """Process batch testing in background"""
        batch_result = await self.db.table("batch_tests").select("*").eq("batch_id", batch_id).execute()
        batch = batch_result.data[0]
        
        results = []
        for i, voice_id in enumerate(batch["voice_ids"]):
            # Test each voice
            test_result = await self.test_voice_quality(
                voice_id=voice_id,
                test_phrases=batch["test_phrases"],
                metrics=batch["metrics"],
                user_id=user_id
            )
            results.append(test_result)
            
            # Update progress
            await self.db.table("batch_tests").update({
                "completed_voices": i + 1,
                "progress": ((i + 1) / len(batch["voice_ids"])) * 100
            }).eq("batch_id", batch_id).execute()
        
        # Update final status
        await self.db.table("batch_tests").update({
            "status": "completed",
            "results": results,
            "completed_at": datetime.now().isoformat()
        }).eq("batch_id", batch_id).execute()


class AnalyticsService:
    """Voice analytics and reporting service"""
    
    def __init__(self):
        self.db = get_database()
        self.service_client = ServiceClient()
    
    async def get_analytics_overview(self, user_id: str, days: int = 30) -> Dict:
        """Get comprehensive analytics overview"""
        start_date = datetime.now() - timedelta(days=days)
        
        # Get generation statistics
        generations = await self.db.table("generations").select("*").eq("user_id", user_id).gte("created_at", start_date.isoformat()).execute()
        
        # Get voice usage statistics
        voice_usage = await self.db.table("voice_usage").select("*").eq("user_id", user_id).execute()
        
        # Calculate metrics
        total_generations = len(generations.data)
        total_characters = sum(g.get("character_count", 0) for g in generations.data)
        total_cost = sum(g.get("cost", 0) for g in generations.data)
        
        # Get unique voices used
        unique_voices = len(set(g["voice_id"] for g in generations.data))
        
        # Calculate average generation time
        avg_generation_time = sum(g.get("generation_time", 0) for g in generations.data) / total_generations if total_generations > 0 else 0
        
        # Get top performing voices
        voice_counts = {}
        for gen in generations.data:
            voice_id = gen["voice_id"]
            voice_counts[voice_id] = voice_counts.get(voice_id, 0) + 1
        
        top_voices = sorted(voice_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "period_days": days,
            "total_generations": total_generations,
            "total_characters": total_characters,
            "total_cost": round(total_cost, 2),
            "unique_voices_used": unique_voices,
            "avg_generation_time": round(avg_generation_time, 2),
            "top_voices": top_voices,
            "daily_usage": await self._get_daily_usage(user_id, days),
            "cost_breakdown": await self._get_cost_breakdown(user_id, days),
            "quality_trends": await self._get_quality_trends(user_id, days)
        }
    
    async def get_voice_analytics(self, voice_id: str, user_id: str, days: int) -> Dict:
        """Get detailed analytics for specific voice"""
        start_date = datetime.now() - timedelta(days=days)
        
        # Get voice generations
        generations = await self.db.table("generations").select("*").eq("voice_id", voice_id).eq("user_id", user_id).gte("created_at", start_date.isoformat()).execute()
        
        # Get voice details
        voice_result = await self.db.table("voices").select("*").eq("voice_id", voice_id).execute()
        voice = voice_result.data[0] if voice_result.data else None
        
        if not voice:
            return None
        
        # Calculate analytics
        total_usage = len(generations.data)
        total_characters = sum(g.get("character_count", 0) for g in generations.data)
        total_cost = sum(g.get("cost", 0) for g in generations.data)
        avg_generation_time = sum(g.get("generation_time", 0) for g in generations.data) / total_usage if total_usage > 0 else 0
        
        # Success rate
        successful = [g for g in generations.data if g.get("status") != "failed"]
        success_rate = (len(successful) / total_usage * 100) if total_usage > 0 else 0
        
        return {
            "voice_id": voice_id,
            "voice_name": voice["name"],
            "period_days": days,
            "total_usage": total_usage,
            "total_characters": total_characters,
            "total_cost": round(total_cost, 2),
            "avg_generation_time": round(avg_generation_time, 2),
            "success_rate": round(success_rate, 1),
            "quality_score": voice["quality_score"],
            "daily_usage": await self._get_voice_daily_usage(voice_id, user_id, days),
            "performance_metrics": await self._get_voice_performance_metrics(voice_id, user_id, days)
        }
    
    async def _get_daily_usage(self, user_id: str, days: int) -> List[Dict]:
        """Get daily usage statistics"""
        daily_usage = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            # Get generations for this date
            generations = await self.db.table("generations").select("*").eq("user_id", user_id).like("created_at", f"{date_str}%").execute()
            
            daily_usage.append({
                "date": date_str,
                "generations": len(generations.data),
                "characters": sum(g.get("character_count", 0) for g in generations.data),
                "cost": sum(g.get("cost", 0) for g in generations.data)
            })
        
        return list(reversed(daily_usage))
    
    async def _get_cost_breakdown(self, user_id: str, days: int) -> Dict:
        """Get cost breakdown by voice category"""
        start_date = datetime.now() - timedelta(days=days)
        
        generations = await self.db.table("generations").select("*").eq("user_id", user_id).gte("created_at", start_date.isoformat()).execute()
        
        cost_breakdown = {"premade": 0, "cloned": 0, "custom": 0}
        
        for gen in generations.data:
            voice_result = await self.db.table("voices").select("category").eq("voice_id", gen["voice_id"]).execute()
            if voice_result.data:
                category = voice_result.data[0]["category"]
                cost_breakdown[category] = cost_breakdown.get(category, 0) + gen.get("cost", 0)
        
        return cost_breakdown
    
    async def _get_quality_trends(self, user_id: str, days: int) -> List[Dict]:
        """Get quality trends over time"""
        # Simplified quality trends - in production would analyze actual quality metrics
        trends = []
        for i in range(0, days, 7):  # Weekly data points
            date = datetime.now() - timedelta(days=i)
            trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "avg_quality": 85 + (i % 10),  # Simulated trend
                "satisfaction": 4.2 + (i % 3) * 0.1  # Simulated satisfaction
            })
        
        return list(reversed(trends))
    
    async def _get_voice_daily_usage(self, voice_id: str, user_id: str, days: int) -> List[Dict]:
        """Get daily usage for specific voice"""
        daily_usage = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            generations = await self.db.table("generations").select("*").eq("voice_id", voice_id).eq("user_id", user_id).like("created_at", f"{date_str}%").execute()
            
            daily_usage.append({
                "date": date_str,
                "usage_count": len(generations.data),
                "characters": sum(g.get("character_count", 0) for g in generations.data)
            })
        
        return list(reversed(daily_usage))
    
    async def _get_voice_performance_metrics(self, voice_id: str, user_id: str, days: int) -> Dict:
        """Get voice performance metrics"""
        start_date = datetime.now() - timedelta(days=days)
        
        generations = await self.db.table("generations").select("*").eq("voice_id", voice_id).eq("user_id", user_id).gte("created_at", start_date.isoformat()).execute()
        
        if not generations.data:
            return {"avg_generation_time": 0, "success_rate": 0, "avg_quality": 0}
        
        successful = [g for g in generations.data if g.get("status") != "failed"]
        avg_generation_time = sum(g.get("generation_time", 0) for g in generations.data) / len(generations.data)
        success_rate = (len(successful) / len(generations.data)) * 100
        
        return {
            "avg_generation_time": round(avg_generation_time, 2),
            "success_rate": round(success_rate, 1),
            "avg_quality": 87.5,  # Would be calculated from actual quality metrics
            "total_generations": len(generations.data)
        }