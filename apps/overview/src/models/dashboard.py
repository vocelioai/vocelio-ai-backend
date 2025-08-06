"""
Overview Service Database Models
SQLAlchemy models for dashboard, metrics, and reports data
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

Base = declarative_base()

class Dashboard(Base):
    """Dashboard configuration model"""
    __tablename__ = "dashboards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    layout_config = Column(JSON)
    widget_configs = Column(JSON)
    is_default = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    theme = Column(String(50), default="dark")
    refresh_interval = Column(Integer, default=30)
    auto_refresh = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MetricsSnapshot(Base):
    """Metrics snapshot model for historical data"""
    __tablename__ = "metrics_snapshots"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    snapshot_time = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Core metrics
    active_calls = Column(Integer, default=0)
    calls_per_minute = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)
    revenue_today = Column(Float, default=0.0)
    revenue_this_hour = Column(Float, default=0.0)
    bookings_today = Column(Integer, default=0)
    conversion_rate = Column(Float, default=0.0)
    average_call_duration = Column(Integer, default=0)
    ai_optimization_score = Column(Float, default=0.0)
    agent_utilization = Column(Float, default=0.0)
    queue_wait_time = Column(Integer, default=0)
    system_load = Column(Float, default=0.0)
    
    # Additional metrics
    total_agents_active = Column(Integer, default=0)
    campaigns_running = Column(Integer, default=0)
    error_rate = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class AIInsight(Base):
    """AI insights and recommendations model"""
    __tablename__ = "ai_insights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    impact_score = Column(Integer, nullable=False)  # 0-100
    confidence = Column(Float, nullable=False)  # 0.0-1.0
    priority = Column(String(20), nullable=False)  # low, medium, high, critical
    category = Column(String(50), nullable=False)
    estimated_revenue_impact = Column(Float)
    implementation_effort = Column(String(20))  # low, medium, high
    action_type = Column(String(50), nullable=False)
    
    # Metadata
    data_sources = Column(JSON)
    parameters = Column(JSON)
    ai_model_version = Column(String(50))
    
    # Status
    status = Column(String(20), default="active")  # active, implemented, dismissed, expired
    implemented = Column(Boolean, default=False)
    implemented_at = Column(DateTime)
    implemented_by = Column(UUID(as_uuid=True))
    
    # Lifecycle
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemHealthCheck(Base):
    """System health check results model"""
    __tablename__ = "system_health_checks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = Column(String(100), nullable=False, index=True)
    check_time = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Health metrics
    status = Column(String(20), nullable=False)  # healthy, degraded, critical, down
    uptime_percentage = Column(Float, default=100.0)
    response_time = Column(Float)  # in milliseconds
    error_rate = Column(Float, default=0.0)
    cpu_usage = Column(Float)
    memory_usage = Column(Float)
    disk_usage = Column(Float)
    active_connections = Column(Integer)
    
    # Additional data
    version = Column(String(50))
    environment = Column(String(20))
    region = Column(String(50))
    health_details = Column(JSON)
    alerts = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    """Dashboard notifications model"""
    __tablename__ = "notifications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=True, index=True)
    
    # Notification content
    type = Column(String(20), nullable=False)  # success, warning, error, info
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    
    # Status
    read = Column(Boolean, default=False)
    acknowledged = Column(Boolean, default=False)
    
    # Actions
    action_url = Column(String(500))
    action_label = Column(String(100))
    dismiss_after = Column(Integer)  # seconds
    
    # Metadata
    source_service = Column(String(100))
    source_event = Column(String(100))
    metadata = Column(JSON)
    
    # Lifecycle
    read_at = Column(DateTime)
    read_by = Column(UUID(as_uuid=True))
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Report(Base):
    """Report generation model"""
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Report configuration
    report_type = Column(String(50), nullable=False)
    title = Column(String(255))
    description = Column(Text)
    format = Column(String(20), nullable=False)  # pdf, excel, csv, json
    
    # Parameters
    parameters = Column(JSON)
    filters = Column(JSON)
    time_range = Column(String(20))
    sections = Column(JSON)
    
    # Status
    status = Column(String(20), default="pending")  # pending, processing, completed, failed, cancelled
    error_message = Column(Text)
    
    # File information
    file_path = Column(String(500))
    file_size = Column(Integer)  # in bytes
    file_hash = Column(String(64))  # SHA-256
    
    # Scheduling
    scheduled = Column(Boolean, default=False)
    schedule_id = Column(UUID(as_uuid=True))
    
    # Lifecycle
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
    downloaded_at = Column(DateTime)
    download_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ScheduledReport(Base):
    """Scheduled report configuration model"""
    __tablename__ = "scheduled_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Schedule configuration
    name = Column(String(255), nullable=False)
    description = Column(Text)
    report_type = Column(String(50), nullable=False)
    format = Column(String(20), nullable=False)
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly
    schedule_time = Column(String(5))  # HH:MM format
    timezone = Column(String(50), default="UTC")
    
    # Report configuration
    parameters = Column(JSON)
    filters = Column(JSON)
    sections = Column(JSON)
    
    # Recipients
    recipient_emails = Column(JSON)
    delivery_method = Column(String(20), default="email")  # email, webhook, storage
    
    # Status
    enabled = Column(Boolean, default=True)
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    run_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Metadata
    last_error = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class QuickAction(Base):
    """Quick actions model"""
    __tablename__ = "quick_actions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Action definition
    action_id = Column(String(100), nullable=False, unique=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    
    # Impact
    estimated_impact = Column(String(255))
    effort = Column(String(100))
    confidence = Column(Float)  # 0.0-1.0
    
    # Parameters
    parameters_schema = Column(JSON)
    default_parameters = Column(JSON)
    
    # Status
    enabled = Column(Boolean, default=True)
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Metadata
    icon = Column(String(50))
    color = Column(String(20))
    tags = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ActionExecution(Base):
    """Action execution history model"""
    __tablename__ = "action_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action_id = Column(String(100), nullable=False, index=True)
    
    # Execution details
    parameters = Column(JSON)
    status = Column(String(20), nullable=False)  # pending, running, completed, failed, cancelled
    result = Column(JSON)
    error_message = Column(Text)
    
    # Timing
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    
    # Impact tracking
    impact_metrics = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class MetricGoal(Base):
    """Metric goals and targets model"""
    __tablename__ = "metric_goals"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Goal definition
    metric_name = Column(String(100), nullable=False)
    target_value = Column(Float, nullable=False)
    current_value = Column(Float, default=0.0)
    progress_percentage = Column(Float, default=0.0)
    
    # Timeline
    target_date = Column(DateTime, nullable=False)
    goal_type = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly, yearly
    
    # Status
    status = Column(String(20), default="active")  # active, achieved, failed, paused
    achieved_at = Column(DateTime)
    
    # Metadata
    description = Column(Text)
    category = Column(String(50))
    priority = Column(String(20), default="medium")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Alert(Base):
    """Real-time alerts model"""
    __tablename__ = "alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Alert definition
    alert_type = Column(String(50), nullable=False)  # threshold, anomaly, trend, system
    metric_name = Column(String(100), nullable=False)
    current_value = Column(Float, nullable=False)
    threshold_value = Column(Float)
    condition = Column(String(20))  # gt, lt, eq, ne, gte, lte
    
    # Severity
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    priority = Column(Integer, default=0)
    
    # Content
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    status = Column(String(20), default="active")  # active, acknowledged, resolved, suppressed
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(UUID(as_uuid=True))
    acknowledged_at = Column(DateTime)
    resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime)
    auto_resolve = Column(Boolean, default=False)
    
    # Actions
    actions_taken = Column(JSON)
    escalation_rules = Column(JSON)
    
    # Lifecycle
    triggered_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Indexes for better query performance
from sqlalchemy import Index

# Create indexes
Index('idx_metrics_snapshots_org_time', MetricsSnapshot.organization_id, MetricsSnapshot.snapshot_time)
Index('idx_ai_insights_org_priority', AIInsight.organization_id, AIInsight.priority)
Index('idx_notifications_user_unread', Notification.user_id, Notification.read)
Index('idx_reports_org_status', Report.organization_id, Report.status)
Index('idx_alerts_org_active', Alert.organization_id, Alert.status)
Index('idx_system_health_service_time', SystemHealthCheck.service_name, SystemHealthCheck.check_time)