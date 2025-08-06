"""
Call Center Service - Vocelio Backend
Real-time call monitoring, live transcripts, and call management
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Query, WebSocket, WebSocketDisconnect
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
import random
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

class CallStatus(str, Enum):
    QUEUED = "queued"
    RINGING = "ringing"
    ANSWERED = "answered"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    TRANSFERRING = "transferring"
    COMPLETED = "completed"
    FAILED = "failed"
    BUSY = "busy"
    NO_ANSWER = "no_answer"
    VOICEMAIL = "voicemail"

class CallDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"

class CallPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class AgentStatus(str, Enum):
    AVAILABLE = "available"
    BUSY = "busy"
    ON_BREAK = "on_break"
    OFFLINE = "offline"
    IN_CALL = "in_call"

class TranscriptSpeaker(str, Enum):
    AGENT = "agent"
    CUSTOMER = "customer"
    SYSTEM = "system"

# Pydantic Models
class TranscriptSegment(BaseModel):
    id: str = None
    speaker: TranscriptSpeaker
    text: str
    timestamp: datetime
    confidence: float = 0.95
    sentiment: Optional[str] = None
    keywords: List[str] = []
    
    def __init__(self, **data):
        if data.get('id') is None:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)

class CallMetrics(BaseModel):
    call_id: str
    duration: float = 0.0
    talk_time: float = 0.0
    hold_time: float = 0.0
    wait_time: float = 0.0
    talk_ratio: float = 0.0
    sentiment_score: float = 0.0
    energy_level: float = 0.0
    interruptions: int = 0
    keywords_mentioned: List[str] = []
    objections_raised: List[str] = []

class CallRecording(BaseModel):
    id: str = None
    call_id: str
    file_url: str
    duration: float
    file_size: int
    format: str = "mp3"
    quality: str = "high"
    created_at: datetime
    
    def __init__(self, **data):
        if data.get('id') is None:
            data['id'] = str(uuid.uuid4())
        super().__init__(**data)

class AgentInfo(BaseModel):
    id: str
    name: str
    status: AgentStatus
    current_call_id: Optional[str] = None
    calls_today: int = 0
    calls_answered: int = 0
    average_handle_time: float = 0.0
    customer_satisfaction: float = 0.0
    login_time: Optional[datetime] = None

class CallCreate(BaseModel):
    direction: CallDirection
    phone_number: str
    campaign_id: Optional[str] = None
    agent_id: Optional[str] = None
    priority: CallPriority = CallPriority.NORMAL
    scheduled_time: Optional[datetime] = None
    customer_data: Dict[str, Any] = {}
    script_id: Optional[str] = None

class CallUpdate(BaseModel):
    status: Optional[CallStatus] = None
    agent_id: Optional[str] = None
    notes: Optional[str] = None
    customer_data: Optional[Dict[str, Any]] = None
    disposition: Optional[str] = None

class CallResponse(BaseModel):
    id: str
    direction: CallDirection
    status: CallStatus
    phone_number: str
    campaign_id: Optional[str]
    agent_id: Optional[str]
    priority: CallPriority
    created_at: datetime
    started_at: Optional[datetime]
    ended_at: Optional[datetime]
    duration: float = 0.0
    customer_data: Dict[str, Any]
    notes: Optional[str]
    disposition: Optional[str]
    metrics: Optional[CallMetrics] = None
    recording: Optional[CallRecording] = None
    transcript: List[TranscriptSegment] = []

class QueueStatus(BaseModel):
    total_calls: int
    waiting_calls: int
    active_calls: int
    completed_calls: int
    average_wait_time: float
    longest_wait_time: float
    available_agents: int
    busy_agents: int
    service_level: float

class RealTimeMetrics(BaseModel):
    timestamp: datetime
    active_calls: int
    waiting_calls: int
    agents_available: int
    agents_busy: int
    average_wait_time: float
    calls_per_hour: int
    answer_rate: float
    abandonment_rate: float
    average_handle_time: float

# Global state (In production, use proper database)
calls_db = {}
agents_db = {}
transcript_db = {}
call_queue = []
active_websockets = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("🚀 Call Center Service starting up...")
    
    # Initialize sample data
    await initialize_sample_data()
    
    # Start background tasks
    asyncio.create_task(call_processing_loop())
    asyncio.create_task(metrics_broadcast_loop())
    
    yield
    
    logger.info("💤 Call Center Service shutting down...")

app = FastAPI(
    title="Call Center Service",
    description="Real-time call monitoring, live transcripts, and call management",
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

async def initialize_sample_data():
    """Initialize sample call center data"""
    
    # Sample agents
    agent_ids = ["agent_001", "agent_002", "agent_003", "agent_004", "agent_005"]
    for i, agent_id in enumerate(agent_ids):
        agents_db[agent_id] = AgentInfo(
            id=agent_id,
            name=f"Agent {i+1}",
            status=random.choice([AgentStatus.AVAILABLE, AgentStatus.BUSY, AgentStatus.IN_CALL]),
            calls_today=random.randint(5, 25),
            calls_answered=random.randint(4, 23),
            average_handle_time=random.uniform(180, 420),
            customer_satisfaction=random.uniform(3.5, 5.0),
            login_time=datetime.utcnow() - timedelta(hours=random.randint(1, 8))
        )
    
    # Sample active calls
    call_statuses = [CallStatus.IN_PROGRESS, CallStatus.ON_HOLD, CallStatus.ANSWERED]
    for i in range(3):
        call_id = str(uuid.uuid4())
        agent_id = random.choice(agent_ids)
        
        # Sample transcript
        transcript = [
            TranscriptSegment(
                speaker=TranscriptSpeaker.AGENT,
                text="Hello! Thank you for calling Vocelio AI. My name is Sarah. How can I help you today?",
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 5)),
                confidence=0.98,
                sentiment="positive"
            ),
            TranscriptSegment(
                speaker=TranscriptSpeaker.CUSTOMER,
                text="Hi Sarah, I'm interested in learning more about your AI voice solutions for my business.",
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 4)),
                confidence=0.96,
                sentiment="neutral",
                keywords=["interested", "AI voice", "business"]
            ),
            TranscriptSegment(
                speaker=TranscriptSpeaker.AGENT,
                text="That's wonderful! I'd be happy to help you learn about our AI voice solutions. Can you tell me a bit about your business and what you're looking to achieve?",
                timestamp=datetime.utcnow() - timedelta(minutes=random.randint(1, 3)),
                confidence=0.97,
                sentiment="positive"
            )
        ]
        
        call_data = {
            "id": call_id,
            "direction": CallDirection.INBOUND,
            "status": random.choice(call_statuses),
            "phone_number": f"+1555{random.randint(1000000, 9999999)}",
            "campaign_id": "campaign_001",
            "agent_id": agent_id,
            "priority": CallPriority.NORMAL,
            "created_at": datetime.utcnow() - timedelta(minutes=random.randint(1, 10)),
            "started_at": datetime.utcnow() - timedelta(minutes=random.randint(1, 8)),
            "ended_at": None,
            "duration": random.uniform(60, 600),
            "customer_data": {
                "name": f"Customer {i+1}",
                "company": f"Company {i+1}",
                "email": f"customer{i+1}@example.com",
                "segment": "enterprise"
            },
            "notes": f"Customer inquiry about AI voice solutions - Call {i+1}",
            "disposition": None,
            "transcript": [segment.dict() for segment in transcript]
        }
        
        calls_db[call_id] = call_data
        transcript_db[call_id] = transcript
        
        # Update agent status
        if call_data["status"] == CallStatus.IN_PROGRESS:
            agents_db[agent_id].status = AgentStatus.IN_CALL
            agents_db[agent_id].current_call_id = call_id
    
    # Sample completed calls
    for i in range(10):
        call_id = str(uuid.uuid4())
        started_time = datetime.utcnow() - timedelta(hours=random.randint(1, 24))
        duration = random.uniform(120, 900)
        
        call_data = {
            "id": call_id,
            "direction": random.choice([CallDirection.INBOUND, CallDirection.OUTBOUND]),
            "status": CallStatus.COMPLETED,
            "phone_number": f"+1555{random.randint(1000000, 9999999)}",
            "campaign_id": "campaign_001",
            "agent_id": random.choice(agent_ids),
            "priority": random.choice([CallPriority.NORMAL, CallPriority.HIGH]),
            "created_at": started_time - timedelta(minutes=2),
            "started_at": started_time,
            "ended_at": started_time + timedelta(seconds=duration),
            "duration": duration,
            "customer_data": {
                "name": f"Customer {i+10}",
                "company": f"Company {i+10}",
                "email": f"customer{i+10}@example.com"
            },
            "notes": f"Completed call - outcome: {'successful' if random.random() > 0.3 else 'unsuccessful'}",
            "disposition": random.choice(["interested", "not_interested", "callback", "demo_scheduled"]),
            "transcript": []
        }
        
        calls_db[call_id] = call_data

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

# Routes

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "call-center",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.websocket("/ws/live-updates")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/calls", response_model=List[CallResponse])
async def get_calls(
    status: Optional[CallStatus] = None,
    direction: Optional[CallDirection] = None,
    agent_id: Optional[str] = None,
    limit: int = Query(default=50, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get calls with optional filtering"""
    
    calls = list(calls_db.values())
    
    # Apply filters
    if status:
        calls = [c for c in calls if c["status"] == status]
    if direction:
        calls = [c for c in calls if c["direction"] == direction]
    if agent_id:
        calls = [c for c in calls if c["agent_id"] == agent_id]
    
    # Sort by created_at desc
    calls.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Apply pagination
    calls = calls[offset:offset + limit]
    
    return calls

