"""
Integrations Service - Vocelio AI Call Center
CRM connections, API integrations, webhooks, and third-party platform connectivity
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
import httpx
import hashlib
import hmac
from urllib.parse import urlencode
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Integration Models
class IntegrationType(str, Enum):
    CRM = "crm"
    MARKETING = "marketing"
    ANALYTICS = "analytics"
    TELEPHONY = "telephony"
    MESSAGING = "messaging"
    PAYMENT = "payment"
    CALENDAR = "calendar"
    DATABASE = "database"
    WEBHOOK = "webhook"
    API = "api"
    SOCIAL_MEDIA = "social_media"
    EMAIL = "email"

class IntegrationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    PENDING = "pending"
    TESTING = "testing"

class AuthType(str, Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BASIC_AUTH = "basic_auth"
    BEARER_TOKEN = "bearer_token"
    WEBHOOK_SECRET = "webhook_secret"
    CUSTOM = "custom"

class SyncDirection(str, Enum):
    INBOUND = "inbound"
    OUTBOUND = "outbound"
    BIDIRECTIONAL = "bidirectional"

class AuthConfig(BaseModel):
    auth_type: AuthType
    credentials: Dict[str, Any] = {}
    oauth_config: Optional[Dict[str, str]] = None
    webhook_secret: Optional[str] = None
    headers: Dict[str, str] = {}
    test_endpoint: Optional[str] = None

class DataMapping(BaseModel):
    source_field: str
    target_field: str
    transformation: Optional[str] = None  # "uppercase", "lowercase", "date_format", etc.
    default_value: Optional[Any] = None
    required: bool = False

class SyncConfig(BaseModel):
    direction: SyncDirection
    frequency: str = "real_time"  # "real_time", "hourly", "daily", "weekly"
    batch_size: int = 100
    enabled: bool = True
    last_sync: Optional[datetime] = None
    retry_count: int = 3
    timeout_seconds: int = 30
    data_mappings: List[DataMapping] = []

class Integration(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    type: IntegrationType
    provider: str  # "salesforce", "hubspot", "zapier", etc.
    status: IntegrationStatus
    auth_config: AuthConfig
    sync_config: SyncConfig
    api_endpoint: str
    webhook_url: Optional[str] = None
    created_by: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    last_activity: Optional[datetime] = None
    error_count: int = 0
    success_count: int = 0
    metadata: Dict[str, Any] = {}
    tags: List[str] = []

class WebhookEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    integration_id: str
    event_type: str
    payload: Dict[str, Any]
    headers: Dict[str, str]
    signature: Optional[str] = None
    received_at: datetime = Field(default_factory=datetime.now)
    processed_at: Optional[datetime] = None
    status: str = "pending"  # "pending", "processed", "failed"
    retry_count: int = 0
    error_message: Optional[str] = None

class DataSync(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    integration_id: str
    direction: SyncDirection
    entity_type: str  # "contact", "lead", "call", etc.
    source_id: str
    target_id: Optional[str] = None
    data: Dict[str, Any]
    status: str = "pending"  # "pending", "synced", "failed"
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    retry_count: int = 0

class APICall(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    integration_id: str
    method: str  # "GET", "POST", "PUT", "DELETE"
    endpoint: str
    headers: Dict[str, str] = {}
    payload: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    response_data: Optional[Dict[str, Any]] = None
    duration_ms: Optional[float] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    success: bool = False
    error_message: Optional[str] = None

class IntegrationTemplate(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    provider: str
    type: IntegrationType
    template_config: Integration
    setup_instructions: List[str] = []
    required_credentials: List[str] = []
    supported_features: List[str] = []
    popularity_score: float = 0.0
    setup_difficulty: str = "medium"  # "easy", "medium", "hard"
    estimated_setup_time: int = 15  # minutes

# Sample Integration Templates
SAMPLE_TEMPLATES = [
    IntegrationTemplate(
        name="Salesforce CRM",
        description="Sync contacts, leads, and opportunities with Salesforce",
        provider="salesforce",
        type=IntegrationType.CRM,
        template_config=Integration(
            name="Salesforce Integration",
            description="Template for Salesforce CRM integration",
            type=IntegrationType.CRM,
            provider="salesforce",
            status=IntegrationStatus.INACTIVE,
            auth_config=AuthConfig(
                auth_type=AuthType.OAUTH2,
                oauth_config={
                    "client_id": "your_client_id",
                    "client_secret": "your_client_secret",
                    "redirect_uri": "https://api.vocelio.com/integrations/oauth/callback"
                }
            ),
            sync_config=SyncConfig(
                direction=SyncDirection.BIDIRECTIONAL,
                frequency="real_time"
            ),
            api_endpoint="https://your-instance.salesforce.com/services/data/v57.0/",
            created_by="system"
        ),
        setup_instructions=[
            "Create a Connected App in Salesforce",
            "Configure OAuth settings",
            "Add API permissions",
            "Test connection"
        ],
        required_credentials=["client_id", "client_secret", "instance_url"],
        supported_features=["Contact Sync", "Lead Management", "Opportunity Tracking"],
        popularity_score=9.5,
        setup_difficulty="medium",
        estimated_setup_time=20
    ),
    IntegrationTemplate(
        name="HubSpot CRM",
        description="Connect with HubSpot for contact and deal management",
        provider="hubspot",
        type=IntegrationType.CRM,
        template_config=Integration(
            name="HubSpot Integration",
            description="Template for HubSpot CRM integration",
            type=IntegrationType.CRM,
            provider="hubspot",
            status=IntegrationStatus.INACTIVE,
            auth_config=AuthConfig(
                auth_type=AuthType.API_KEY,
                credentials={"api_key": "your_hubspot_api_key"}
            ),
            sync_config=SyncConfig(
                direction=SyncDirection.BIDIRECTIONAL,
                frequency="hourly"
            ),
            api_endpoint="https://api.hubapi.com/",
            created_by="system"
        ),
        setup_instructions=[
            "Generate API key in HubSpot settings",
            "Configure webhook endpoints",
            "Set up data mappings"
        ],
        required_credentials=["api_key"],
        supported_features=["Contact Sync", "Deal Pipeline", "Email Tracking"],
        popularity_score=8.8,
        setup_difficulty="easy",
        estimated_setup_time=10
    ),
    IntegrationTemplate(
        name="Zapier Webhooks",
        description="Connect to 5000+ apps through Zapier automation",
        provider="zapier",
        type=IntegrationType.WEBHOOK,
        template_config=Integration(
            name="Zapier Integration",
            description="Template for Zapier webhook integration",
            type=IntegrationType.WEBHOOK,
            provider="zapier",
            status=IntegrationStatus.INACTIVE,
            auth_config=AuthConfig(
                auth_type=AuthType.WEBHOOK_SECRET,
                webhook_secret="your_webhook_secret"
            ),
            sync_config=SyncConfig(
                direction=SyncDirection.OUTBOUND,
                frequency="real_time"
            ),
            api_endpoint="https://hooks.zapier.com/hooks/catch/",
            webhook_url="https://api.vocelio.com/integrations/webhooks/zapier",
            created_by="system"
        ),
        setup_instructions=[
            "Create Zapier webhook trigger",
            "Configure webhook URL",
            "Set up automation workflows"
        ],
        required_credentials=["webhook_url"],
        supported_features=["Real-time Events", "Multi-app Workflows", "Data Transformation"],
        popularity_score=8.2,
        setup_difficulty="easy",
        estimated_setup_time=5
    )
]

# Sample Integrations
SAMPLE_INTEGRATIONS = [
    Integration(
        name="Production Salesforce",
        description="Main Salesforce CRM integration for customer data",
        type=IntegrationType.CRM,
        provider="salesforce",
        status=IntegrationStatus.ACTIVE,
        auth_config=AuthConfig(
            auth_type=AuthType.OAUTH2,
            oauth_config={
                "client_id": "3MVG9...demo",
                "access_token": "00D...demo",
                "refresh_token": "5Aep...demo"
            }
        ),
        sync_config=SyncConfig(
            direction=SyncDirection.BIDIRECTIONAL,
            frequency="real_time",
            last_sync=datetime.now() - timedelta(minutes=5),
            data_mappings=[
                DataMapping(source_field="phone", target_field="Phone", required=True),
                DataMapping(source_field="email", target_field="Email", required=True),
                DataMapping(source_field="company", target_field="Company", default_value="Unknown")
            ]
        ),
        api_endpoint="https://vocelio-dev.my.salesforce.com/services/data/v57.0/",
        created_by="admin@vocelio.com",
        last_activity=datetime.now() - timedelta(minutes=2),
        success_count=1247,
        error_count=12,
        tags=["production", "crm", "primary"]
    ),
    Integration(
        name="Marketing Automation",
        description="HubSpot integration for marketing campaigns",
        type=IntegrationType.MARKETING,
        provider="hubspot",
        status=IntegrationStatus.ACTIVE,
        auth_config=AuthConfig(
            auth_type=AuthType.API_KEY,
            credentials={"api_key": "pat-na1-demo-key"}
        ),
        sync_config=SyncConfig(
            direction=SyncDirection.OUTBOUND,
            frequency="hourly",
            last_sync=datetime.now() - timedelta(hours=1),
            data_mappings=[
                DataMapping(source_field="call_outcome", target_field="last_call_result"),
                DataMapping(source_field="call_duration", target_field="call_duration_seconds"),
                DataMapping(source_field="lead_score", target_field="hs_lead_score")
            ]
        ),
        api_endpoint="https://api.hubapi.com/",
        created_by="marketing@vocelio.com",
        last_activity=datetime.now() - timedelta(minutes=45),
        success_count=892,
        error_count=5,
        tags=["marketing", "automation", "leads"]
    ),
    Integration(
        name="Call Analytics Export",
        description="Export call data to Google Analytics for tracking",
        type=IntegrationType.ANALYTICS,
        provider="google_analytics",
        status=IntegrationStatus.ACTIVE,
        auth_config=AuthConfig(
            auth_type=AuthType.OAUTH2,
            oauth_config={
                "client_id": "google-demo-id",
                "access_token": "ya29.demo-token"
            }
        ),
        sync_config=SyncConfig(
            direction=SyncDirection.OUTBOUND,
            frequency="daily",
            last_sync=datetime.now() - timedelta(hours=8)
        ),
        api_endpoint="https://analyticsreporting.googleapis.com/v4/",
        created_by="analytics@vocelio.com",
        last_activity=datetime.now() - timedelta(hours=8),
        success_count=156,
        error_count=2,
        tags=["analytics", "reporting", "google"]
    )
]

# Global storage
integrations: List[Integration] = []
templates: List[IntegrationTemplate] = []
webhook_events: List[WebhookEvent] = []
data_syncs: List[DataSync] = []
api_calls: List[APICall] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global integrations, templates
    
    integrations.extend(SAMPLE_INTEGRATIONS)
    templates.extend(SAMPLE_TEMPLATES)
    
    logger.info("Sample integration data initialized successfully")

async def verify_webhook_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify webhook signature for security"""
    try:
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    except Exception as e:
        logger.error(f"Webhook signature verification failed: {str(e)}")
        return False

