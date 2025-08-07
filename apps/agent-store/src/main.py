"""
Agent Store Service - Vocelio AI Call Center
AI agent marketplace with specialized agents for different industries and use cases
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
from enum import Enum
import uuid
import asyncio
import json
import logging
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Agent Store Models
class AgentCategory(str, Enum):
    SALES = "sales"
    CUSTOMER_SERVICE = "customer_service"
    LEAD_QUALIFICATION = "lead_qualification"
    APPOINTMENT_SETTING = "appointment_setting"
    DEBT_COLLECTION = "debt_collection"
    SURVEYS = "surveys"
    TECHNICAL_SUPPORT = "technical_support"
    HEALTHCARE = "healthcare"
    REAL_ESTATE = "real_estate"
    INSURANCE = "insurance"
    AUTOMOTIVE = "automotive"
    FINANCE = "finance"
    EDUCATION = "education"
    LEGAL = "legal"
    HOSPITALITY = "hospitality"
    RETAIL = "retail"
    LOGISTICS = "logistics"
    UTILITIES = "utilities"
    GOVERNMENT = "government"
    NON_PROFIT = "non_profit"

class AgentComplexity(str, Enum):
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    ENTERPRISE = "enterprise"

class AgentStatus(str, Enum):
    ACTIVE = "active"
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    DEPRECATED = "deprecated"
    SUSPENDED = "suspended"

class LicenseType(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

class DeploymentType(str, Enum):
    CLOUD = "cloud"
    ON_PREMISE = "on_premise"
    HYBRID = "hybrid"

class AgentCapability(BaseModel):
    name: str
    description: str
    enabled: bool = True
    configuration: Dict[str, Any] = {}

class AgentPersonality(BaseModel):
    tone: str = "professional"  # "professional", "friendly", "authoritative", "empathetic"
    communication_style: str = "formal"  # "formal", "casual", "conversational"
    energy_level: str = "balanced"  # "low", "balanced", "high", "enthusiastic"
    patience_level: str = "high"  # "low", "medium", "high", "unlimited"
    assertiveness: str = "moderate"  # "passive", "moderate", "assertive", "aggressive"
    humor_usage: bool = False
    empathy_level: str = "high"  # "low", "medium", "high", "very_high"
    technical_depth: str = "adaptive"  # "basic", "intermediate", "advanced", "adaptive"

class AgentKnowledgeBase(BaseModel):
    industry_expertise: List[str] = []
    product_knowledge: List[str] = []
    compliance_requirements: List[str] = []
    faq_coverage: Dict[str, str] = {}
    training_documents: List[str] = []
    api_integrations: List[str] = []

class AgentMetrics(BaseModel):
    total_downloads: int = 0
    active_deployments: int = 0
    average_rating: float = 0.0
    total_reviews: int = 0
    success_rate: float = 0.0
    average_call_duration: float = 0.0
    conversion_rate: float = 0.0
    customer_satisfaction: float = 0.0
    resolution_rate: float = 0.0

class AgentPricing(BaseModel):
    license_type: LicenseType
    base_price: Decimal = Decimal("0.00")
    per_call_price: Decimal = Decimal("0.00")
    per_minute_price: Decimal = Decimal("0.00")
    monthly_subscription: Decimal = Decimal("0.00")
    setup_fee: Decimal = Decimal("0.00")
    support_included: bool = False
    trial_period_days: int = 0
    bulk_discount_threshold: int = 1000
    bulk_discount_percentage: float = 0.0

class Agent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    display_name: str
    description: str
    detailed_description: str
    category: AgentCategory
    subcategories: List[str] = []
    complexity: AgentComplexity
    status: AgentStatus
    version: str = "1.0.0"
    
    # Creator and ownership
    created_by: str
    organization: str
    verified_creator: bool = False
    official_agent: bool = False
    
    # Technical specifications
    capabilities: List[AgentCapability] = []
    personality: AgentPersonality = Field(default_factory=AgentPersonality)
    knowledge_base: AgentKnowledgeBase = Field(default_factory=AgentKnowledgeBase)
    supported_languages: List[str] = ["en-US"]
    supported_channels: List[str] = ["voice", "chat", "sms"]
    
    # Deployment and integration
    deployment_types: List[DeploymentType] = [DeploymentType.CLOUD]
    required_integrations: List[str] = []
    optional_integrations: List[str] = []
    custom_fields: Dict[str, Any] = {}
    
    # Performance and quality
    metrics: AgentMetrics = Field(default_factory=AgentMetrics)
    pricing: AgentPricing = Field(default_factory=AgentPricing)
    
    # Metadata
    tags: List[str] = []
    keywords: List[str] = []
    demo_available: bool = False
    demo_url: Optional[str] = None
    documentation_url: Optional[str] = None
    support_url: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    published_at: Optional[datetime] = None
    
    # Media and assets
    icon_url: Optional[str] = None
    banner_url: Optional[str] = None
    screenshots: List[str] = []
    video_demo_url: Optional[str] = None

class AgentReview(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    reviewer_id: str
    reviewer_name: str
    rating: float = Field(ge=1.0, le=5.0)
    title: str
    review_text: str
    pros: List[str] = []
    cons: List[str] = []
    use_case: str
    deployment_type: DeploymentType
    verified_purchase: bool = False
    helpful_votes: int = 0
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class AgentDeployment(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    user_id: str
    organization_id: str
    deployment_name: str
    deployment_type: DeploymentType
    configuration: Dict[str, Any] = {}
    custom_personality: Optional[AgentPersonality] = None
    custom_knowledge: Dict[str, Any] = {}
    
    # Status and monitoring
    status: str = "active"  # "active", "paused", "stopped", "failed"
    health_status: str = "healthy"  # "healthy", "warning", "critical"
    last_activity: Optional[datetime] = None
    
    # Usage metrics
    total_calls: int = 0
    total_minutes: float = 0.0
    success_rate: float = 0.0
    average_rating: float = 0.0
    
    # Billing
    current_usage_cost: Decimal = Decimal("0.00")
    monthly_cost: Decimal = Decimal("0.00")
    
    # Timestamps
    deployed_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)

class AgentMarketplace(BaseModel):
    featured_agents: List[str] = []
    trending_agents: List[str] = []
    new_agents: List[str] = []
    top_rated_agents: List[str] = []
    most_downloaded: List[str] = []
    categories: Dict[AgentCategory, int] = {}
    total_agents: int = 0
    total_downloads: int = 0
    average_rating: float = 0.0

class AgentAnalytics(BaseModel):
    agent_id: str
    time_period: str  # "24h", "7d", "30d", "90d"
    
    # Usage metrics
    total_calls: int
    total_minutes: float
    unique_users: int
    success_rate: float
    error_rate: float
    
    # Performance metrics
    average_response_time: float
    average_call_duration: float
    conversion_rate: float
    customer_satisfaction: float
    
    # Revenue metrics
    total_revenue: Decimal
    revenue_per_call: Decimal
    revenue_per_user: Decimal
    
    # Trend data
    daily_usage: List[Dict[str, Any]] = []
    hourly_distribution: Dict[str, int] = {}
    geographic_distribution: Dict[str, int] = {}
    
    # Quality metrics
    rating_distribution: Dict[str, int] = {}
    common_issues: List[Dict[str, Any]] = []
    improvement_suggestions: List[str] = []

# Sample agents data
SAMPLE_AGENTS = [
    Agent(
        name="sales_pro_elite",
        display_name="SalesPro Elite",
        description="Advanced sales agent specialized in B2B lead qualification and conversion",
        detailed_description="SalesPro Elite is a sophisticated AI sales agent designed for high-value B2B sales processes. It excels at lead qualification, objection handling, and deal progression through complex sales funnels.",
        category=AgentCategory.SALES,
        subcategories=["b2b", "enterprise", "lead_qualification"],
        complexity=AgentComplexity.ADVANCED,
        status=AgentStatus.ACTIVE,
        created_by="vocelio_official",
        organization="Vocelio",
        verified_creator=True,
        official_agent=True,
        capabilities=[
            AgentCapability(name="lead_qualification", description="Advanced lead scoring and qualification"),
            AgentCapability(name="objection_handling", description="Intelligent objection resolution"),
            AgentCapability(name="crm_integration", description="Seamless CRM data synchronization"),
            AgentCapability(name="follow_up_scheduling", description="Automated follow-up coordination")
        ],
        personality=AgentPersonality(
            tone="professional",
            communication_style="conversational",
            energy_level="balanced",
            assertiveness="moderate",
            technical_depth="adaptive"
        ),
        knowledge_base=AgentKnowledgeBase(
            industry_expertise=["technology", "finance", "healthcare", "manufacturing"],
            product_knowledge=["saas", "enterprise_software", "consulting"],
            compliance_requirements=["gdpr", "ccpa", "do_not_call"],
            api_integrations=["salesforce", "hubspot", "pipedrive"]
        ),
        metrics=AgentMetrics(
            total_downloads=2847,
            active_deployments=1205,
            average_rating=4.8,
            total_reviews=156,
            success_rate=87.3,
            conversion_rate=23.7,
            customer_satisfaction=4.6
        ),
        pricing=AgentPricing(
            license_type=LicenseType.PROFESSIONAL,
            per_call_price=Decimal("2.50"),
            monthly_subscription=Decimal("299.00"),
            trial_period_days=14,
            support_included=True
        ),
        tags=["sales", "b2b", "lead_qualification", "crm", "enterprise"],
        demo_available=True,
        published_at=datetime.now() - timedelta(days=45)
    ),
    Agent(
        name="support_specialist",
        display_name="Support Specialist",
        description="Empathetic customer support agent with advanced problem resolution capabilities",
        detailed_description="Support Specialist provides exceptional customer service with natural language understanding, emotional intelligence, and comprehensive knowledge base integration for rapid issue resolution.",
        category=AgentCategory.CUSTOMER_SERVICE,
        subcategories=["technical_support", "general_inquiries", "billing"],
        complexity=AgentComplexity.INTERMEDIATE,
        status=AgentStatus.ACTIVE,
        created_by="vocelio_official",
        organization="Vocelio",
        verified_creator=True,
        official_agent=True,
        capabilities=[
            AgentCapability(name="ticket_management", description="Automated ticket creation and tracking"),
            AgentCapability(name="knowledge_search", description="Intelligent knowledge base queries"),
            AgentCapability(name="escalation_management", description="Smart escalation to human agents"),
            AgentCapability(name="sentiment_analysis", description="Real-time emotion detection")
        ],
        personality=AgentPersonality(
            tone="empathetic",
            communication_style="conversational",
            energy_level="balanced",
            patience_level="unlimited",
            empathy_level="very_high"
        ),
        knowledge_base=AgentKnowledgeBase(
            industry_expertise=["technology", "retail", "telecommunications"],
            compliance_requirements=["accessibility", "privacy"],
            api_integrations=["zendesk", "freshdesk", "intercom"]
        ),
        metrics=AgentMetrics(
            total_downloads=4201,
            active_deployments=2156,
            average_rating=4.7,
            total_reviews=298,
            success_rate=91.2,
            resolution_rate=84.6,
            customer_satisfaction=4.5
        ),
        pricing=AgentPricing(
            license_type=LicenseType.BASIC,
            per_call_price=Decimal("1.75"),
            monthly_subscription=Decimal("199.00"),
            trial_period_days=30,
            support_included=True
        ),
        tags=["support", "customer_service", "empathy", "resolution"],
        demo_available=True,
        published_at=datetime.now() - timedelta(days=60)
    ),
    Agent(
        name="healthcare_navigator",
        display_name="Healthcare Navigator",
        description="HIPAA-compliant healthcare assistant for appointment scheduling and patient support",
        detailed_description="Healthcare Navigator is designed specifically for healthcare organizations, providing HIPAA-compliant patient interactions, appointment scheduling, prescription reminders, and basic health information assistance.",
        category=AgentCategory.HEALTHCARE,
        subcategories=["appointments", "patient_support", "insurance"],
        complexity=AgentComplexity.EXPERT,
        status=AgentStatus.ACTIVE,
        created_by="medical_ai_solutions",
        organization="Medical AI Solutions Inc.",
        verified_creator=True,
        official_agent=False,
        capabilities=[
            AgentCapability(name="hipaa_compliance", description="Full HIPAA compliance and security"),
            AgentCapability(name="appointment_scheduling", description="Intelligent scheduling optimization"),
            AgentCapability(name="insurance_verification", description="Real-time insurance eligibility checks"),
            AgentCapability(name="medication_reminders", description="Automated prescription reminders")
        ],
        personality=AgentPersonality(
            tone="professional",
            communication_style="formal",
            energy_level="balanced",
            patience_level="unlimited",
            empathy_level="very_high",
            technical_depth="advanced"
        ),
        knowledge_base=AgentKnowledgeBase(
            industry_expertise=["healthcare", "medical_billing", "insurance"],
            compliance_requirements=["hipaa", "hitech", "medical_privacy"],
            api_integrations=["epic", "cerner", "allscripts", "athenahealth"]
        ),
        metrics=AgentMetrics(
            total_downloads=892,
            active_deployments=234,
            average_rating=4.9,
            total_reviews=67,
            success_rate=94.1,
            customer_satisfaction=4.8
        ),
        pricing=AgentPricing(
            license_type=LicenseType.ENTERPRISE,
            monthly_subscription=Decimal("899.00"),
            setup_fee=Decimal("2500.00"),
            trial_period_days=7,
            support_included=True
        ),
        tags=["healthcare", "hipaa", "appointments", "medical", "compliance"],
        demo_available=False,
        published_at=datetime.now() - timedelta(days=30)
    )
]

# Global storage
agents: List[Agent] = []
reviews: List[AgentReview] = []
deployments: List[AgentDeployment] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global agents
    
    agents.extend(SAMPLE_AGENTS)
    
    # Add sample reviews
    sample_reviews = [
        AgentReview(
            agent_id=agents[0].id,
            reviewer_id="user_001",
            reviewer_name="John Smith",
            rating=5.0,
            title="Excellent sales performance",
            review_text="This agent has significantly improved our lead qualification process. Highly recommended!",
            pros=["Great conversion rates", "Professional communication", "Easy integration"],
            cons=["Could use more customization options"],
            use_case="B2B lead qualification",
            deployment_type=DeploymentType.CLOUD,
            verified_purchase=True,
            helpful_votes=23
        ),
        AgentReview(
            agent_id=agents[1].id,
            reviewer_id="user_002",
            reviewer_name="Sarah Johnson",
            rating=4.5,
            title="Great customer support agent",
            review_text="Our customer satisfaction scores improved after deploying this agent.",
            pros=["Empathetic responses", "Quick resolution", "Good knowledge base"],
            cons=["Sometimes needs human escalation"],
            use_case="Customer support",
            deployment_type=DeploymentType.CLOUD,
            verified_purchase=True,
            helpful_votes=18
        )
    ]
    
    reviews.extend(sample_reviews)
    
    logger.info("Sample agent store data initialized successfully")

async def calculate_agent_metrics(agent_id: str) -> AgentMetrics:
    """Calculate real-time metrics for an agent"""
    agent_reviews = [r for r in reviews if r.agent_id == agent_id]
    agent_deployments = [d for d in deployments if d.agent_id == agent_id]
    
    if agent_reviews:
        average_rating = sum(r.rating for r in agent_reviews) / len(agent_reviews)
    else:
        average_rating = 0.0
    
    active_deployments = len([d for d in agent_deployments if d.status == "active"])
    
    # Mock additional metrics
    total_calls = sum(d.total_calls for d in agent_deployments)
    total_minutes = sum(d.total_minutes for d in agent_deployments)
    
    return AgentMetrics(
        total_downloads=len(agent_deployments) + 100,  # Mock base downloads
        active_deployments=active_deployments,
        average_rating=round(average_rating, 1),
        total_reviews=len(agent_reviews),
        success_rate=85.0 + (hash(agent_id) % 15),  # Mock success rate
        average_call_duration=total_minutes / total_calls if total_calls > 0 else 0,
        conversion_rate=20.0 + (hash(agent_id) % 20),  # Mock conversion rate
        customer_satisfaction=4.0 + (hash(agent_id) % 10) / 10  # Mock satisfaction
    )

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    yield
    
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="Agent Store Service",
    description="AI agent marketplace with specialized agents for different industries and use cases for Vocelio AI Call Center",
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
        "service": "agent-store",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Agent Marketplace Endpoints
@app.get("/marketplace", response_model=AgentMarketplace)
async def get_marketplace_overview():
    """Get marketplace overview with featured and trending agents"""
    
    # Calculate category distribution
    category_counts = {}
    for category in AgentCategory:
        count = len([a for a in agents if a.category == category])
        if count > 0:
            category_counts[category] = count
    
    # Sort agents by different criteria
    featured_agents = [a.id for a in sorted(agents, key=lambda x: x.metrics.average_rating, reverse=True)[:3]]
    trending_agents = [a.id for a in sorted(agents, key=lambda x: x.metrics.total_downloads, reverse=True)[:3]]
    new_agents = [a.id for a in sorted(agents, key=lambda x: x.published_at or datetime.min, reverse=True)[:3]]
    top_rated = [a.id for a in sorted(agents, key=lambda x: x.metrics.average_rating, reverse=True)[:5]]
    most_downloaded = [a.id for a in sorted(agents, key=lambda x: x.metrics.total_downloads, reverse=True)[:5]]
    
    total_downloads = sum(a.metrics.total_downloads for a in agents)
    average_rating = sum(a.metrics.average_rating for a in agents) / len(agents) if agents else 0
    
    return AgentMarketplace(
        featured_agents=featured_agents,
        trending_agents=trending_agents,
        new_agents=new_agents,
        top_rated_agents=top_rated,
        most_downloaded=most_downloaded,
        categories=category_counts,
        total_agents=len(agents),
        total_downloads=total_downloads,
        average_rating=round(average_rating, 1)
    )

@app.get("/agents", response_model=List[Agent])
async def get_agents(
    category: Optional[AgentCategory] = None,
    complexity: Optional[AgentComplexity] = None,
    license_type: Optional[LicenseType] = None,
    verified_only: Optional[bool] = None,
    official_only: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = "rating",  # "rating", "downloads", "name", "created", "price"
    limit: int = 20,
    offset: int = 0
):
    """Get agents with filtering and sorting options"""
    
    filtered_agents = agents.copy()
    
    # Apply filters
    if category:
        filtered_agents = [a for a in filtered_agents if a.category == category]
    
    if complexity:
        filtered_agents = [a for a in filtered_agents if a.complexity == complexity]
    
    if license_type:
        filtered_agents = [a for a in filtered_agents if a.pricing.license_type == license_type]
    
    if verified_only:
        filtered_agents = [a for a in filtered_agents if a.verified_creator]
    
    if official_only:
        filtered_agents = [a for a in filtered_agents if a.official_agent]
    
    if search:
        search_lower = search.lower()
        filtered_agents = [
            a for a in filtered_agents
            if (search_lower in a.name.lower() or 
                search_lower in a.display_name.lower() or
                search_lower in a.description.lower() or
                any(search_lower in tag.lower() for tag in a.tags))
        ]
    
    # Apply sorting
    if sort_by == "rating":
        filtered_agents.sort(key=lambda x: x.metrics.average_rating, reverse=True)
    elif sort_by == "downloads":
        filtered_agents.sort(key=lambda x: x.metrics.total_downloads, reverse=True)
    elif sort_by == "name":
        filtered_agents.sort(key=lambda x: x.display_name.lower())
    elif sort_by == "created":
        filtered_agents.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == "price":
        filtered_agents.sort(key=lambda x: float(x.pricing.monthly_subscription))
    
    # Apply pagination
    return filtered_agents[offset:offset + limit]

@app.get("/agents/{agent_id}", response_model=Agent)
async def get_agent(agent_id: str):
    """Get detailed information about a specific agent"""
    agent = next((a for a in agents if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update metrics with real-time data
    agent.metrics = await calculate_agent_metrics(agent_id)
    return agent

@app.post("/agents", response_model=Agent)
async def create_agent(agent_data: Agent):
    """Create a new agent (for verified creators)"""
    # In production, this would require authentication and creator verification
    agents.append(agent_data)
    logger.info(f"Created new agent: {agent_data.display_name}")
    return agent_data

@app.put("/agents/{agent_id}", response_model=Agent)
async def update_agent(agent_id: str, agent_data: Agent):
    """Update an existing agent"""
    agent = next((a for a in agents if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Update fields
    for field, value in agent_data.dict(exclude_unset=True).items():
        if field != "id":
            setattr(agent, field, value)
    
    agent.updated_at = datetime.now()
    logger.info(f"Updated agent: {agent.display_name}")
    return agent

# Agent Reviews Endpoints
@app.get("/agents/{agent_id}/reviews", response_model=List[AgentReview])
async def get_agent_reviews(
    agent_id: str,
    sort_by: str = "recent",  # "recent", "rating", "helpful"
    limit: int = 20
):
    """Get reviews for a specific agent"""
    agent_reviews = [r for r in reviews if r.agent_id == agent_id]
    
    if sort_by == "recent":
        agent_reviews.sort(key=lambda x: x.created_at, reverse=True)
    elif sort_by == "rating":
        agent_reviews.sort(key=lambda x: x.rating, reverse=True)
    elif sort_by == "helpful":
        agent_reviews.sort(key=lambda x: x.helpful_votes, reverse=True)
    
    return agent_reviews[:limit]

@app.post("/agents/{agent_id}/reviews", response_model=AgentReview)
async def create_review(agent_id: str, review_data: AgentReview):
    """Create a review for an agent"""
    # Verify agent exists
    agent = next((a for a in agents if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    review_data.agent_id = agent_id
    reviews.append(review_data)
    
    # Update agent metrics
    agent.metrics = await calculate_agent_metrics(agent_id)
    
    logger.info(f"Created review for agent: {agent.display_name}")
    return review_data

# Agent Deployment Endpoints
@app.post("/agents/{agent_id}/deploy", response_model=AgentDeployment)
async def deploy_agent(
    agent_id: str,
    deployment_name: str,
    deployment_type: DeploymentType,
    user_id: str,
    organization_id: str,
    configuration: Optional[Dict[str, Any]] = None,
    custom_personality: Optional[AgentPersonality] = None
):
    """Deploy an agent for a user/organization"""
    
    # Verify agent exists
    agent = next((a for a in agents if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Create deployment
    deployment = AgentDeployment(
        agent_id=agent_id,
        user_id=user_id,
        organization_id=organization_id,
        deployment_name=deployment_name,
        deployment_type=deployment_type,
        configuration=configuration or {},
        custom_personality=custom_personality
    )
    
    deployments.append(deployment)
    
    # Update agent metrics
    agent.metrics.active_deployments += 1
    
    logger.info(f"Deployed agent {agent.display_name} for user {user_id}")
    return deployment

@app.get("/deployments", response_model=List[AgentDeployment])
async def get_user_deployments(
    user_id: Optional[str] = None,
    organization_id: Optional[str] = None,
    status: Optional[str] = None
):
    """Get agent deployments for a user or organization"""
    
    filtered_deployments = deployments.copy()
    
    if user_id:
        filtered_deployments = [d for d in filtered_deployments if d.user_id == user_id]
    
    if organization_id:
        filtered_deployments = [d for d in filtered_deployments if d.organization_id == organization_id]
    
    if status:
        filtered_deployments = [d for d in filtered_deployments if d.status == status]
    
    # Sort by deployment date
    filtered_deployments.sort(key=lambda x: x.deployed_at, reverse=True)
    
    return filtered_deployments

@app.get("/deployments/{deployment_id}", response_model=AgentDeployment)
async def get_deployment(deployment_id: str):
    """Get details of a specific deployment"""
    deployment = next((d for d in deployments if d.id == deployment_id), None)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    return deployment

@app.put("/deployments/{deployment_id}/status")
async def update_deployment_status(deployment_id: str, status: str):
    """Update deployment status (start, stop, pause)"""
    deployment = next((d for d in deployments if d.id == deployment_id), None)
    if not deployment:
        raise HTTPException(status_code=404, detail="Deployment not found")
    
    deployment.status = status
    deployment.last_updated = datetime.now()
    
    if status == "active":
        deployment.last_activity = datetime.now()
    
    logger.info(f"Updated deployment {deployment_id} status to {status}")
    return {"message": f"Deployment status updated to {status}"}

# Analytics Endpoints
@app.get("/agents/{agent_id}/analytics", response_model=AgentAnalytics)
async def get_agent_analytics(
    agent_id: str,
    time_period: str = "30d"
):
    """Get analytics for a specific agent"""
    
    agent = next((a for a in agents if a.id == agent_id), None)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent_deployments = [d for d in deployments if d.agent_id == agent_id]
    
    # Calculate metrics
    total_calls = sum(d.total_calls for d in agent_deployments)
    total_minutes = sum(d.total_minutes for d in agent_deployments)
    unique_users = len(set(d.user_id for d in agent_deployments))
    
    # Mock revenue calculation
    total_revenue = Decimal(str(total_calls)) * agent.pricing.per_call_price
    
    # Mock trend data
    daily_usage = [
        {"date": (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d"), 
         "calls": max(0, 50 - i * 2 + (hash(agent_id + str(i)) % 20))}
        for i in range(7, 0, -1)
    ]
    
    return AgentAnalytics(
        agent_id=agent_id,
        time_period=time_period,
        total_calls=total_calls,
        total_minutes=total_minutes,
        unique_users=unique_users,
        success_rate=agent.metrics.success_rate,
        error_rate=100 - agent.metrics.success_rate,
        average_response_time=2.3,  # Mock response time
        average_call_duration=total_minutes / total_calls if total_calls > 0 else 0,
        conversion_rate=agent.metrics.conversion_rate,
        customer_satisfaction=agent.metrics.customer_satisfaction,
        total_revenue=total_revenue,
        revenue_per_call=agent.pricing.per_call_price,
        revenue_per_user=total_revenue / unique_users if unique_users > 0 else Decimal("0"),
        daily_usage=daily_usage,
        hourly_distribution={str(i): max(0, 50 - abs(12 - i) * 3) for i in range(24)},
        geographic_distribution={"US": 65, "CA": 15, "UK": 12, "AU": 8},
        rating_distribution={"5": 45, "4": 30, "3": 15, "2": 7, "1": 3},
        common_issues=[
            {"issue": "Integration timeout", "count": 5, "severity": "medium"},
            {"issue": "Voice quality", "count": 2, "severity": "low"}
        ],
        improvement_suggestions=[
            "Consider adding more training data for edge cases",
            "Optimize response time for complex queries",
            "Add support for additional languages"
        ]
    )

@app.get("/analytics/overview")
async def get_store_analytics():
    """Get overall agent store analytics"""
    
    total_agents = len(agents)
    total_deployments = len(deployments)
    total_reviews = len(reviews)
    
    # Category popularity
    category_popularity = {}
    for agent in agents:
        category = agent.category.value
        category_popularity[category] = category_popularity.get(category, 0) + agent.metrics.total_downloads
    
    # Top performing agents
    top_agents = sorted(agents, key=lambda x: x.metrics.average_rating * x.metrics.total_downloads, reverse=True)[:5]
    
    # Revenue metrics (mock)
    total_revenue = sum(
        float(d.monthly_cost) for d in deployments if d.status == "active"
    )
    
    return {
        "marketplace_metrics": {
            "total_agents": total_agents,
            "total_deployments": total_deployments,
            "total_reviews": total_reviews,
            "average_rating": sum(a.metrics.average_rating for a in agents) / total_agents if total_agents > 0 else 0,
            "total_downloads": sum(a.metrics.total_downloads for a in agents)
        },
        "performance_metrics": {
            "active_deployments": len([d for d in deployments if d.status == "active"]),
            "success_rate": sum(a.metrics.success_rate for a in agents) / total_agents if total_agents > 0 else 0,
            "customer_satisfaction": sum(a.metrics.customer_satisfaction for a in agents) / total_agents if total_agents > 0 else 0
        },
        "revenue_metrics": {
            "monthly_recurring_revenue": total_revenue,
            "average_revenue_per_agent": total_revenue / total_agents if total_agents > 0 else 0,
            "top_revenue_agents": [{"name": a.display_name, "revenue": float(a.pricing.monthly_subscription)} for a in top_agents[:3]]
        },
        "category_popularity": dict(sorted(category_popularity.items(), key=lambda x: x[1], reverse=True)),
        "growth_metrics": {
            "new_agents_this_month": len([a for a in agents if a.created_at > datetime.now() - timedelta(days=30)]),
            "new_deployments_this_month": len([d for d in deployments if d.deployed_at > datetime.now() - timedelta(days=30)]),
            "reviews_this_month": len([r for r in reviews if r.created_at > datetime.now() - timedelta(days=30)])
        }
    }

# Agent Categories Endpoint
@app.get("/categories")
async def get_agent_categories():
    """Get all available agent categories with descriptions"""
    
    category_descriptions = {
        AgentCategory.SALES: "Specialized sales agents for lead generation and conversion",
        AgentCategory.CUSTOMER_SERVICE: "Customer support agents with empathy and problem-solving skills",
        AgentCategory.LEAD_QUALIFICATION: "Agents focused on qualifying and scoring leads",
        AgentCategory.APPOINTMENT_SETTING: "Scheduling and calendar management specialists",
        AgentCategory.DEBT_COLLECTION: "Professional debt recovery and payment reminder agents",
        AgentCategory.SURVEYS: "Survey administration and data collection agents",
        AgentCategory.TECHNICAL_SUPPORT: "Technical troubleshooting and support specialists",
        AgentCategory.HEALTHCARE: "HIPAA-compliant healthcare communication agents",
        AgentCategory.REAL_ESTATE: "Real estate transaction and property inquiry specialists",
        AgentCategory.INSURANCE: "Insurance claim processing and policy information agents",
        AgentCategory.AUTOMOTIVE: "Vehicle sales, service, and support specialists",
        AgentCategory.FINANCE: "Financial services and banking communication agents",
        AgentCategory.EDUCATION: "Educational institution and student service agents",
        AgentCategory.LEGAL: "Legal consultation and document processing specialists",
        AgentCategory.HOSPITALITY: "Hotel, restaurant, and travel service agents",
        AgentCategory.RETAIL: "E-commerce and retail customer service specialists",
        AgentCategory.LOGISTICS: "Shipping, delivery, and supply chain agents",
        AgentCategory.UTILITIES: "Utility company customer service and billing agents",
        AgentCategory.GOVERNMENT: "Government service and citizen inquiry agents",
        AgentCategory.NON_PROFIT: "Non-profit organization outreach and support agents"
    }
    
    categories_with_counts = []
    for category in AgentCategory:
        agent_count = len([a for a in agents if a.category == category])
        categories_with_counts.append({
            "category": category.value,
            "display_name": category.value.replace("_", " ").title(),
            "description": category_descriptions.get(category, "Specialized agents for this category"),
            "agent_count": agent_count,
            "available": agent_count > 0
        })
    
    return {"categories": categories_with_counts}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8023)