@app.get("/calls/{call_id}", response_model=CallResponse)
async def get_call(
    call_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get call by ID"""
    
    if call_id not in calls_db:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return calls_db[call_id]

@app.post("/calls", response_model=CallResponse)
async def create_call(
    call: CallCreate,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user)
):
    """Create a new call"""
    
    call_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    call_data = {
        "id": call_id,
        **call.dict(),
        "status": CallStatus.QUEUED,
        "created_at": now,
        "started_at": None,
        "ended_at": None,
        "duration": 0.0,
        "notes": None,
        "disposition": None,
        "transcript": []
    }
    
    calls_db[call_id] = call_data
    
    # Add to queue for processing
    call_queue.append(call_id)
    
    # Start call processing in background
    background_tasks.add_task(process_call, call_id)
    
    return call_data

@app.put("/calls/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: str,
    updates: CallUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update call"""
    
    if call_id not in calls_db:
        raise HTTPException(status_code=404, detail="Call not found")
    
    call = calls_db[call_id]
    
    # Apply updates
    update_data = updates.dict(exclude_unset=True)
    call.update(update_data)
    
    # Handle status changes
    if "status" in update_data:
        await handle_status_change(call_id, update_data["status"])
    
    return call

@app.post("/calls/{call_id}/transfer")
async def transfer_call(
    call_id: str,
    target_agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Transfer call to another agent"""
    
    if call_id not in calls_db:
        raise HTTPException(status_code=404, detail="Call not found")
    
    if target_agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Target agent not found")
    
    call = calls_db[call_id]
    target_agent = agents_db[target_agent_id]
    
    if target_agent.status != AgentStatus.AVAILABLE:
        raise HTTPException(status_code=400, detail="Target agent is not available")
    
    # Update call
    old_agent_id = call["agent_id"]
    call["agent_id"] = target_agent_id
    call["status"] = CallStatus.TRANSFERRING
    
    # Update agent statuses
    if old_agent_id and old_agent_id in agents_db:
        agents_db[old_agent_id].status = AgentStatus.AVAILABLE
        agents_db[old_agent_id].current_call_id = None
    
    target_agent.status = AgentStatus.IN_CALL
    target_agent.current_call_id = call_id
    
    # Add transfer note to transcript
    transcript_segment = TranscriptSegment(
        speaker=TranscriptSpeaker.SYSTEM,
        text=f"Call transferred to {target_agent.name}",
        timestamp=datetime.utcnow()
    )
    
    if call_id not in transcript_db:
        transcript_db[call_id] = []
    transcript_db[call_id].append(transcript_segment)
    call["transcript"].append(transcript_segment.dict())
    
    return {"message": "Call transferred successfully"}

@app.post("/calls/{call_id}/hold")
async def hold_call(
    call_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Put call on hold"""
    
    if call_id not in calls_db:
        raise HTTPException(status_code=404, detail="Call not found")
    
    call = calls_db[call_id]
    
    if call["status"] not in [CallStatus.IN_PROGRESS, CallStatus.ANSWERED]:
        raise HTTPException(status_code=400, detail="Can only hold active calls")
    
    call["status"] = CallStatus.ON_HOLD
    
    # Add hold note to transcript
    transcript_segment = TranscriptSegment(
        speaker=TranscriptSpeaker.SYSTEM,
        text="Call placed on hold",
        timestamp=datetime.utcnow()
    )
    
    if call_id not in transcript_db:
        transcript_db[call_id] = []
    transcript_db[call_id].append(transcript_segment)
    call["transcript"].append(transcript_segment.dict())
    
    return {"message": "Call placed on hold"}

@app.post("/calls/{call_id}/resume")
async def resume_call(
    call_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Resume call from hold"""
    
    if call_id not in calls_db:
        raise HTTPException(status_code=404, detail="Call not found")
    
    call = calls_db[call_id]
    
    if call["status"] != CallStatus.ON_HOLD:
        raise HTTPException(status_code=400, detail="Call is not on hold")
    
    call["status"] = CallStatus.IN_PROGRESS
    
    # Add resume note to transcript
    transcript_segment = TranscriptSegment(
        speaker=TranscriptSpeaker.SYSTEM,
        text="Call resumed from hold",
        timestamp=datetime.utcnow()
    )
    
    if call_id not in transcript_db:
        transcript_db[call_id] = []
    transcript_db[call_id].append(transcript_segment)
    call["transcript"].append(transcript_segment.dict())
    
    return {"message": "Call resumed"}

@app.get("/calls/{call_id}/transcript", response_model=List[TranscriptSegment])
async def get_call_transcript(
    call_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get real-time call transcript"""
    
    if call_id not in calls_db:
        raise HTTPException(status_code=404, detail="Call not found")
    
    return transcript_db.get(call_id, [])

@app.get("/agents", response_model=List[AgentInfo])
async def get_agents(
    status: Optional[AgentStatus] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get call center agents"""
    
    agents = list(agents_db.values())
    
    if status:
        agents = [a for a in agents if a.status == status]
    
    return agents

@app.get("/agents/{agent_id}", response_model=AgentInfo)
async def get_agent(
    agent_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get agent by ID"""
    
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agents_db[agent_id]

@app.post("/agents/{agent_id}/status")
async def update_agent_status(
    agent_id: str,
    status: AgentStatus,
    current_user: dict = Depends(get_current_user)
):
    """Update agent status"""
    
    if agent_id not in agents_db:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents_db[agent_id]
    old_status = agent.status
    agent.status = status
    
    # Handle status change logic
    if status == AgentStatus.OFFLINE and agent.current_call_id:
        # Transfer active call if going offline
        # In production, implement proper call transfer logic
        agent.current_call_id = None
    
    return {"message": f"Agent status updated from {old_status} to {status}"}

@app.get("/queue/status", response_model=QueueStatus)
async def get_queue_status(current_user: dict = Depends(get_current_user)):
    """Get call queue status"""
    
    total_calls = len(calls_db)
    waiting_calls = len([c for c in calls_db.values() if c["status"] == CallStatus.QUEUED])
    active_calls = len([c for c in calls_db.values() if c["status"] in [CallStatus.IN_PROGRESS, CallStatus.ANSWERED]])
    completed_calls = len([c for c in calls_db.values() if c["status"] == CallStatus.COMPLETED])
    
    available_agents = len([a for a in agents_db.values() if a.status == AgentStatus.AVAILABLE])
    busy_agents = len([a for a in agents_db.values() if a.status in [AgentStatus.BUSY, AgentStatus.IN_CALL]])
    
    # Calculate average wait time (simplified)
    wait_times = [
        (datetime.utcnow() - datetime.fromisoformat(c["created_at"])).total_seconds()
        for c in calls_db.values() 
        if c["status"] == CallStatus.QUEUED
    ]
    
    avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
    longest_wait_time = max(wait_times) if wait_times else 0
    
    return QueueStatus(
        total_calls=total_calls,
        waiting_calls=waiting_calls,
        active_calls=active_calls,
        completed_calls=completed_calls,
        average_wait_time=avg_wait_time,
        longest_wait_time=longest_wait_time,
        available_agents=available_agents,
        busy_agents=busy_agents,
        service_level=95.2  # Simulated
    )

@app.get("/metrics/realtime", response_model=RealTimeMetrics)
async def get_realtime_metrics(current_user: dict = Depends(get_current_user)):
    """Get real-time call center metrics"""
    
    active_calls = len([c for c in calls_db.values() if c["status"] in [CallStatus.IN_PROGRESS, CallStatus.ANSWERED]])
    waiting_calls = len([c for c in calls_db.values() if c["status"] == CallStatus.QUEUED])
    agents_available = len([a for a in agents_db.values() if a.status == AgentStatus.AVAILABLE])
    agents_busy = len([a for a in agents_db.values() if a.status in [AgentStatus.BUSY, AgentStatus.IN_CALL]])
    
    # Simulated metrics (in production, calculate from actual data)
    return RealTimeMetrics(
        timestamp=datetime.utcnow(),
        active_calls=active_calls,
        waiting_calls=waiting_calls,
        agents_available=agents_available,
        agents_busy=agents_busy,
        average_wait_time=45.2,
        calls_per_hour=127,
        answer_rate=94.8,
        abandonment_rate=2.1,
        average_handle_time=256.7
    )

@app.get("/analytics/dashboard")
async def get_dashboard_analytics(
    date_range: int = Query(default=7, description="Days of data to include"),
    current_user: dict = Depends(get_current_user)
):
    """Get dashboard analytics for Call Center"""
    
    return {
        "overview": {
            "total_calls_today": 234,
            "answered_calls": 221,
            "missed_calls": 13,
            "average_wait_time": 42.3,
            "service_level": 94.8,
            "agent_utilization": 78.5
        },
        "performance": {
            "answer_rate": 94.8,
            "abandonment_rate": 2.1,
            "first_call_resolution": 87.3,
            "average_handle_time": 256.7,
            "customer_satisfaction": 4.3,
            "calls_per_agent": 28.5
        },
        "trends": {
            "calls_by_hour": [12, 18, 24, 31, 28, 35, 42, 38, 29, 25, 19, 15],
            "wait_times": [45, 52, 38, 41, 47, 43, 39],
            "agent_efficiency": [82, 85, 79, 88, 84, 86, 81]
        },
        "agents": {
            "total_agents": len(agents_db),
            "available": len([a for a in agents_db.values() if a.status == AgentStatus.AVAILABLE]),
            "busy": len([a for a in agents_db.values() if a.status in [AgentStatus.BUSY, AgentStatus.IN_CALL]]),
            "on_break": len([a for a in agents_db.values() if a.status == AgentStatus.ON_BREAK]),
            "top_performer": "Agent 1"
        }
    }

# Background Tasks

async def handle_status_change(call_id: str, new_status: CallStatus):
    """Handle call status changes"""
    
    call = calls_db.get(call_id)
    if not call:
        return
    
    now = datetime.utcnow()
    
    if new_status == CallStatus.ANSWERED and not call["started_at"]:
        call["started_at"] = now
    elif new_status == CallStatus.COMPLETED and not call["ended_at"]:
        call["ended_at"] = now
        if call["started_at"]:
            call["duration"] = (now - datetime.fromisoformat(call["started_at"])).total_seconds()
        
        # Free up agent
        if call["agent_id"] and call["agent_id"] in agents_db:
            agents_db[call["agent_id"]].status = AgentStatus.AVAILABLE
            agents_db[call["agent_id"]].current_call_id = None

async def process_call(call_id: str):
    """Process call (simulated)"""
    
    call = calls_db.get(call_id)
    if not call:
        return
    
    logger.info(f"Processing call {call_id}")
    
    # Simulate call progression
    await asyncio.sleep(2)
    
    # Move from queued to ringing
    call["status"] = CallStatus.RINGING
    await asyncio.sleep(3)
    
    # Simulate answer or no answer
    if random.random() > 0.1:  # 90% answer rate
        call["status"] = CallStatus.ANSWERED
        call["started_at"] = datetime.utcnow()
        
        # Assign to available agent
        available_agents = [a for a in agents_db.values() if a.status == AgentStatus.AVAILABLE]
        if available_agents:
            agent = random.choice(available_agents)
            call["agent_id"] = agent.id
            agent.status = AgentStatus.IN_CALL
            agent.current_call_id = call_id
        
        await asyncio.sleep(2)
        call["status"] = CallStatus.IN_PROGRESS
        
        # Simulate live transcript generation
        await simulate_live_transcript(call_id)
        
    else:
        call["status"] = CallStatus.NO_ANSWER
        call["ended_at"] = datetime.utcnow()

async def simulate_live_transcript(call_id: str):
    """Simulate live transcript generation"""
    
    if call_id not in transcript_db:
        transcript_db[call_id] = []
    
    sample_conversations = [
        ("agent", "Thank you for calling! How can I help you today?"),
        ("customer", "Hi, I'm interested in your AI voice services."),
        ("agent", "Great! I'd be happy to help. What type of business do you have?"),
        ("customer", "We're a software company with about 50 employees."),
        ("agent", "Perfect! Our AI solutions can really help streamline your customer communication."),
        ("customer", "That sounds interesting. Can you tell me more about pricing?"),
        ("agent", "Absolutely! Let me walk you through our pricing tiers...")
    ]
    
    for i, (speaker, text) in enumerate(sample_conversations):
        await asyncio.sleep(random.uniform(5, 15))  # Random intervals
        
        # Check if call is still active
        call = calls_db.get(call_id)
        if not call or call["status"] not in [CallStatus.IN_PROGRESS, CallStatus.ANSWERED]:
            break
        
        segment = TranscriptSegment(
            speaker=TranscriptSpeaker.AGENT if speaker == "agent" else TranscriptSpeaker.CUSTOMER,
            text=text,
            timestamp=datetime.utcnow(),
            confidence=random.uniform(0.85, 0.99),
            sentiment=random.choice(["positive", "neutral", "negative"])
        )
        
        transcript_db[call_id].append(segment)
        call["transcript"].append(segment.dict())
        
        # Broadcast to WebSocket clients
        await manager.broadcast(json.dumps({
            "type": "transcript_update",
            "call_id": call_id,
            "segment": segment.dict()
        }))

async def call_processing_loop():
    """Background loop for processing calls"""
    
    while True:
        try:
            # Process queued calls
            if call_queue:
                call_id = call_queue.pop(0)
                await process_call(call_id)
            
            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error in call processing loop: {e}")

async def metrics_broadcast_loop():
    """Background loop for broadcasting real-time metrics"""
    
    while True:
        try:
            # Get current metrics
            metrics = {
                "type": "metrics_update",
                "data": {
                    "active_calls": len([c for c in calls_db.values() if c["status"] in [CallStatus.IN_PROGRESS, CallStatus.ANSWERED]]),
                    "waiting_calls": len([c for c in calls_db.values() if c["status"] == CallStatus.QUEUED]),
                    "available_agents": len([a for a in agents_db.values() if a.status == AgentStatus.AVAILABLE]),
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            await manager.broadcast(json.dumps(metrics))
            await asyncio.sleep(5)  # Broadcast every 5 seconds
            
        except Exception as e:
            logger.error(f"Error in metrics broadcast loop: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )