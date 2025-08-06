"""
Flow Builder Service - Vocelio AI Call Center
Visual conversation flow designer and workflow automation
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flow Builder Models
class NodeType(str, Enum):
    START = "start"
    END = "end"
    MESSAGE = "message"
    QUESTION = "question"
    CONDITION = "condition"
    ACTION = "action"
    API_CALL = "api_call"
    TRANSFER = "transfer"
    COLLECT_INPUT = "collect_input"
    PLAY_AUDIO = "play_audio"
    RECORD_AUDIO = "record_audio"
    WEBHOOK = "webhook"
    DECISION_TREE = "decision_tree"
    AI_RESPONSE = "ai_response"
    DELAY = "delay"

class FlowStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    TESTING = "testing"

class NodePosition(BaseModel):
    x: float
    y: float

class NodeConnection(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None
    label: Optional[str] = None

class NodeConfiguration(BaseModel):
    message_text: Optional[str] = None
    voice_settings: Optional[Dict[str, Any]] = None
    timeout_seconds: Optional[int] = None
    max_attempts: Optional[int] = None
    expected_input_type: Optional[str] = None  # "speech", "dtmf", "both"
    api_endpoint: Optional[str] = None
    api_method: Optional[str] = None
    api_headers: Optional[Dict[str, str]] = None
    api_payload: Optional[Dict[str, Any]] = None
    transfer_destination: Optional[str] = None
    webhook_url: Optional[str] = None
    audio_file_url: Optional[str] = None
    recording_duration: Optional[int] = None
    delay_seconds: Optional[int] = None
    ai_prompt: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None

class FlowNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: NodeType
    position: NodePosition
    configuration: NodeConfiguration = Field(default_factory=NodeConfiguration)
    connections: List[str] = []  # IDs of connected nodes
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ConversationFlow(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    version: str = "1.0.0"
    status: FlowStatus
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    nodes: List[FlowNode] = []
    connections: List[NodeConnection] = []
    variables: Dict[str, Any] = {}
    tags: List[str] = []
    category: str = "general"
    is_template: bool = False
    usage_count: int = 0
    success_rate: float = 0.0
    average_duration: float = 0.0

class FlowTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    category: str
    template_data: ConversationFlow
    preview_image: Optional[str] = None
    difficulty_level: str = "beginner"  # "beginner", "intermediate", "advanced"
    estimated_setup_time: int = 15  # minutes
    features: List[str] = []
    use_cases: List[str] = []
    created_at: datetime = Field(default_factory=datetime.now)
    downloads: int = 0
    rating: float = 4.5

class FlowExecution(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    flow_id: str
    call_id: str
    current_node_id: str
    execution_context: Dict[str, Any] = {}
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    status: str = "running"  # "running", "completed", "failed", "paused"
    error_message: Optional[str] = None
    execution_path: List[str] = []  # Node IDs in execution order

class FlowValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    suggestions: List[str] = []

class FlowAnalytics(BaseModel):
    flow_id: str
    total_executions: int
    successful_executions: int
    failed_executions: int
    average_completion_time: float
    most_common_path: List[str]
    drop_off_points: List[Dict[str, Any]]
    conversion_rate: float
    performance_metrics: Dict[str, Any]

# Sample Flow Templates
SAMPLE_TEMPLATES = [
    FlowTemplate(
        name="Customer Support Flow",
        description="Basic customer support flow with routing to different departments",
        category="support",
        template_data=ConversationFlow(
            name="Customer Support Template",
            description="Template for customer support calls",
            status=FlowStatus.PUBLISHED,
            created_by="system",
            nodes=[],
            category="support"
        ),
        difficulty_level="beginner",
        estimated_setup_time=10,
        features=["Department Routing", "Queue Management", "Callback Option"],
        use_cases=["Technical Support", "Billing Inquiries", "General Help"],
        downloads=1247,
        rating=4.7
    ),
    FlowTemplate(
        name="Sales Qualification Flow",
        description="Lead qualification and appointment booking flow",
        category="sales",
        template_data=ConversationFlow(
            name="Sales Qualification Template",
            description="Template for sales calls",
            status=FlowStatus.PUBLISHED,
            created_by="system",
            nodes=[],
            category="sales"
        ),
        difficulty_level="intermediate",
        estimated_setup_time=20,
        features=["Lead Scoring", "CRM Integration", "Calendar Booking"],
        use_cases=["Lead Qualification", "Product Demos", "Follow-up Calls"],
        downloads=892,
        rating=4.5
    ),
    FlowTemplate(
        name="Survey Collection Flow",
        description="Automated survey and feedback collection",
        category="research",
        template_data=ConversationFlow(
            name="Survey Collection Template",
            description="Template for survey calls",
            status=FlowStatus.PUBLISHED,
            created_by="system",
            nodes=[],
            category="research"
        ),
        difficulty_level="beginner",
        estimated_setup_time=15,
        features=["Multi-Question Surveys", "Rating Collection", "Data Export"],
        use_cases=["Customer Satisfaction", "Market Research", "Product Feedback"],
        downloads=654,
        rating=4.3
    )
]

SAMPLE_FLOWS = [
    ConversationFlow(
        name="Welcome & Routing Flow",
        description="Main greeting flow that routes callers to appropriate departments",
        status=FlowStatus.PUBLISHED,
        created_by="admin@vocelio.com",
        nodes=[
            FlowNode(
                name="Start Call",
                type=NodeType.START,
                position=NodePosition(x=100, y=100),
                configuration=NodeConfiguration(
                    message_text="Welcome to Vocelio! How can we help you today?"
                )
            ),
            FlowNode(
                name="Collect Input",
                type=NodeType.COLLECT_INPUT,
                position=NodePosition(x=300, y=100),
                configuration=NodeConfiguration(
                    message_text="Please say 'sales' for sales, 'support' for support, or 'billing' for billing.",
                    expected_input_type="speech",
                    timeout_seconds=10,
                    max_attempts=3
                )
            ),
            FlowNode(
                name="Route Decision",
                type=NodeType.CONDITION,
                position=NodePosition(x=500, y=100),
                configuration=NodeConfiguration(
                    variables={"routing_keywords": ["sales", "support", "billing"]}
                )
            ),
            FlowNode(
                name="Transfer to Sales",
                type=NodeType.TRANSFER,
                position=NodePosition(x=400, y=250),
                configuration=NodeConfiguration(
                    message_text="Transferring you to our sales team...",
                    transfer_destination="sales_queue"
                )
            ),
            FlowNode(
                name="Transfer to Support",
                type=NodeType.TRANSFER,
                position=NodePosition(x=600, y=250),
                configuration=NodeConfiguration(
                    message_text="Connecting you with technical support...",
                    transfer_destination="support_queue"
                )
            )
        ],
        connections=[
            NodeConnection(from_node="start_1", to_node="collect_1", label="Begin"),
            NodeConnection(from_node="collect_1", to_node="condition_1", label="Input Received"),
            NodeConnection(from_node="condition_1", to_node="transfer_sales", condition="input contains 'sales'"),
            NodeConnection(from_node="condition_1", to_node="transfer_support", condition="input contains 'support'")
        ],
        category="routing",
        usage_count=1450,
        success_rate=94.7,
        average_duration=45.2
    ),
    ConversationFlow(
        name="Appointment Booking Flow",
        description="Automated appointment booking with calendar integration",
        status=FlowStatus.PUBLISHED,
        created_by="sales@vocelio.com",
        nodes=[
            FlowNode(
                name="Welcome Message",
                type=NodeType.MESSAGE,
                position=NodePosition(x=100, y=100),
                configuration=NodeConfiguration(
                    message_text="Hello! I'm here to help you schedule an appointment. Let me check available times."
                )
            ),
            FlowNode(
                name="Check Calendar",
                type=NodeType.API_CALL,
                position=NodePosition(x=300, y=100),
                configuration=NodeConfiguration(
                    api_endpoint="https://calendar.vocelio.com/api/available-slots",
                    api_method="GET",
                    api_headers={"Authorization": "Bearer token"}
                )
            ),
            FlowNode(
                name="Present Options",
                type=NodeType.QUESTION,
                position=NodePosition(x=500, y=100),
                configuration=NodeConfiguration(
                    message_text="I have availability tomorrow at 2 PM, Thursday at 10 AM, or Friday at 3 PM. Which works best for you?",
                    expected_input_type="speech"
                )
            )
        ],
        category="sales",
        usage_count=687,
        success_rate=89.3,
        average_duration=120.5
    )
]

# Global storage
flows: List[ConversationFlow] = []
templates: List[FlowTemplate] = []
executions: List[FlowExecution] = []
active_websockets: List[WebSocket] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global flows, templates
    
    flows.extend(SAMPLE_FLOWS)
    templates.extend(SAMPLE_TEMPLATES)
    
    logger.info("Sample flow data initialized successfully")

async def broadcast_flow_update(flow_id: str, update_type: str, data: Dict[str, Any]):
    """Broadcast flow updates to connected WebSocket clients"""
    message = {
        "type": update_type,
        "flow_id": flow_id,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }
    
    disconnected = []
    for websocket in active_websockets:
        try:
            await websocket.send_text(json.dumps(message))
        except:
            disconnected.append(websocket)
    
    # Remove disconnected websockets
    for ws in disconnected:
        active_websockets.remove(ws)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    yield
    
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="Flow Builder Service",
    description="Visual conversation flow designer and workflow automation for Vocelio AI Call Center",
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
        "service": "flow-builder",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# WebSocket endpoint for real-time collaboration
@app.websocket("/ws/flows/{flow_id}")
async def websocket_endpoint(websocket: WebSocket, flow_id: str):
    await websocket.accept()
    active_websockets.append(websocket)
    
    try:
        await websocket.send_text(json.dumps({
            "type": "connected",
            "flow_id": flow_id,
            "message": "Connected to flow builder"
        }))
        
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Broadcast updates to other connected clients
            await broadcast_flow_update(flow_id, message.get("type", "update"), message.get("data", {}))
            
    except WebSocketDisconnect:
        active_websockets.remove(websocket)

# Flow Management Endpoints
@app.get("/flows", response_model=List[ConversationFlow])
async def get_flows(
    status: Optional[FlowStatus] = None,
    category: Optional[str] = None,
    created_by: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all conversation flows with optional filtering"""
    filtered_flows = flows
    
    if status:
        filtered_flows = [f for f in filtered_flows if f.status == status]
    
    if category:
        filtered_flows = [f for f in filtered_flows if f.category == category]
    
    if created_by:
        filtered_flows = [f for f in filtered_flows if f.created_by == created_by]
    
    if search:
        search_lower = search.lower()
        filtered_flows = [
            f for f in filtered_flows 
            if search_lower in f.name.lower() or search_lower in f.description.lower()
        ]
    
    return filtered_flows