async def make_api_call(integration: Integration, method: str, endpoint: str, 
                       payload: Optional[Dict[str, Any]] = None) -> APICall:
    """Make an API call to an integrated service"""
    call = APICall(
        integration_id=integration.id,
        method=method,
        endpoint=endpoint,
        payload=payload
    )
    
    try:
        # Prepare headers
        headers = integration.auth_config.headers.copy()
        
        if integration.auth_config.auth_type == AuthType.API_KEY:
            api_key = integration.auth_config.credentials.get("api_key")
            headers["Authorization"] = f"Bearer {api_key}"
        elif integration.auth_config.auth_type == AuthType.BEARER_TOKEN:
            token = integration.auth_config.credentials.get("token")
            headers["Authorization"] = f"Bearer {token}"
        elif integration.auth_config.auth_type == AuthType.BASIC_AUTH:
            username = integration.auth_config.credentials.get("username")
            password = integration.auth_config.credentials.get("password")
            credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
            headers["Authorization"] = f"Basic {credentials}"
        
        # Make the API call
        start_time = datetime.now()
        
        async with httpx.AsyncClient(timeout=integration.sync_config.timeout_seconds) as client:
            if method.upper() == "GET":
                response = await client.get(endpoint, headers=headers)
            elif method.upper() == "POST":
                response = await client.post(endpoint, headers=headers, json=payload)
            elif method.upper() == "PUT":
                response = await client.put(endpoint, headers=headers, json=payload)
            elif method.upper() == "DELETE":
                response = await client.delete(endpoint, headers=headers)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        
        duration = (datetime.now() - start_time).total_seconds() * 1000
        
        call.response_status = response.status_code
        call.duration_ms = duration
        call.success = response.is_success
        
        if response.is_success:
            call.response_data = response.json() if response.content else {}
            integration.success_count += 1
        else:
            call.error_message = f"HTTP {response.status_code}: {response.text}"
            integration.error_count += 1
            
    except Exception as e:
        call.error_message = str(e)
        call.success = False
        integration.error_count += 1
        logger.error(f"API call failed for integration {integration.id}: {str(e)}")
    
    api_calls.append(call)
    integration.last_activity = datetime.now()
    
    return call

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    yield
    
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="Integrations Service",
    description="CRM connections, API integrations, webhooks, and third-party platform connectivity for Vocelio AI Call Center",
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
        "service": "integrations",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Integration Management Endpoints
