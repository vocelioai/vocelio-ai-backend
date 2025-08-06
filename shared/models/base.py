"""
Database Models
Comprehensive database schema for all Vocelio microservices
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum
import uuid

# Enums for type safety
class UserRole(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    VIEWER = "viewer"

class AgentStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TRAINING = "training"
    OPTIMIZING = "optimizing"
    MAINTENANCE = "maintenance"

class CampaignStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"

class CallStatus(str, Enum):
    INITIATED = "initiated"
    RINGING = "ringing"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    NO_ANSWER = "no_answer"
    BUSY = "busy"

class VoiceProvider(str, Enum):
    ELEVENLABS = "elevenlabs"
    RAMBLE_AI = "ramble_ai"
    PIPER_TTS = "piper_tts"
    CUSTOM = "custom"

class VoiceQuality(str, Enum):
    STANDARD = "standard"      # Piper TTS - $0.08/min
    PRO = "pro"               # Ramble.AI - $0.18/min
    ULTRA_PREMIUM = "ultra"   # ElevenLabs - $0.35/min

class IndustryType(str, Enum):
    SOLAR_ENERGY = "solar_energy"
    REAL_ESTATE = "real_estate"
    INSURANCE = "insurance"
    HEALTHCARE = "healthcare"
    FINANCE = "finance"
    EDUCATION = "education"
    RETAIL = "retail"
    TECHNOLOGY = "technology"
    AUTOMOTIVE = "automotive"
    OTHER = "other"

class ComplianceType(str, Enum):
    GDPR = "gdpr"
    CCPA = "ccpa"
    TCPA = "tcpa"
    DNC = "dnc"
    HIPAA = "hipaa"

# Base model class with common fields
class BaseModel:
    def __init__(self):
        self.id: str = str(uuid.uuid4())
        self.created_at: datetime = datetime.utcnow()
        self.updated_at: datetime = datetime.utcnow()

# User and Organization Models
class User(BaseModel):
    def __init__(self):
        super().__init__()
        self.email: str = ""
        self.first_name: str = ""
        self.last_name: str = ""
        self.phone: Optional[str] = None
        self.role: UserRole = UserRole.USER
        self.organization_id: Optional[str] = None
        self.is_active: bool = True
        self.profile_image: Optional[str] = None
        self.last_login: Optional[datetime] = None
        self.preferences: Dict[str, Any] = {}
        self.subscription_tier: str = "free"  # free, starter, pro, enterprise

class Organization(BaseModel):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.industry: IndustryType = IndustryType.OTHER
        self.size: str = "small"  # small, medium, large, enterprise
        self.website: Optional[str] = None
        self.phone: Optional[str] = None
        self.address: Dict[str, str] = {}
        self.billing_email: Optional[str] = None
        self.subscription_tier: str = "free"
        self.settings: Dict[str, Any] = {}
        self.compliance_requirements: List[ComplianceType] = []

# AI Agent Models
class Agent(BaseModel):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.description: str = ""
        self.user_id: str = ""
        self.organization_id: str = ""
        self.industry: IndustryType = IndustryType.OTHER
        self.voice_id: str = ""
        self.voice_provider: VoiceProvider = VoiceProvider.PIPER_TTS
        self.language: str = "en"
        self.accent: str = "american"
        self.personality_traits: List[str] = []
        self.status: AgentStatus = AgentStatus.INACTIVE
        self.performance_score: float = 0.0
        self.total_calls: int = 0
        self.success_rate: float = 0.0
        self.avg_call_duration: float = 0.0
        self.revenue_generated: float = 0.0
        self.script_template: str = ""
        self.objection_handlers: List[Dict[str, str]] = []
        self.optimization_settings: Dict[str, Any] = {}
        self.is_template: bool = False
        self.template_category: Optional[str] = None

class AgentTemplate(BaseModel):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.description: str = ""
        self.industry: IndustryType = IndustryType.OTHER
        self.use_case: str = ""
        self.template_data: Dict[str, Any] = {}
        self.expected_performance: Dict[str, float] = {}
        self.is_premium: bool = False
        self.price: float = 0.0
        self.downloads: int = 0
        self.rating: float = 0.0

# Campaign Models
class Campaign(BaseModel):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.description: str = ""
        self.user_id: str = ""
        self.organization_id: str = ""
        self.agent_id: str = ""
        self.status: CampaignStatus = CampaignStatus.DRAFT
        self.industry: IndustryType = IndustryType.OTHER
        self.target_audience: Dict[str, Any] = {}
        self.schedule: Dict[str, Any] = {}  # start_time, end_time, timezone, days
        self.prospect_list: List[Dict[str, str]] = []  # phone, name, additional_data
        self.script: str = ""
        self.goals: Dict[str, Any] = {}  # target_calls, target_conversion_rate
        self.performance_metrics: Dict[str, float] = {}
        self.ai_optimization: Dict[str, Any] = {}
        self.a_b_testing: Dict[str, Any] = {}
        self.compliance_settings: Dict[str, Any] = {}
        self.budget_settings: Dict[str, float] = {}
        self.tags: List[str] = []

class Prospect(BaseModel):
    def __init__(self):
        super().__init__()
        self.campaign_id: str = ""
        self.name: str = ""
        self.phone: str = ""
        self.email: Optional[str] = None
        self.address: Dict[str, str] = {}
        self.additional_data: Dict[str, Any] = {}
        self.status: str = "pending"  # pending, called, converted, do_not_call
        self.call_attempts: int = 0
        self.last_called: Optional[datetime] = None
        self.conversion_value: Optional[float] = None
        self.notes: str = ""

# Call Management Models
class Call(BaseModel):
    def __init__(self):
        super().__init__()
        self.campaign_id: str = ""
        self.agent_id: str = ""
        self.prospect_id: str = ""
        self.phone_number: str = ""
        self.caller_id: str = ""
        self.status: CallStatus = CallStatus.INITIATED
        self.twilio_call_sid: Optional[str] = None
        self.duration: float = 0.0  # in seconds
        self.cost: float = 0.0
        self.recording_url: Optional[str] = None
        self.transcript: str = ""
        self.sentiment_analysis: Dict[str, Any] = {}
        self.conversion_result: Optional[bool] = None
        self.conversion_value: Optional[float] = None
        self.hang_up_reason: Optional[str] = None
        self.ai_insights: Dict[str, Any] = {}
        self.quality_score: Optional[float] = None

class Conversation(BaseModel):
    def __init__(self):
        super().__init__()
        self.call_id: str = ""
        self.messages: List[Dict[str, Any]] = []  # timestamp, speaker, message, sentiment
        self.flow_path: List[str] = []  # nodes traversed
        self.objections_handled: List[str] = []
        self.key_moments: List[Dict[str, Any]] = []
        self.decision_points: List[Dict[str, Any]] = []

# Voice Management Models
class Voice(BaseModel):
    def __init__(self):
        super().__init__()
        self.voice_id: str = ""  # Provider's voice ID
        self.name: str = ""
        self.provider: VoiceProvider = VoiceProvider.PIPER_TTS
        self.quality: VoiceQuality = VoiceQuality.STANDARD
        self.gender: str = "female"  # male, female, neutral
        self.age: str = "young"  # young, middle_aged, old
        self.accent: str = "american"
        self.language: str = "en"
        self.description: str = ""
        self.use_case: str = ""  # business, sales, customer_service
        self.category: str = "premade"  # premade, custom, cloned
        self.performance_metrics: Dict[str, float] = {}
        self.settings: Dict[str, float] = {}  # stability, similarity_boost, style
        self.preview_url: Optional[str] = None
        self.cost_per_character: float = 0.0
        self.available_tiers: List[str] = []
        self.is_active: bool = True
        self.usage_count: int = 0
        self.rating: float = 0.0

class VoiceClone(BaseModel):
    def __init__(self):
        super().__init__()
        self.user_id: str = ""
        self.organization_id: str = ""
        self.name: str = ""
        self.description: str = ""
        self.source_audio_url: str = ""
        self.cloned_voice_id: str = ""
        self.provider: VoiceProvider = VoiceProvider.ELEVENLABS
        self.quality_score: float = 0.0
        self.training_status: str = "pending"  # pending, training, completed, failed
        self.training_progress: float = 0.0
        self.cost: float = 0.0
        self.usage_restrictions: Dict[str, Any] = {}

# Phone Number Management Models
class PhoneNumber(BaseModel):
    def __init__(self):
        super().__init__()
        self.user_id: str = ""
        self.organization_id: str = ""
        self.phone_number: str = ""
        self.friendly_name: str = ""
        self.provider: str = "twilio"
        self.provider_sid: str = ""
        self.country_code: str = ""
        self.region: str = ""
        self.capabilities: List[str] = []  # voice, sms, mms
        self.status: str = "active"  # active, suspended, porting
        self.monthly_cost: float = 0.0
        self.usage_cost: float = 0.0
        self.campaign_assignments: List[str] = []
        self.verification_status: str = "pending"

# Flow Builder Models
class Flow(BaseModel):
    def __init__(self):
        super().__init__()
        self.user_id: str = ""
        self.organization_id: str = ""
        self.name: str = ""
        self.description: str = ""
        self.industry: IndustryType = IndustryType.OTHER
        self.nodes: List[Dict[str, Any]] = []
        self.edges: List[Dict[str, Any]] = []
        self.version: int = 1
        self.is_production: bool = False
        self.performance_metrics: Dict[str, float] = {}
        self.optimization_suggestions: List[str] = []
        self.tags: List[str] = []

class FlowTemplate(BaseModel):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.description: str = ""
        self.industry: IndustryType = IndustryType.OTHER
        self.category: str = ""
        self.template_data: Dict[str, Any] = {}
        self.expected_performance: Dict[str, float] = {}
        self.is_premium: bool = False
        self.price: float = 0.0
        self.downloads: int = 0

# Analytics Models
class AnalyticsMetric(BaseModel):
    def __init__(self):
        super().__init__()
        self.user_id: str = ""
        self.organization_id: str = ""
        self.metric_type: str = ""  # call_volume, conversion_rate, revenue
        self.metric_value: float = 0.0
        self.dimensions: Dict[str, str] = {}  # campaign_id, agent_id, industry
        self.timestamp: datetime = datetime.utcnow()
        self.metadata: Dict[str, Any] = {}

class DashboardWidget(BaseModel):
    def __init__(self):
        super().__init__()
        self.user_id: str = ""
        self.widget_type: str = ""  # metric_card, chart, table
        self.title: str = ""
        self.configuration: Dict[str, Any] = {}
        self.position: Dict[str, int] = {}  # x, y, width, height
        self.is_visible: bool = True

# Billing Models
class BillingAccount(BaseModel):
    def __init__(self):
        super().__init__()
        self.organization_id: str = ""
        self.stripe_customer_id: Optional[str] = None
        self.payment_method_id: Optional[str] = None
        self.billing_email: str = ""
        self.billing_address: Dict[str, str] = {}
        self.current_plan: str = "free"
        self.billing_cycle: str = "monthly"  # monthly, yearly
        self.auto_pay: bool = True
        self.credit_balance: float = 0.0

class UsageLog(BaseModel):
    def __init__(self):
        super().__init__()
        self.user_id: str = ""
        self.organization_id: str = ""
        self.usage_type: str = ""  # call_minutes, voice_generation, api_calls
        self.quantity: float = 0.0
        self.unit_cost: float = 0.0
        self.total_cost: float = 0.0
        self.resource_id: Optional[str] = None  # call_id, voice_id, etc.
        self.billing_period: str = ""  # YYYY-MM
        self.metadata: Dict[str, Any] = {}

class Invoice(BaseModel):
    def __init__(self):
        super().__init__()
        self.organization_id: str = ""
        self.invoice_number: str = ""
        self.billing_period_start: datetime = datetime.utcnow()
        self.billing_period_end: datetime = datetime.utcnow()
        self.subtotal: float = 0.0
        self.tax_amount: float = 0.0
        self.total_amount: float = 0.0
        self.status: str = "draft"  # draft, sent, paid, overdue
        self.due_date: datetime = datetime.utcnow()
        self.paid_date: Optional[datetime] = None
        self.line_items: List[Dict[str, Any]] = []
        self.stripe_invoice_id: Optional[str] = None

# Team Management Models
class TeamMember(BaseModel):
    def __init__(self):
        super().__init__()
        self.user_id: str = ""
        self.organization_id: str = ""
        self.role: UserRole = UserRole.USER
        self.permissions: List[str] = []
        self.invited_by: str = ""
        self.invitation_status: str = "pending"  # pending, accepted, declined
        self.last_active: Optional[datetime] = None

class Permission(BaseModel):
    def __init__(self):
        super().__init__()
        self.name: str = ""
        self.description: str = ""
        self.resource: str = ""  # campaigns, agents, billing
        self.action: str = ""  # read, write, delete, admin
        self.scope: str = "organization"  # user, organization, global

# Compliance Models
class ComplianceRule(BaseModel):
    def __init__(self):
        super().__init__()
        self.organization_id: str = ""
        self.rule_type: ComplianceType = ComplianceType.DNC
        self.name: str = ""
        self.description: str = ""
        self.configuration: Dict[str, Any] = {}
        self.is_active: bool = True
        self.enforcement_level: str = "strict"  # strict, moderate, lenient

class DoNotCallEntry(BaseModel):
    def __init__(self):
        super().__init__()
        self.organization_id: str = ""
        self.phone_number: str = ""
        self.reason: str = ""
        self.source: str = ""  # manual, automated, external
        self.expiry_date: Optional[datetime] = None
        self.notes: str = ""

class ConsentRecord(BaseModel):
    def __init__(self):
        super().__init__()
        self.organization_id: str = ""
        self.prospect_phone: str = ""
        self.consent_type: str = ""  # call, recording, data_processing
        self.consent_given: bool = False
        self.consent_date: datetime = datetime.utcnow()
        self.consent_method: str = ""  # verbal, written, digital
        self.recording_url: Optional[str] = None
        self.expiry_date: Optional[datetime] = None

# Integration Models
class Integration(BaseModel):
    def __init__(self):
        super().__init__()
        self.user_id: str = ""
        self.organization_id: str = ""
        self.provider: str = ""  # salesforce, hubspot, zapier
        self.name: str = ""
        self.configuration: Dict[str, Any] = {}
        self.credentials: Dict[str, str] = {}  # encrypted
        self.status: str = "inactive"  # active, inactive, error
        self.last_sync: Optional[datetime] = None
        self.sync_frequency: str = "daily"
        self.field_mappings: List[Dict[str, str]] = []

class Webhook(BaseModel):
    def __init__(self):
        super().__init__()
        self.user_id: str = ""
        self.organization_id: str = ""
        self.name: str = ""
        self.url: str = ""
        self.events: List[str] = []  # call.completed, campaign.started
        self.secret: str = ""
        self.is_active: bool = True
        self.retry_count: int = 3
        self.timeout: int = 30
        self.last_triggered: Optional[datetime] = None

# White Label Models
class WhiteLabelConfig(BaseModel):
    def __init__(self):
        super().__init__()
        self.organization_id: str = ""
        self.brand_name: str = ""
        self.logo_url: Optional[str] = None
        self.primary_color: str = "#3B82F6"
        self.secondary_color: str = "#1F2937"
        self.custom_domain: Optional[str] = None
        self.email_templates: Dict[str, str] = {}
        self.custom_css: str = ""
        self.support_email: str = ""
        self.terms_url: Optional[str] = None
        self.privacy_url: Optional[str] = None

# API Management Models
class APIKey(BaseModel):
    def __init__(self):
        super().__init__()
        self.user_id: str = ""
        self.organization_id: str = ""
        self.name: str = ""
        self.key_hash: str = ""  # Store hash, not actual key
        self.permissions: List[str] = []
        self.rate_limit: int = 1000  # requests per hour
        self.is_active: bool = True
        self.last_used: Optional[datetime] = None
        self.expires_at: Optional[datetime] = None

class APIUsage(BaseModel):
    def __init__(self):
        super().__init__()
        self.api_key_id: str = ""
        self.endpoint: str = ""
        self.method: str = ""
        self.status_code: int = 200
        self.response_time: float = 0.0
        self.timestamp: datetime = datetime.utcnow()
        self.ip_address: str = ""
        self.user_agent: str = ""