@app.get("/flows/{flow_id}", response_model=ConversationFlow)
async def get_flow(flow_id: str):
    """Get a specific conversation flow by ID"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    return flow

@app.post("/flows", response_model=ConversationFlow)
async def create_flow(flow_data: ConversationFlow):
    """Create a new conversation flow"""
    flows.append(flow_data)
    
    # Broadcast creation event
    await broadcast_flow_update(flow_data.id, "flow_created", flow_data.dict())
    
    return flow_data

@app.put("/flows/{flow_id}", response_model=ConversationFlow)
async def update_flow(flow_id: str, flow_data: ConversationFlow):
    """Update an existing conversation flow"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    # Update fields
    for field, value in flow_data.dict(exclude_unset=True).items():
        setattr(flow, field, value)
    
    flow.updated_at = datetime.now()
    
    # Broadcast update event
    await broadcast_flow_update(flow_id, "flow_updated", flow.dict())
    
    return flow

@app.delete("/flows/{flow_id}")
async def delete_flow(flow_id: str):
    """Delete a conversation flow"""
    global flows
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    flows = [f for f in flows if f.id != flow_id]
    
    # Broadcast deletion event
    await broadcast_flow_update(flow_id, "flow_deleted", {"flow_id": flow_id})
    
    return {"message": "Flow deleted successfully"}