@app.get("/integrations", response_model=List[Integration])
async def get_integrations(
    type: Optional[IntegrationType] = None,
    provider: Optional[str] = None,
    status: Optional[IntegrationStatus] = None,
    search: Optional[str] = None
):
    """Get all integrations with optional filtering"""
    filtered_integrations = integrations
    
    if type:
        filtered_integrations = [i for i in filtered_integrations if i.type == type]
    
    if provider:
        filtered_integrations = [i for i in filtered_integrations if i.provider.lower() == provider.lower()]
    
    if status:
        filtered_integrations = [i for i in filtered_integrations if i.status == status]
    
    if search:
        search_lower = search.lower()
        filtered_integrations = [
            i for i in filtered_integrations
            if search_lower in i.name.lower() or search_lower in i.description.lower()
        ]
    
    return filtered_integrations

@app.get("/integrations/{integration_id}", response_model=Integration)
async def get_integration(integration_id: str):
    """Get a specific integration by ID"""
    integration = next((i for i in integrations if i.id == integration_id), None)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    return integration

@app.post("/integrations", response_model=Integration)
async def create_integration(integration_data: Integration):
    """Create a new integration"""
    integrations.append(integration_data)
    logger.info(f"Created new integration: {integration_data.name}")
    return integration_data

@app.put("/integrations/{integration_id}", response_model=Integration)
async def update_integration(integration_id: str, integration_data: Integration):
    """Update an existing integration"""
    integration = next((i for i in integrations if i.id == integration_id), None)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Update fields
    for field, value in integration_data.dict(exclude_unset=True).items():
        if field != "id":  # Don't update ID
            setattr(integration, field, value)
    
    integration.updated_at = datetime.now()
    logger.info(f"Updated integration: {integration.name}")
    return integration

@app.delete("/integrations/{integration_id}")
async def delete_integration(integration_id: str):
    """Delete an integration"""
    global integrations
    integration = next((i for i in integrations if i.id == integration_id), None)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    integrations = [i for i in integrations if i.id != integration_id]
    logger.info(f"Deleted integration: {integration.name}")
    return {"message": "Integration deleted successfully"}

# Integration Control Endpoints
@app.post("/integrations/{integration_id}/activate")
async def activate_integration(integration_id: str):
    """Activate an integration"""
    integration = next((i for i in integrations if i.id == integration_id), None)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    integration.status = IntegrationStatus.ACTIVE
    integration.updated_at = datetime.now()
    
    logger.info(f"Activated integration: {integration.name}")
    return {"message": "Integration activated successfully"}

@app.post("/integrations/{integration_id}/deactivate")
async def deactivate_integration(integration_id: str):
    """Deactivate an integration"""
    integration = next((i for i in integrations if i.id == integration_id), None)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    integration.status = IntegrationStatus.INACTIVE
    integration.updated_at = datetime.now()
    
    logger.info(f"Deactivated integration: {integration.name}")
    return {"message": "Integration deactivated successfully"}

@app.post("/integrations/{integration_id}/test")
async def test_integration(integration_id: str):
    """Test an integration connection"""
    integration = next((i for i in integrations if i.id == integration_id), None)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Use test endpoint if available, otherwise use main endpoint
    test_endpoint = integration.auth_config.test_endpoint or integration.api_endpoint
    
    try:
        call = await make_api_call(integration, "GET", test_endpoint)
        
        if call.success:
            integration.status = IntegrationStatus.ACTIVE
            return {
                "success": True,
                "message": "Integration test successful",
                "response_time_ms": call.duration_ms,
                "status_code": call.response_status
            }
        else:
            integration.status = IntegrationStatus.ERROR
            return {
                "success": False,
                "message": "Integration test failed",
                "error": call.error_message,
                "status_code": call.response_status
            }
    except Exception as e:
        integration.status = IntegrationStatus.ERROR
        logger.error(f"Integration test failed: {str(e)}")
        return {
            "success": False,
            "message": "Integration test failed",
            "error": str(e)
        }

