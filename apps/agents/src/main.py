"""
Vocelio Agents Service
Handles AI agent management, creation, and configuration
"""

import os
import sys
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
import logging

# Add shared directory to path (root-level for Docker)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "shared")))

from shared.database.client import DatabaseClient
# Import only the basic models that exist
# from models.base import Agent, Voice, User

# Create simple Pydantic models for the agents service
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    voice_id: Optional[str] = ""
    language: Optional[str] = "en"
    personality_traits: Optional[List[str]] = []

class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    voice_id: Optional[str] = None
    language: Optional[str] = None
    personality_traits: Optional[List[str]] = None

class Agent(BaseModel):
    id: str
    name: str
    description: str = ""
    voice_id: str = ""
    language: str = "en"
    personality_traits: List[str] = []
    status: str = "inactive"
    created_at: datetime
    updated_at: datetime

class Voice(BaseModel):
    id: str
    name: str
    provider: str = "piper_tts"
    
class User(BaseModel):
    id: str
    email: str

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Vocelio Agents Service",
    description="AI Agent Management and Configuration Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database client with error handling
try:
    db = DatabaseClient()
    logger.info("Database client initialized successfully")
except ValueError as e:
    logger.warning(f"Database client initialization failed: {e}")
    logger.warning("Running in demo mode without database connectivity")
    db = None

# Dependency for authentication
async def get_current_user(user_id: str = "authenticated_user"):
    """Simple user dependency - will be enhanced with proper JWT validation"""
    return {"user_id": user_id, "role": "admin"}

@app.on_event("startup")
async def startup_event():
    """Initialize service on startup"""
    logger.info("Agents Service starting up...")
    if db:
        await db.connect()
        logger.info("Connected to database")
    else:
        logger.info("Running in demo mode without database")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Agents Service shutting down...")
    if db:
        await db.disconnect()

@app.get("/")
async def root():
    """Service info"""
    return {
        "service": "Vocelio Agents Service",
        "version": "1.0.0",
        "status": "healthy",
        "description": "AI Agent Management and Configuration"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection if available
        if db:
            await db.health_check()
            database_status = "connected"
        else:
            database_status = "demo_mode"
            
        return {
            "status": "healthy",
            "service": "agents",
            "timestamp": datetime.utcnow().isoformat(),
            "database": database_status
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail="Service unhealthy"
        )

@app.post("/agents", response_model=Agent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new AI agent"""
    try:
        logger.info(f"Creating agent: {agent_data.name}")
        
        # Create agent data
        agent_dict = agent_data.model_dump()
        agent_dict["id"] = str(uuid.uuid4())
        agent_dict["created_at"] = datetime.utcnow()
        agent_dict["updated_at"] = datetime.utcnow()
        agent_dict["user_id"] = current_user["user_id"]
        
        # Insert into database
        agent_id = await db.create_agent(agent_dict)
        
        # Fetch and return created agent
        agent = await db.get_agent(agent_id)
        if not agent:
            raise HTTPException(status_code=500, detail="Failed to create agent")
        
        logger.info(f"Agent created successfully: {agent_id}")
        return Agent(**agent)
        
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create agent: {str(e)}"
        )

@app.get("/agents", response_model=List[Agent])
async def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    organization_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """List all agents with pagination"""
    try:
        logger.info(f"Listing agents: skip={skip}, limit={limit}")
        
        agents = await db.get_agents(
            user_id=current_user["user_id"],
            organization_id=organization_id,
            offset=skip,
            limit=limit
        )
        
        return [Agent(**agent) for agent in agents]
        
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list agents: {str(e)}"
        )

@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific agent by ID"""
    try:
        logger.info(f"Getting agent: {agent_id}")
        
        agent = await db.get_agent(agent_id)
        if not agent:
            raise HTTPException(
                status_code=404,
                detail="Agent not found"
            )
        
        # Check if user has access to this agent
        if agent.get("user_id") != current_user["user_id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied"
            )
        
        return Agent(**agent)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get agent: {str(e)}"
        )

@app.put("/agents/{agent_id}", response_model=Agent)
async def update_agent(
    agent_id: str,
    agent_update: AgentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an existing agent"""
    try:
        logger.info(f"Updating agent: {agent_id}")
        
        # Check if agent exists and user has access
        existing_agent = await db.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if existing_agent.get("user_id") != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update agent
        update_data = agent_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        await db.update_agent(agent_id, update_data)
        
        # Return updated agent
        updated_agent = await db.get_agent(agent_id)
        return Agent(**updated_agent)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update agent: {str(e)}"
        )

@app.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete an agent"""
    try:
        logger.info(f"Deleting agent: {agent_id}")
        
        # Check if agent exists and user has access
        existing_agent = await db.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if existing_agent.get("user_id") != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Delete agent
        await db.delete_agent(agent_id)
        logger.info(f"Agent deleted successfully: {agent_id}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete agent: {str(e)}"
        )

@app.post("/agents/{agent_id}/train", status_code=status.HTTP_202_ACCEPTED)
async def train_agent(
    agent_id: str,
    training_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Start training process for an agent"""
    try:
        logger.info(f"Starting training for agent: {agent_id}")
        
        # Check if agent exists and user has access
        existing_agent = await db.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if existing_agent.get("user_id") != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Update agent status to training
        await db.update_agent(agent_id, {
            "status": "training",
            "updated_at": datetime.utcnow()
        })
        
        # TODO: Implement actual training logic
        # This would integrate with AI training pipeline
        
        return {
            "message": "Training started",
            "agent_id": agent_id,
            "status": "training"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting training: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start training: {str(e)}"
        )

@app.get("/agents/{agent_id}/voices", response_model=List[Voice])
async def get_agent_voices(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get available voices for an agent"""
    try:
        logger.info(f"Getting voices for agent: {agent_id}")
        
        # Check if agent exists and user has access
        existing_agent = await db.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if existing_agent.get("user_id") != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get available voices
        voices = await db.get_voices_for_agent(agent_id)
        return [Voice(**voice) for voice in voices]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get voices: {str(e)}"
        )

@app.post("/agents/{agent_id}/assign-voice/{voice_id}")
async def assign_voice_to_agent(
    agent_id: str,
    voice_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Assign a voice to an agent"""
    try:
        logger.info(f"Assigning voice {voice_id} to agent {agent_id}")
        
        # Check if agent exists and user has access
        existing_agent = await db.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if existing_agent.get("user_id") != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Assign voice
        await db.assign_voice_to_agent(agent_id, voice_id)
        
        return {
            "message": "Voice assigned successfully",
            "agent_id": agent_id,
            "voice_id": voice_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning voice: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to assign voice: {str(e)}"
        )

@app.get("/agents/{agent_id}/analytics")
async def get_agent_analytics(
    agent_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user)
):
    """Get analytics for an agent"""
    try:
        logger.info(f"Getting analytics for agent: {agent_id}")
        
        # Check if agent exists and user has access
        existing_agent = await db.get_agent(agent_id)
        if not existing_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        if existing_agent.get("user_id") != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Get analytics data
        analytics = await db.get_agent_analytics(agent_id, days)
        
        return {
            "agent_id": agent_id,
            "period_days": days,
            "analytics": analytics
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analytics: {str(e)}"
        )

# Development mode runner
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,
        reload=True,
        log_level="info"
    )