# Node Management Endpoints
@app.post("/flows/{flow_id}/nodes", response_model=FlowNode)
async def add_node_to_flow(flow_id: str, node_data: FlowNode):
    """Add a new node to a conversation flow"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    flow.nodes.append(node_data)
    flow.updated_at = datetime.now()
    
    # Broadcast node addition
    await broadcast_flow_update(flow_id, "node_added", node_data.dict())
    
    return node_data

@app.put("/flows/{flow_id}/nodes/{node_id}", response_model=FlowNode)
async def update_node(flow_id: str, node_id: str, node_data: FlowNode):
    """Update a node in a conversation flow"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    node = next((n for n in flow.nodes if n.id == node_id), None)
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    # Update node fields
    for field, value in node_data.dict(exclude_unset=True).items():
        setattr(node, field, value)
    
    node.updated_at = datetime.now()
    flow.updated_at = datetime.now()
    
    # Broadcast node update
    await broadcast_flow_update(flow_id, "node_updated", node.dict())
    
    return node

@app.delete("/flows/{flow_id}/nodes/{node_id}")
async def delete_node(flow_id: str, node_id: str):
    """Delete a node from a conversation flow"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    flow.nodes = [n for n in flow.nodes if n.id != node_id]
    flow.connections = [c for c in flow.connections if c.from_node != node_id and c.to_node != node_id]
    flow.updated_at = datetime.now()
    
    # Broadcast node deletion
    await broadcast_flow_update(flow_id, "node_deleted", {"node_id": node_id})
    
    return {"message": "Node deleted successfully"}

# Connection Management Endpoints
@app.post("/flows/{flow_id}/connections")
async def add_connection(flow_id: str, connection_data: NodeConnection):
    """Add a connection between nodes in a flow"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    # Verify nodes exist
    from_node_exists = any(n.id == connection_data.from_node for n in flow.nodes)
    to_node_exists = any(n.id == connection_data.to_node for n in flow.nodes)
    
    if not from_node_exists or not to_node_exists:
        raise HTTPException(status_code=400, detail="One or both nodes do not exist")
    
    flow.connections.append(connection_data)
    flow.updated_at = datetime.now()
    
    # Broadcast connection addition
    await broadcast_flow_update(flow_id, "connection_added", connection_data.dict())
    
    return {"message": "Connection added successfully"}

@app.delete("/flows/{flow_id}/connections")
async def remove_connection(flow_id: str, from_node: str, to_node: str):
    """Remove a connection between nodes"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    original_count = len(flow.connections)
    flow.connections = [
        c for c in flow.connections 
        if not (c.from_node == from_node and c.to_node == to_node)
    ]
    
    if len(flow.connections) == original_count:
        raise HTTPException(status_code=404, detail="Connection not found")
    
    flow.updated_at = datetime.now()
    
    # Broadcast connection removal
    await broadcast_flow_update(flow_id, "connection_removed", {
        "from_node": from_node,
        "to_node": to_node
    })
    
    return {"message": "Connection removed successfully"}

# Flow Validation Endpoints
@app.post("/flows/{flow_id}/validate", response_model=FlowValidationResult)
async def validate_flow(flow_id: str):
    """Validate a conversation flow for errors and issues"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    errors = []
    warnings = []
    suggestions = []
    
    # Check for start node
    start_nodes = [n for n in flow.nodes if n.type == NodeType.START]
    if not start_nodes:
        errors.append("Flow must have at least one START node")
    elif len(start_nodes) > 1:
        warnings.append("Flow has multiple START nodes, only the first will be used")
    
    # Check for end nodes
    end_nodes = [n for n in flow.nodes if n.type == NodeType.END]
    if not end_nodes:
        warnings.append("Flow should have at least one END node")
    
    # Check for orphaned nodes
    connected_nodes = set()
    for conn in flow.connections:
        connected_nodes.add(conn.from_node)
        connected_nodes.add(conn.to_node)
    
    for node in flow.nodes:
        if node.id not in connected_nodes and node.type != NodeType.START:
            warnings.append(f"Node '{node.name}' is not connected to any other nodes")
    
    # Check for unreachable nodes
    if start_nodes:
        reachable = set()
        to_visit = [start_nodes[0].id]
        
        while to_visit:
            current = to_visit.pop()
            if current not in reachable:
                reachable.add(current)
                # Add connected nodes
                for conn in flow.connections:
                    if conn.from_node == current:
                        to_visit.append(conn.to_node)
        
        for node in flow.nodes:
            if node.id not in reachable:
                warnings.append(f"Node '{node.name}' is unreachable from the start node")
    
    # Performance suggestions
    if len(flow.nodes) > 50:
        suggestions.append("Consider breaking this flow into smaller, more manageable flows")
    
    if len([n for n in flow.nodes if n.type == NodeType.API_CALL]) > 10:
        suggestions.append("High number of API calls may impact performance")
    
    is_valid = len(errors) == 0
    
    return FlowValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        suggestions=suggestions
    )