# Template Management Endpoints
@app.get("/templates", response_model=List[IntegrationTemplate])
async def get_templates(
    type: Optional[IntegrationType] = None,
    provider: Optional[str] = None,
    difficulty: Optional[str] = None
):
    """Get all integration templates with optional filtering"""
    filtered_templates = templates
    
    if type:
        filtered_templates = [t for t in filtered_templates if t.type == type]
    
    if provider:
        filtered_templates = [t for t in filtered_templates if t.provider.lower() == provider.lower()]
    
    if difficulty:
        filtered_templates = [t for t in filtered_templates if t.setup_difficulty == difficulty]
    
    return filtered_templates

@app.get("/templates/{template_id}", response_model=IntegrationTemplate)
async def get_template(template_id: str):
    """Get a specific integration template by ID"""
    template = next((t for t in templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template

@app.post("/templates/{template_id}/use", response_model=Integration)
async def create_integration_from_template(
    template_id: str, 
    name: str, 
    created_by: str,
    custom_config: Optional[Dict[str, Any]] = None
):
    """Create a new integration from a template"""
    template = next((t for t in templates if t.id == template_id), None)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # Create new integration based on template
    new_integration = Integration(
        name=name,
        description=f"Created from template: {template.name}",
        type=template.type,
        provider=template.provider,
        status=IntegrationStatus.PENDING,
        auth_config=template.template_config.auth_config.copy(),
        sync_config=template.template_config.sync_config.copy(),
        api_endpoint=template.template_config.api_endpoint,
        webhook_url=template.template_config.webhook_url,
        created_by=created_by
    )
    
    # Apply custom configuration if provided
    if custom_config:
        for key, value in custom_config.items():
            if hasattr(new_integration, key):
                setattr(new_integration, key, value)
    
    integrations.append(new_integration)
    template.popularity_score += 0.1  # Increase popularity
    
    logger.info(f"Created integration from template: {name}")
    return new_integration

# Webhook Endpoints
@app.post("/webhooks/{integration_id}")
async def receive_webhook(integration_id: str, payload: Dict[str, Any], headers: Dict[str, str]):
    """Receive webhook events from integrated services"""
    integration = next((i for i in integrations if i.id == integration_id), None)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    # Verify webhook signature if secret is configured
    if integration.auth_config.webhook_secret:
        signature = headers.get("X-Hub-Signature-256") or headers.get("X-Signature")
        if not signature:
            raise HTTPException(status_code=401, detail="Missing webhook signature")
        
        payload_str = json.dumps(payload, sort_keys=True)
        if not await verify_webhook_signature(payload_str, signature, integration.auth_config.webhook_secret):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
    
    # Create webhook event
    event = WebhookEvent(
        integration_id=integration_id,
        event_type=payload.get("event_type", "unknown"),
        payload=payload,
        headers=headers
    )
    
    webhook_events.append(event)
    integration.last_activity = datetime.now()
    
    logger.info(f"Received webhook event for integration {integration.name}")
    return {"message": "Webhook received successfully", "event_id": event.id}

@app.get("/webhooks/{integration_id}/events", response_model=List[WebhookEvent])
async def get_webhook_events(integration_id: str, limit: int = 50):
    """Get recent webhook events for an integration"""
    events = [e for e in webhook_events if e.integration_id == integration_id]
    events.sort(key=lambda x: x.received_at, reverse=True)
    return events[:limit]

# Data Sync Endpoints
@app.post("/integrations/{integration_id}/sync")
async def trigger_sync(integration_id: str, entity_type: str, background_tasks: BackgroundTasks):
    """Trigger a data sync for an integration"""
    integration = next((i for i in integrations if i.id == integration_id), None)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    if integration.status != IntegrationStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Integration is not active")
    
    # Add background task for sync
    background_tasks.add_task(perform_data_sync, integration, entity_type)
    
    return {"message": f"Sync triggered for {entity_type}", "integration": integration.name}

async def perform_data_sync(integration: Integration, entity_type: str):
    """Perform actual data synchronization"""
    try:
        logger.info(f"Starting sync for {integration.name} - {entity_type}")
        
        # Mock sync process
        sync = DataSync(
            integration_id=integration.id,
            direction=integration.sync_config.direction,
            entity_type=entity_type,
            source_id=f"sync_{uuid.uuid4()}",
            data={"entity_type": entity_type, "sync_timestamp": datetime.now().isoformat()}
        )
        
        # Simulate API calls and data processing
        await asyncio.sleep(2)  # Simulate processing time
        
        sync.status = "synced"
        sync.completed_at = datetime.now()
        sync.target_id = f"target_{uuid.uuid4()}"
        
        data_syncs.append(sync)
        integration.sync_config.last_sync = datetime.now()
        integration.success_count += 1
        
        logger.info(f"Sync completed for {integration.name} - {entity_type}")
        
    except Exception as e:
        logger.error(f"Sync failed for {integration.name}: {str(e)}")
        sync.status = "failed"
        sync.error_message = str(e)
        sync.completed_at = datetime.now()
        data_syncs.append(sync)
        integration.error_count += 1

@app.get("/integrations/{integration_id}/syncs", response_model=List[DataSync])
async def get_sync_history(integration_id: str, limit: int = 50):
    """Get sync history for an integration"""
    syncs = [s for s in data_syncs if s.integration_id == integration_id]
    syncs.sort(key=lambda x: x.started_at, reverse=True)
    return syncs[:limit]

# API Call Monitoring Endpoints
@app.get("/integrations/{integration_id}/api-calls", response_model=List[APICall])
async def get_api_calls(integration_id: str, limit: int = 100):
    """Get recent API calls for an integration"""
    calls = [c for c in api_calls if c.integration_id == integration_id]
    calls.sort(key=lambda x: x.timestamp, reverse=True)
    return calls[:limit]

@app.get("/integrations/{integration_id}/analytics")
async def get_integration_analytics(integration_id: str):
    """Get analytics and metrics for an integration"""
    integration = next((i for i in integrations if i.id == integration_id), None)
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    
    integration_calls = [c for c in api_calls if c.integration_id == integration_id]
    integration_syncs = [s for s in data_syncs if s.integration_id == integration_id]
    integration_webhooks = [w for w in webhook_events if w.integration_id == integration_id]
    
    # Calculate metrics
    total_calls = len(integration_calls)
    successful_calls = len([c for c in integration_calls if c.success])
    failed_calls = total_calls - successful_calls
    
    avg_response_time = 0
    if integration_calls:
        response_times = [c.duration_ms for c in integration_calls if c.duration_ms]
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
    
    # Recent activity
    recent_activity = []
    for call in integration_calls[-10:]:
        recent_activity.append({
            "type": "api_call",
            "timestamp": call.timestamp,
            "success": call.success,
            "method": call.method,
            "endpoint": call.endpoint
        })
    
    return {
        "integration_id": integration_id,
        "integration_name": integration.name,
        "status": integration.status,
        "total_api_calls": total_calls,
        "successful_calls": successful_calls,
        "failed_calls": failed_calls,
        "success_rate": round(success_rate, 2),
        "average_response_time_ms": round(avg_response_time, 2),
        "total_syncs": len(integration_syncs),
        "successful_syncs": len([s for s in integration_syncs if s.status == "synced"]),
        "total_webhooks": len(integration_webhooks),
        "last_activity": integration.last_activity,
        "recent_activity": recent_activity,
        "uptime_percentage": 98.5,  # Mock uptime
        "data_volume": {
            "records_synced_today": 1247,
            "api_calls_today": 342,
            "webhooks_today": 89
        }
    }

# Bulk Operations Endpoints
@app.post("/integrations/bulk-sync")
async def bulk_sync(integration_ids: List[str], entity_type: str, background_tasks: BackgroundTasks):
    """Trigger sync for multiple integrations"""
    valid_integrations = []
    
    for integration_id in integration_ids:
        integration = next((i for i in integrations if i.id == integration_id), None)
        if integration and integration.status == IntegrationStatus.ACTIVE:
            valid_integrations.append(integration)
    
    if not valid_integrations:
        raise HTTPException(status_code=400, detail="No valid active integrations found")
    
    # Add background tasks for each integration
    for integration in valid_integrations:
        background_tasks.add_task(perform_data_sync, integration, entity_type)
    
    return {
        "message": f"Bulk sync triggered for {len(valid_integrations)} integrations",
        "entity_type": entity_type,
        "integrations": [i.name for i in valid_integrations]
    }

@app.get("/analytics/overview")
async def get_integrations_overview():
    """Get overall integration analytics and metrics"""
    total_integrations = len(integrations)
    active_integrations = len([i for i in integrations if i.status == IntegrationStatus.ACTIVE])
    error_integrations = len([i for i in integrations if i.status == IntegrationStatus.ERROR])
    
    # Integration types breakdown
    type_breakdown = {}
    for integration_type in IntegrationType:
        count = len([i for i in integrations if i.type == integration_type])
        if count > 0:
            type_breakdown[integration_type.value] = count
    
    # Provider popularity
    provider_stats = {}
    for integration in integrations:
        provider = integration.provider
        if provider not in provider_stats:
            provider_stats[provider] = {"total": 0, "active": 0}
        provider_stats[provider]["total"] += 1
        if integration.status == IntegrationStatus.ACTIVE:
            provider_stats[provider]["active"] += 1
    
    # Recent activity
    recent_syncs = len([s for s in data_syncs if s.started_at > datetime.now() - timedelta(hours=24)])
    recent_webhooks = len([w for w in webhook_events if w.received_at > datetime.now() - timedelta(hours=24)])
    recent_api_calls = len([c for c in api_calls if c.timestamp > datetime.now() - timedelta(hours=24)])
    
    return {
        "total_integrations": total_integrations,
        "active_integrations": active_integrations,
        "inactive_integrations": total_integrations - active_integrations - error_integrations,
        "error_integrations": error_integrations,
        "health_percentage": round((active_integrations / total_integrations * 100) if total_integrations > 0 else 0, 1),
        "integration_types": type_breakdown,
        "provider_stats": provider_stats,
        "activity_24h": {
            "syncs": recent_syncs,
            "webhooks": recent_webhooks,
            "api_calls": recent_api_calls
        },
        "performance_metrics": {
            "average_response_time_ms": 245.7,
            "success_rate_percentage": 96.8,
            "uptime_percentage": 99.2
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8010)