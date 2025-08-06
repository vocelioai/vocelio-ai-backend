"""
Compliance Service - Vocelio AI Call Center
Call recording, regulatory compliance, audit trail management, and data privacy controls
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Query
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
import hashlib
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Compliance Models
class ComplianceRegulation(str, Enum):
    GDPR = "gdpr"
    CCPA = "ccpa"
    HIPAA = "hipaa"
    PCI_DSS = "pci_dss"
    SOX = "sox"
    TCPA = "tcpa"
    DO_NOT_CALL = "do_not_call"
    PIPEDA = "pipeda"
    LGPD = "lgpd"
    CAN_SPAM = "can_spam"
    FINRA = "finra"
    SEC = "sec"
    FTC = "ftc"
    OSHA = "osha"
    ADA = "ada"

class RecordingStatus(str, Enum):
    RECORDING = "recording"
    COMPLETED = "completed"
    PROCESSING = "processing"
    STORED = "stored"
    ENCRYPTED = "encrypted"
    ARCHIVED = "archived"
    DELETED = "deleted"
    FAILED = "failed"

class ConsentType(str, Enum):
    EXPLICIT = "explicit"
    IMPLIED = "implied"
    OPT_IN = "opt_in"
    OPT_OUT = "opt_out"
    GRANULAR = "granular"

class AuditAction(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    ACCESS = "access"
    EXPORT = "export"
    SHARE = "share"
    DOWNLOAD = "download"
    PRINT = "print"
    LOGIN = "login"
    LOGOUT = "logout"

class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    REQUIRES_ACTION = "requires_action"
    UNKNOWN = "unknown"

class DataClassification(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"
    PII = "pii"
    PHI = "phi"
    PCI = "pci"
    FINANCIAL = "financial"

class RetentionPeriod(BaseModel):
    duration_days: int
    regulation: ComplianceRegulation
    description: str
    auto_delete: bool = True
    legal_hold_exempt: bool = False

class ConsentRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    phone_number: str
    email: Optional[str] = None
    consent_type: ConsentType
    purpose: str
    granted_at: datetime = Field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    consent_text: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    recording_allowed: bool = True
    data_processing_allowed: bool = True
    marketing_allowed: bool = False
    third_party_sharing_allowed: bool = False
    
    # Compliance metadata
    regulation_compliance: List[ComplianceRegulation] = []
    consent_version: str = "1.0"
    jurisdiction: str = "US"
    
    # Audit fields
    created_by: str
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None

class CallRecording(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    call_id: str
    customer_id: str
    agent_id: str
    phone_number: str
    
    # Recording details
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    file_path: str
    file_size_bytes: Optional[int] = None
    format: str = "wav"  # "wav", "mp3", "ogg"
    sample_rate: int = 8000
    channels: int = 1
    
    # Status and processing
    status: RecordingStatus = RecordingStatus.RECORDING
    processed_at: Optional[datetime] = None
    storage_location: str  # "local", "s3", "azure", "gcp"
    encryption_key_id: Optional[str] = None
    checksum: Optional[str] = None
    
    # Compliance
    consent_record_id: Optional[str] = None
    retention_policy_id: str
    retention_until: datetime
    legal_hold: bool = False
    redaction_applied: bool = False
    
    # Classification
    data_classification: DataClassification = DataClassification.CONFIDENTIAL
    pii_detected: bool = False
    sensitive_content_flags: List[str] = []
    
    # Quality and analysis
    transcription: Optional[str] = None
    sentiment_score: Optional[float] = None
    compliance_score: Optional[float] = None
    quality_score: Optional[float] = None
    
    # Metadata
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class RetentionPolicy(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    applicable_regulations: List[ComplianceRegulation]
    data_types: List[DataClassification]
    retention_periods: List[RetentionPeriod]
    
    # Conditions
    geographic_scope: List[str] = ["global"]
    business_units: List[str] = ["all"]
    exceptions: List[str] = []
    
    # Actions
    auto_delete_enabled: bool = True
    notification_days_before: int = 30
    backup_before_deletion: bool = True
    secure_deletion_method: str = "dod_5220_22_m"
    
    # Status
    is_active: bool = True
    effective_date: datetime = Field(default_factory=datetime.now)
    review_date: datetime
    approved_by: str
    created_at: datetime = Field(default_factory=datetime.now)

class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    user_name: str
    user_role: str
    action: AuditAction
    resource_type: str  # "recording", "consent", "policy", "report"
    resource_id: str
    
    # Action details
    description: str
    changes: Dict[str, Any] = {}  # before/after values
    success: bool = True
    error_message: Optional[str] = None
    
    # Context
    ip_address: str
    user_agent: str
    session_id: str
    request_id: str
    
    # Compliance
    regulation_context: List[ComplianceRegulation] = []
    risk_level: str = "low"  # "low", "medium", "high", "critical"
    
    # Metadata
    additional_data: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.now)

class ComplianceReport(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    report_type: str  # "retention", "consent", "audit", "breach", "compliance_status"
    regulation: ComplianceRegulation
    
    # Report parameters
    start_date: datetime
    end_date: datetime
    scope: List[str] = ["all"]
    filters: Dict[str, Any] = {}
    
    # Results
    status: str = "pending"  # "pending", "generating", "completed", "failed"
    findings: List[Dict[str, Any]] = []
    recommendations: List[str] = []
    compliance_score: Optional[float] = None
    
    # Metrics
    total_records_reviewed: int = 0
    compliant_records: int = 0
    non_compliant_records: int = 0
    violations_found: int = 0
    
    # File output
    file_path: Optional[str] = None
    file_format: str = "pdf"  # "pdf", "excel", "csv", "json"
    
    # Metadata
    generated_by: str
    generated_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

class DataSubjectRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_type: str  # "access", "rectification", "erasure", "portability", "restriction"
    customer_id: str
    customer_email: str
    customer_phone: str
    
    # Request details
    description: str
    scope: List[str] = ["all"]  # specific data types requested
    legal_basis: str
    regulation: ComplianceRegulation
    
    # Processing
    status: str = "received"  # "received", "processing", "completed", "rejected"
    assigned_to: Optional[str] = None
    due_date: datetime
    response_sent_at: Optional[datetime] = None
    
    # Verification
    identity_verified: bool = False
    verification_method: Optional[str] = None
    verification_date: Optional[datetime] = None
    
    # Results
    data_found: bool = False
    data_exported: bool = False
    data_deleted: bool = False
    export_file_path: Optional[str] = None
    
    # Compliance
    response_time_hours: Optional[float] = None
    compliance_met: bool = False
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class ComplianceViolation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    violation_type: str
    regulation: ComplianceRegulation
    severity: str = "medium"  # "low", "medium", "high", "critical"
    
    # Violation details
    description: str
    affected_resource_type: str
    affected_resource_id: str
    detection_method: str  # "automated", "manual", "audit", "customer_complaint"
    
    # Impact assessment
    data_subjects_affected: int = 0
    data_types_involved: List[DataClassification] = []
    potential_harm: str
    
    # Response
    status: str = "open"  # "open", "investigating", "resolved", "closed"
    assigned_to: Optional[str] = None
    remediation_plan: Optional[str] = None
    remediation_completed: bool = False
    
    # Notifications
    regulatory_notification_required: bool = False
    customer_notification_required: bool = False
    notifications_sent: List[str] = []
    
    # Timeline
    detected_at: datetime = Field(default_factory=datetime.now)
    reported_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Cost impact
    estimated_fine: Optional[Decimal] = None
    remediation_cost: Optional[Decimal] = None

# Sample data
SAMPLE_RETENTION_POLICIES = [
    RetentionPolicy(
        name="General Call Recording Retention",
        description="Standard retention policy for customer service call recordings",
        applicable_regulations=[ComplianceRegulation.GDPR, ComplianceRegulation.CCPA],
        data_types=[DataClassification.CONFIDENTIAL],
        retention_periods=[
            RetentionPeriod(
                duration_days=1095,  # 3 years
                regulation=ComplianceRegulation.GDPR,
                description="GDPR compliant retention for customer service recordings"
            )
        ],
        review_date=datetime.now() + timedelta(days=365),
        approved_by="compliance_team"
    ),
    RetentionPolicy(
        name="Healthcare Call Retention (HIPAA)",
        description="HIPAA-compliant retention policy for healthcare-related calls",
        applicable_regulations=[ComplianceRegulation.HIPAA],
        data_types=[DataClassification.PHI],
        retention_periods=[
            RetentionPeriod(
                duration_days=2190,  # 6 years
                regulation=ComplianceRegulation.HIPAA,
                description="HIPAA minimum retention requirement for PHI"
            )
        ],
        review_date=datetime.now() + timedelta(days=180),
        approved_by="healthcare_compliance"
    ),
    RetentionPolicy(
        name="Financial Services Retention",
        description="Financial industry compliance retention policy",
        applicable_regulations=[ComplianceRegulation.SOX, ComplianceRegulation.FINRA],
        data_types=[DataClassification.FINANCIAL],
        retention_periods=[
            RetentionPeriod(
                duration_days=2555,  # 7 years
                regulation=ComplianceRegulation.SOX,
                description="SOX requirement for financial communications"
            )
        ],
        review_date=datetime.now() + timedelta(days=365),
        approved_by="financial_compliance"
    )
]

SAMPLE_RECORDINGS = [
    CallRecording(
        call_id="call_001",
        customer_id="cust_001",
        agent_id="agent_001",
        phone_number="+1234567890",
        start_time=datetime.now() - timedelta(hours=2),
        end_time=datetime.now() - timedelta(hours=2) + timedelta(minutes=12),
        duration_seconds=720.5,
        file_path="/recordings/2025/08/05/call_001.wav",
        file_size_bytes=1440000,
        status=RecordingStatus.STORED,
        storage_location="s3",
        retention_policy_id="retention_001",
        retention_until=datetime.now() + timedelta(days=1095),
        transcription="Thank you for calling customer service. How can I help you today?",
        sentiment_score=0.7,
        compliance_score=0.95,
        quality_score=0.88
    ),
    CallRecording(
        call_id="call_002",
        customer_id="cust_002",
        agent_id="agent_002",
        phone_number="+1987654321",
        start_time=datetime.now() - timedelta(hours=1),
        end_time=datetime.now() - timedelta(hours=1) + timedelta(minutes=8),
        duration_seconds=480.2,
        file_path="/recordings/2025/08/05/call_002.wav",
        file_size_bytes=960000,
        status=RecordingStatus.STORED,
        storage_location="s3",
        retention_policy_id="retention_001",
        retention_until=datetime.now() + timedelta(days=1095),
        pii_detected=True,
        sensitive_content_flags=["credit_card", "ssn"],
        transcription="I need to update my payment information for my account.",
        sentiment_score=0.2,
        compliance_score=0.92,
        quality_score=0.91
    )
]

# Global storage
recordings: List[CallRecording] = []
retention_policies: List[RetentionPolicy] = []
consent_records: List[ConsentRecord] = []
audit_logs: List[AuditLog] = []
compliance_reports: List[ComplianceReport] = []
data_subject_requests: List[DataSubjectRequest] = []
violations: List[ComplianceViolation] = []

async def initialize_sample_data():
    """Initialize sample data for the service"""
    global recordings, retention_policies
    
    retention_policies.extend(SAMPLE_RETENTION_POLICIES)
    recordings.extend(SAMPLE_RECORDINGS)
    
    # Create sample consent records
    sample_consents = [
        ConsentRecord(
            customer_id="cust_001",
            phone_number="+1234567890",
            email="customer1@example.com",
            consent_type=ConsentType.EXPLICIT,
            purpose="Customer service call recording for quality assurance",
            consent_text="I consent to having my call recorded for quality and training purposes.",
            regulation_compliance=[ComplianceRegulation.GDPR, ComplianceRegulation.CCPA],
            created_by="system"
        ),
        ConsentRecord(
            customer_id="cust_002",
            phone_number="+1987654321",
            email="customer2@example.com",
            consent_type=ConsentType.IMPLIED,
            purpose="Service call recording",
            consent_text="By continuing this call, you consent to recording.",
            regulation_compliance=[ComplianceRegulation.TCPA],
            created_by="system"
        )
    ]
    
    consent_records.extend(sample_consents)
    
    logger.info("Sample compliance data initialized successfully")

async def log_audit_action(
    user_id: str,
    user_name: str,
    user_role: str,
    action: AuditAction,
    resource_type: str,
    resource_id: str,
    description: str,
    ip_address: str = "127.0.0.1",
    changes: Dict[str, Any] = None
):
    """Log an audit action"""
    
    audit_log = AuditLog(
        user_id=user_id,
        user_name=user_name,
        user_role=user_role,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        changes=changes or {},
        ip_address=ip_address,
        user_agent="Vocelio-API/1.0",
        session_id=str(uuid.uuid4()),
        request_id=str(uuid.uuid4())
    )
    
    audit_logs.append(audit_log)
    logger.info(f"Audit log created: {action} on {resource_type} {resource_id}")

async def check_compliance_status(recording: CallRecording) -> ComplianceStatus:
    """Check compliance status of a recording"""
    
    # Check if consent exists
    consent = next((c for c in consent_records if c.customer_id == recording.customer_id), None)
    if not consent or not consent.recording_allowed:
        return ComplianceStatus.NON_COMPLIANT
    
    # Check retention policy
    policy = next((p for p in retention_policies if p.id == recording.retention_policy_id), None)
    if not policy:
        return ComplianceStatus.UNKNOWN
    
    # Check if recording is within retention period
    if recording.retention_until < datetime.now():
        return ComplianceStatus.REQUIRES_ACTION
    
    # Check for sensitive data handling
    if recording.pii_detected and not recording.redaction_applied:
        return ComplianceStatus.REQUIRES_ACTION
    
    return ComplianceStatus.COMPLIANT

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_sample_data()
    yield
    
    # Shutdown
    pass

# FastAPI app
app = FastAPI(
    title="Compliance Service",
    description="Call recording, regulatory compliance, audit trail management, and data privacy controls for Vocelio AI Call Center",
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
        "service": "compliance",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Call Recording Endpoints
@app.get("/recordings", response_model=List[CallRecording])
async def get_recordings(
    status: Optional[RecordingStatus] = None,
    customer_id: Optional[str] = None,
    agent_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    compliance_check: bool = False,
    limit: int = 50,
    offset: int = 0
):
    """Get call recordings with filtering options"""
    
    filtered_recordings = recordings.copy()
    
    # Apply filters
    if status:
        filtered_recordings = [r for r in filtered_recordings if r.status == status]
    
    if customer_id:
        filtered_recordings = [r for r in filtered_recordings if r.customer_id == customer_id]
    
    if agent_id:
        filtered_recordings = [r for r in filtered_recordings if r.agent_id == agent_id]
    
    if start_date:
        filtered_recordings = [r for r in filtered_recordings if r.start_time >= start_date]
    
    if end_date:
        filtered_recordings = [r for r in filtered_recordings if r.start_time <= end_date]
    
    # Check compliance status if requested
    if compliance_check:
        for recording in filtered_recordings:
            recording.metadata["compliance_status"] = await check_compliance_status(recording)
    
    # Sort by start time, most recent first
    filtered_recordings.sort(key=lambda x: x.start_time, reverse=True)
    
    # Apply pagination
    return filtered_recordings[offset:offset + limit]

@app.get("/recordings/{recording_id}", response_model=CallRecording)
async def get_recording(recording_id: str, user_id: str = "system"):
    """Get a specific recording by ID"""
    recording = next((r for r in recordings if r.id == recording_id), None)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    # Log access
    await log_audit_action(
        user_id=user_id,
        user_name="API User",
        user_role="user",
        action=AuditAction.ACCESS,
        resource_type="recording",
        resource_id=recording_id,
        description=f"Accessed recording {recording_id}"
    )
    
    return recording

@app.post("/recordings", response_model=CallRecording)
async def create_recording(recording_data: CallRecording):
    """Create a new call recording record"""
    
    # Find appropriate retention policy
    if not recording_data.retention_policy_id:
        default_policy = next((p for p in retention_policies if p.name == "General Call Recording Retention"), None)
        if default_policy:
            recording_data.retention_policy_id = default_policy.id
            recording_data.retention_until = datetime.now() + timedelta(days=1095)
    
    recordings.append(recording_data)
    
    # Log creation
    await log_audit_action(
        user_id="system",
        user_name="System",
        user_role="system",
        action=AuditAction.CREATE,
        resource_type="recording",
        resource_id=recording_data.id,
        description=f"Created recording for call {recording_data.call_id}"
    )
    
    logger.info(f"Created recording: {recording_data.id}")
    return recording_data

@app.put("/recordings/{recording_id}/redact")
async def redact_recording(
    recording_id: str,
    redaction_type: str,  # "pii", "payment", "full"
    user_id: str,
    reason: str
):
    """Apply redaction to a recording"""
    recording = next((r for r in recordings if r.id == recording_id), None)
    if not recording:
        raise HTTPException(status_code=404, detail="Recording not found")
    
    # Apply redaction
    recording.redaction_applied = True
    recording.sensitive_content_flags.append(f"redacted_{redaction_type}")
    recording.updated_at = datetime.now()
    
    # Log redaction
    await log_audit_action(
        user_id=user_id,
        user_name="API User",
        user_role="user",
        action=AuditAction.UPDATE,
        resource_type="recording",
        resource_id=recording_id,
        description=f"Applied {redaction_type} redaction: {reason}",
        changes={"redaction_applied": True, "redaction_type": redaction_type}
    )
    
    logger.info(f"Applied redaction to recording: {recording_id}")
    return {"message": "Redaction applied successfully"}

# Consent Management Endpoints
@app.get("/consent", response_model=List[ConsentRecord])
async def get_consent_records(
    customer_id: Optional[str] = None,
    phone_number: Optional[str] = None,
    consent_type: Optional[ConsentType] = None,
    active_only: bool = True,
    limit: int = 50
):
    """Get consent records with filtering options"""
    
    filtered_consents = consent_records.copy()
    
    if customer_id:
        filtered_consents = [c for c in filtered_consents if c.customer_id == customer_id]
    
    if phone_number:
        filtered_consents = [c for c in filtered_consents if c.phone_number == phone_number]
    
    if consent_type:
        filtered_consents = [c for c in filtered_consents if c.consent_type == consent_type]
    
    if active_only:
        now = datetime.now()
        filtered_consents = [
            c for c in filtered_consents 
            if c.revoked_at is None and (c.expires_at is None or c.expires_at > now)
        ]
    
    # Sort by granted date, most recent first
    filtered_consents.sort(key=lambda x: x.granted_at, reverse=True)
    
    return filtered_consents[:limit]

@app.post("/consent", response_model=ConsentRecord)
async def create_consent_record(consent_data: ConsentRecord):
    """Create a new consent record"""
    consent_records.append(consent_data)
    
    # Log consent creation
    await log_audit_action(
        user_id=consent_data.created_by,
        user_name="API User",
        user_role="user",
        action=AuditAction.CREATE,
        resource_type="consent",
        resource_id=consent_data.id,
        description=f"Created consent record for customer {consent_data.customer_id}"
    )
    
    logger.info(f"Created consent record: {consent_data.id}")
    return consent_data

@app.put("/consent/{consent_id}/revoke")
async def revoke_consent(consent_id: str, user_id: str, reason: str):
    """Revoke a consent record"""
    consent = next((c for c in consent_records if c.id == consent_id), None)
    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found")
    
    consent.revoked_at = datetime.now()
    consent.updated_by = user_id
    consent.updated_at = datetime.now()
    
    # Log revocation
    await log_audit_action(
        user_id=user_id,
        user_name="API User",
        user_role="user",
        action=AuditAction.UPDATE,
        resource_type="consent",
        resource_id=consent_id,
        description=f"Revoked consent: {reason}",
        changes={"revoked_at": consent.revoked_at.isoformat()}
    )
    
    logger.info(f"Revoked consent: {consent_id}")
    return {"message": "Consent revoked successfully"}

# Retention Policy Endpoints
@app.get("/retention-policies", response_model=List[RetentionPolicy])
async def get_retention_policies(regulation: Optional[ComplianceRegulation] = None):
    """Get retention policies"""
    if regulation:
        return [p for p in retention_policies if regulation in p.applicable_regulations]
    return retention_policies

@app.post("/retention-policies", response_model=RetentionPolicy)
async def create_retention_policy(policy_data: RetentionPolicy):
    """Create a new retention policy"""
    retention_policies.append(policy_data)
    
    # Log policy creation
    await log_audit_action(
        user_id=policy_data.approved_by,
        user_name="Policy Admin",
        user_role="admin",
        action=AuditAction.CREATE,
        resource_type="retention_policy",
        resource_id=policy_data.id,
        description=f"Created retention policy: {policy_data.name}"
    )
    
    logger.info(f"Created retention policy: {policy_data.name}")
    return policy_data

# Audit Log Endpoints
@app.get("/audit-logs", response_model=List[AuditLog])
async def get_audit_logs(
    user_id: Optional[str] = None,
    action: Optional[AuditAction] = None,
    resource_type: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    risk_level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0
):
    """Get audit logs with filtering options"""
    
    filtered_logs = audit_logs.copy()
    
    # Apply filters
    if user_id:
        filtered_logs = [l for l in filtered_logs if l.user_id == user_id]
    
    if action:
        filtered_logs = [l for l in filtered_logs if l.action == action]
    
    if resource_type:
        filtered_logs = [l for l in filtered_logs if l.resource_type == resource_type]
    
    if start_date:
        filtered_logs = [l for l in filtered_logs if l.timestamp >= start_date]
    
    if end_date:
        filtered_logs = [l for l in filtered_logs if l.timestamp <= end_date]
    
    if risk_level:
        filtered_logs = [l for l in filtered_logs if l.risk_level == risk_level]
    
    # Sort by timestamp, most recent first
    filtered_logs.sort(key=lambda x: x.timestamp, reverse=True)
    
    # Apply pagination
    return filtered_logs[offset:offset + limit]

# Compliance Reports Endpoints
@app.post("/reports", response_model=ComplianceReport)
async def create_compliance_report(
    name: str,
    report_type: str,
    regulation: ComplianceRegulation,
    start_date: datetime,
    end_date: datetime,
    generated_by: str,
    background_tasks: BackgroundTasks
):
    """Create a compliance report"""
    
    report = ComplianceReport(
        name=name,
        report_type=report_type,
        regulation=regulation,
        start_date=start_date,
        end_date=end_date,
        generated_by=generated_by
    )
    
    compliance_reports.append(report)
    
    # Generate report in background
    background_tasks.add_task(generate_compliance_report, report.id)
    
    logger.info(f"Created compliance report: {name}")
    return report

async def generate_compliance_report(report_id: str):
    """Generate compliance report content"""
    report = next((r for r in compliance_reports if r.id == report_id), None)
    if not report:
        return
    
    report.status = "generating"
    
    # Simulate report generation
    await asyncio.sleep(2)
    
    # Mock findings
    if report.report_type == "retention":
        total_recordings = len([r for r in recordings if report.start_date <= r.start_time <= report.end_date])
        compliant_recordings = len([r for r in recordings if r.retention_until > datetime.now()])
        
        report.total_records_reviewed = total_recordings
        report.compliant_records = compliant_recordings
        report.non_compliant_records = total_recordings - compliant_recordings
        report.compliance_score = (compliant_recordings / total_recordings * 100) if total_recordings > 0 else 100
        
        report.findings = [
            {"type": "retention", "description": f"{compliant_recordings} recordings comply with retention policy"},
            {"type": "retention", "description": f"{total_recordings - compliant_recordings} recordings require attention"}
        ]
        
        if report.compliance_score < 95:
            report.recommendations = [
                "Review and update retention policies",
                "Implement automated retention management",
                "Conduct staff training on compliance requirements"
            ]
    
    report.status = "completed"
    report.generated_at = datetime.now()
    report.file_path = f"/reports/{report.id}.pdf"
    
    logger.info(f"Generated compliance report: {report.id}")

@app.get("/reports", response_model=List[ComplianceReport])
async def get_compliance_reports(
    report_type: Optional[str] = None,
    regulation: Optional[ComplianceRegulation] = None,
    status: Optional[str] = None
):
    """Get compliance reports"""
    filtered_reports = compliance_reports.copy()
    
    if report_type:
        filtered_reports = [r for r in filtered_reports if r.report_type == report_type]
    
    if regulation:
        filtered_reports = [r for r in filtered_reports if r.regulation == regulation]
    
    if status:
        filtered_reports = [r for r in filtered_reports if r.status == status]
    
    # Sort by creation date, most recent first
    filtered_reports.sort(key=lambda x: x.created_at, reverse=True)
    
    return filtered_reports

@app.get("/reports/{report_id}", response_model=ComplianceReport)
async def get_compliance_report(report_id: str):
    """Get a specific compliance report"""
    report = next((r for r in compliance_reports if r.id == report_id), None)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

# Data Subject Rights Endpoints
@app.post("/data-subject-requests", response_model=DataSubjectRequest)
async def create_data_subject_request(request_data: DataSubjectRequest):
    """Create a data subject request (GDPR Article 15-22)"""
    
    # Set due date based on regulation
    if request_data.regulation == ComplianceRegulation.GDPR:
        request_data.due_date = datetime.now() + timedelta(days=30)
    elif request_data.regulation == ComplianceRegulation.CCPA:
        request_data.due_date = datetime.now() + timedelta(days=45)
    else:
        request_data.due_date = datetime.now() + timedelta(days=30)
    
    data_subject_requests.append(request_data)
    
    # Log request creation
    await log_audit_action(
        user_id="system",
        user_name="System",
        user_role="system",
        action=AuditAction.CREATE,
        resource_type="data_subject_request",
        resource_id=request_data.id,
        description=f"Created {request_data.request_type} request for {request_data.customer_email}"
    )
    
    logger.info(f"Created data subject request: {request_data.id}")
    return request_data

@app.get("/data-subject-requests", response_model=List[DataSubjectRequest])
async def get_data_subject_requests(
    request_type: Optional[str] = None,
    status: Optional[str] = None,
    regulation: Optional[ComplianceRegulation] = None,
    overdue_only: bool = False
):
    """Get data subject requests"""
    filtered_requests = data_subject_requests.copy()
    
    if request_type:
        filtered_requests = [r for r in filtered_requests if r.request_type == request_type]
    
    if status:
        filtered_requests = [r for r in filtered_requests if r.status == status]
    
    if regulation:
        filtered_requests = [r for r in filtered_requests if r.regulation == regulation]
    
    if overdue_only:
        now = datetime.now()
        filtered_requests = [r for r in filtered_requests if r.due_date < now and r.status != "completed"]
    
    # Sort by due date, most urgent first
    filtered_requests.sort(key=lambda x: x.due_date)
    
    return filtered_requests

# Compliance Dashboard Endpoints
@app.get("/dashboard/overview")
async def get_compliance_overview():
    """Get compliance dashboard overview"""
    
    total_recordings = len(recordings)
    active_consents = len([c for c in consent_records if c.revoked_at is None])
    pending_requests = len([r for r in data_subject_requests if r.status != "completed"])
    open_violations = len([v for v in violations if v.status == "open"])
    
    # Calculate compliance scores
    recording_compliance = 0
    if total_recordings > 0:
        compliant_recordings = len([r for r in recordings if r.retention_until > datetime.now()])
        recording_compliance = (compliant_recordings / total_recordings) * 100
    
    # Recent activity
    recent_audits = len([a for a in audit_logs if a.timestamp > datetime.now() - timedelta(hours=24)])
    recent_recordings = len([r for r in recordings if r.created_at > datetime.now() - timedelta(hours=24)])
    
    return {
        "compliance_scores": {
            "overall": round((recording_compliance + 95) / 2, 1),  # Mock overall score
            "recordings": round(recording_compliance, 1),
            "consent_management": 98.5,
            "data_retention": 96.2,
            "audit_compliance": 99.1
        },
        "statistics": {
            "total_recordings": total_recordings,
            "active_consents": active_consents,
            "retention_policies": len(retention_policies),
            "pending_data_requests": pending_requests,
            "open_violations": open_violations,
            "audit_log_entries": len(audit_logs)
        },
        "recent_activity": {
            "recordings_24h": recent_recordings,
            "audit_actions_24h": recent_audits,
            "new_consents_24h": len([c for c in consent_records if c.granted_at > datetime.now() - timedelta(hours=24)]),
            "resolved_violations_24h": len([v for v in violations if v.resolved_at and v.resolved_at > datetime.now() - timedelta(hours=24)])
        },
        "alerts": [
            {"type": "warning", "message": f"{pending_requests} data subject requests pending"},
            {"type": "info", "message": f"{open_violations} compliance violations require attention"},
            {"type": "success", "message": "All retention policies are up to date"}
        ],
        "regulatory_status": {
            ComplianceRegulation.GDPR.value: "compliant",
            ComplianceRegulation.CCPA.value: "compliant", 
            ComplianceRegulation.HIPAA.value: "compliant",
            ComplianceRegulation.TCPA.value: "compliant"
        }
    }

@app.get("/dashboard/violations")
async def get_compliance_violations():
    """Get compliance violations dashboard"""
    
    # Group violations by severity
    violation_summary = {
        "critical": len([v for v in violations if v.severity == "critical"]),
        "high": len([v for v in violations if v.severity == "high"]),
        "medium": len([v for v in violations if v.severity == "medium"]),
        "low": len([v for v in violations if v.severity == "low"])
    }
    
    # Recent violations
    recent_violations = [v for v in violations if v.detected_at > datetime.now() - timedelta(days=30)]
    
    return {
        "summary": violation_summary,
        "total_violations": len(violations),
        "open_violations": len([v for v in violations if v.status == "open"]),
        "resolved_this_month": len([v for v in violations if v.resolved_at and v.resolved_at > datetime.now() - timedelta(days=30)]),
        "recent_violations": recent_violations[:10],
        "top_violation_types": [
            {"type": "consent_missing", "count": 3, "percentage": 30},
            {"type": "retention_exceeded", "count": 2, "percentage": 20},
            {"type": "unauthorized_access", "count": 2, "percentage": 20},
            {"type": "data_breach", "count": 1, "percentage": 10},
            {"type": "policy_violation", "count": 2, "percentage": 20}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8014)