# Flow Templates Endpoints
@app.get("/templates", response_model=List[FlowTemplate])
async def get_templates(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    search: Optional[str] = None
):
    """Get all flow templates with optional filtering"""
    filtered_templates = templates
    
    if category:
        filtered_templates = [t for t in filtered_templates if t.category == category]
    
    if difficulty:
        filtered_templates = [t for t in filtered_templates if t.difficulty_level == difficulty]
    
    if search:
        search_lower = search.lower()
        filtered_templates = [
            t for t in filtered_templates
            if search_lower in t.name.lower() or search_lower in t.description.lower()
        ]
    
    return filtered_templates

@app.get("/templates/{template_id}", response_model=FlowTemplate)
async def get_template(template_id: str):
    """Get a specific flow template by ID"""
    template = next((t for t in templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@app.post("/templates/{template_id}/use", response_model=ConversationFlow)
async def create_flow_from_template(template_id: str, flow_name: str, created_by: str):
    """Create a new flow from a template"""
    template = next((t for t in templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create new flow based on template
    new_flow = ConversationFlow(
        name=flow_name,
        description=f"Created from template: {template.name}",
        status=FlowStatus.DRAFT,
        created_by=created_by,
        nodes=template.template_data.nodes.copy(),
        connections=template.template_data.connections.copy(),
        category=template.category
    )
    
    flows.append(new_flow)
    
    # Update template download count
    template.downloads += 1
    
    return new_flow

# Flow Execution Endpoints
@app.post("/flows/{flow_id}/execute")
async def execute_flow(flow_id: str, call_id: str, context: Dict[str, Any] = {}):
    """Start execution of a conversation flow"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    if flow.status != FlowStatus.PUBLISHED:
        raise HTTPException(status_code=400, detail="Only published flows can be executed")
    
    # Find start node
    start_node = next((n for n in flow.nodes if n.type == NodeType.START), None)
    if not start_node:
        raise HTTPException(status_code=400, detail="Flow has no start node")
    
    execution = FlowExecution(
        flow_id=flow_id,
        call_id=call_id,
        current_node_id=start_node.id,
        execution_context=context,
        execution_path=[start_node.id]
    )
    
    executions.append(execution)
    
    # Update flow usage count
    flow.usage_count += 1
    
    return {
        "execution_id": execution.id,
        "status": "started",
        "current_node": start_node.name,
        "message": "Flow execution started successfully"
    }

@app.get("/executions/{execution_id}", response_model=FlowExecution)
async def get_execution(execution_id: str):
    """Get execution details"""
    execution = next((e for e in executions if e.id == execution_id), None)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution

@app.get("/flows/{flow_id}/executions", response_model=List[FlowExecution])
async def get_flow_executions(flow_id: str, limit: int = 50):
    """Get recent executions for a flow"""
    flow_executions = [e for e in executions if e.flow_id == flow_id]
    flow_executions.sort(key=lambda x: x.started_at, reverse=True)
    return flow_executions[:limit]

# Analytics Endpoints
@app.get("/flows/{flow_id}/analytics", response_model=FlowAnalytics)
async def get_flow_analytics(flow_id: str):
    """Get analytics for a specific flow"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    flow_executions = [e for e in executions if e.flow_id == flow_id]
    
    total_executions = len(flow_executions)
    successful_executions = len([e for e in flow_executions if e.status == "completed"])
    failed_executions = len([e for e in flow_executions if e.status == "failed"])
    
    # Calculate average completion time
    completed_executions = [e for e in flow_executions if e.completed_at]
    avg_completion_time = 0.0
    if completed_executions:
        completion_times = [
            (e.completed_at - e.started_at).total_seconds()
            for e in completed_executions
        ]
        avg_completion_time = sum(completion_times) / len(completion_times)
    
    # Mock most common path and drop-off points
    most_common_path = [node.id for node in flow.nodes[:3]]  # Simplified
    drop_off_points = [
        {"node_id": "node_1", "drop_off_rate": 15.2},
        {"node_id": "node_3", "drop_off_rate": 8.7}
    ]
    
    conversion_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
    
    return FlowAnalytics(
        flow_id=flow_id,
        total_executions=total_executions,
        successful_executions=successful_executions,
        failed_executions=failed_executions,
        average_completion_time=avg_completion_time,
        most_common_path=most_common_path,
        drop_off_points=drop_off_points,
        conversion_rate=conversion_rate,
        performance_metrics={
            "nodes_count": len(flow.nodes),
            "connections_count": len(flow.connections),
            "complexity_score": len(flow.nodes) + len(flow.connections)
        }
    )

# Publishing Endpoints
@app.post("/flows/{flow_id}/publish")
async def publish_flow(flow_id: str):
    """Publish a flow to make it available for execution"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    # Validate flow before publishing
    validation_result = await validate_flow(flow_id)
    if not validation_result.is_valid:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot publish invalid flow. Errors: {', '.join(validation_result.errors)}"
        )
    
    flow.status = FlowStatus.PUBLISHED
    flow.published_at = datetime.now()
    flow.updated_at = datetime.now()
    
    # Broadcast publish event
    await broadcast_flow_update(flow_id, "flow_published", {"flow_id": flow_id})
    
    return {"message": "Flow published successfully", "published_at": flow.published_at}

@app.post("/flows/{flow_id}/unpublish")
async def unpublish_flow(flow_id: str):
    """Unpublish a flow to stop it from being executed"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    flow.status = FlowStatus.DRAFT
    flow.updated_at = datetime.now()
    
    # Broadcast unpublish event
    await broadcast_flow_update(flow_id, "flow_unpublished", {"flow_id": flow_id})
    
    return {"message": "Flow unpublished successfully"}

# Export/Import Endpoints
@app.get("/flows/{flow_id}/export")
async def export_flow(flow_id: str):
    """Export a flow as JSON"""
    flow = next((f for f in flows if f.id == flow_id), None)
    if not flow:
        raise HTTPException(status_code=404, detail="Flow not found")
    
    export_data = {
        "flow": flow.dict(),
        "exported_at": datetime.now().isoformat(),
        "version": "1.0.0"
    }
    
    return export_data

@app.post("/flows/import", response_model=ConversationFlow)
async def import_flow(import_data: Dict[str, Any], created_by: str):
    """Import a flow from JSON data"""
    try:
        flow_data = import_data.get("flow")
        if not flow_data:
            raise HTTPException(status_code=400, detail="Invalid import data")
        
        # Create new IDs to avoid conflicts
        imported_flow = ConversationFlow(**flow_data)
        imported_flow.id = str(uuid.uuid4())
        imported_flow.created_by = created_by
        imported_flow.created_at = datetime.now()
        imported_flow.updated_at = datetime.now()
        imported_flow.status = FlowStatus.DRAFT
        
        # Update node IDs
        for node in imported_flow.nodes:
            node.id = str(uuid.uuid4())
            node.created_at = datetime.now()
            node.updated_at = datetime.now()
        
        flows.append(imported_flow)
        
        return imported_flow
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Import failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8009)