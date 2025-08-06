# src/models/metrics.py
"""
Metrics Database Models
Models for metrics storage and analytics
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .dashboard import Base

class MetricDefinition(Base):
    """Custom metric definitions"""
    __tablename__ = "metric_definitions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Metric definition
    name = Column(String(100), nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text)
    unit = Column(String(50))
    data_type = Column(String(20), default="float")  # float, integer, boolean, string
    category = Column(String(50))
    
    # Calculation
    formula = Column(Text)  # For calculated metrics
    data_sources = Column(JSON)
    aggregation_method = Column(String(20))  # sum, avg, count, max, min
    refresh_frequency = Column(Integer, default=300)  # seconds
    
    # Display
    icon = Column(String(50))
    color = Column(String(20))
    chart_type = Column(String(20))  # line, bar, pie, gauge
    
    # Status
    enabled = Column(Boolean, default=True)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class MetricValue(Base):
    """Individual metric values over time"""
    __tablename__ = "metric_values"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    
    # Value data
    value = Column(Float, nullable=False)
    string_value = Column(String(255))  # For non-numeric values
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Context
    tags = Column(JSON)  # Key-value pairs for filtering
    metadata = Column(JSON)  # Additional context
    source = Column(String(100))  # Data source
    
    # Quality
    confidence = Column(Float, default=1.0)  # 0.0-1.0
    is_anomaly = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class MetricAlert(Base):
    """Metric-based alert rules"""
    __tablename__ = "metric_alerts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Alert rule
    name = Column(String(255), nullable=False)
    description = Column(Text)
    metric_name = Column(String(100), nullable=False)
    condition = Column(String(20), nullable=False)  # gt, lt, eq, ne, gte, lte
    threshold_value = Column(Float, nullable=False)
    
    # Severity and priority
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    priority = Column(Integer, default=5)  # 1-10
    
    # Evaluation
    evaluation_window = Column(Integer, default=300)  # seconds
    evaluation_frequency = Column(Integer, default=60)  # seconds
    consecutive_breaches = Column(Integer, default=1)
    
    # Actions
    notification_channels = Column(JSON)
    auto_actions = Column(JSON)
    escalation_rules = Column(JSON)
    
    # Status
    enabled = Column(Boolean, default=True)
    last_evaluated = Column(DateTime)
    last_triggered = Column(DateTime)
    trigger_count = Column(Integer, default=0)
    
    # Metadata
    created_by = Column(UUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# ===================================

# src/models/reports.py  
"""
Reports Database Models
Models for report generation and scheduling
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Text, LargeBinary
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from .dashboard import Base

class ReportTemplate(Base):
    """Report templates for reusable reports"""
    __tablename__ = "report_templates"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Template definition
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    report_type = Column(String(50), nullable=False)
    version = Column(String(20), default="1.0")
    
    # Configuration
    default_format = Column(String(20), default="pdf")
    default_parameters = Column(JSON)
    required_parameters = Column(JSON)
    optional_parameters = Column(JSON)
    
    # Layout
    sections = Column(JSON)
    layout_config = Column(JSON)
    styling_config = Column(JSON)
    
    # Metadata
    tags = Column(JSON)
    preview_image_url = Column(String(500))
    is_premium = Column(Boolean, default=False)
    is_public = Column(Boolean, default=True)
    
    # Usage stats
    usage_count = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    
    # Lifecycle
    created_by = Column(UUID(as_uuid=True))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReportExecution(Base):
    """Report execution logs and history"""
    __tablename__ = "report_executions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    report_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Execution details
    execution_type = Column(String(20), default="manual")  # manual, scheduled, api
    trigger_source = Column(String(100))
    parameters_used = Column(JSON)
    
    # Performance
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    duration_seconds = Column(Float)
    memory_usage_mb = Column(Float)
    cpu_usage_percent = Column(Float)
    
    # Results
    status = Column(String(20), nullable=False)  # success, failed, timeout, cancelled
    records_processed = Column(Integer)
    output_size_bytes = Column(Integer)
    error_details = Column(JSON)
    
    # Quality metrics
    data_quality_score = Column(Float)  # 0.0-1.0
    completeness_score = Column(Float)  # 0.0-1.0
    
    created_at = Column(DateTime, default=datetime.utcnow)

class ExportJob(Base):
    """Data export job tracking"""
    __tablename__ = "export_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Export configuration
    export_type = Column(String(50), nullable=False)  # dashboard, metrics, reports, custom
    format = Column(String(20), nullable=False)
    data_sources = Column(JSON)
    filters = Column(JSON)
    date_range = Column(JSON)
    
    # Processing
    status = Column(String(20), default="pending")
    progress_percentage = Column(Float, default=0.0)
    current_step = Column(String(100))
    total_steps = Column(Integer)
    
    # Output
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size_bytes = Column(Integer)
    file_hash = Column(String(64))
    download_url = Column(String(500))
    
    # Lifecycle
    scheduled_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime)
    downloaded_at = Column(DateTime)
    download_count = Column(Integer, default=0)
    
    # Error handling
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ReportSubscription(Base):
    """Report subscriptions for automated delivery"""
    __tablename__ = "report_subscriptions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    
    # Subscription details
    name = Column(String(255), nullable=False)
    description = Column(Text)
    report_type = Column(String(50), nullable=False)
    template_id = Column(UUID(as_uuid=True))
    
    # Schedule
    frequency = Column(String(20), nullable=False)  # daily, weekly, monthly, quarterly
    schedule_config = Column(JSON)  # Cron-like config
    timezone = Column(String(50), default="UTC")
    
    # Delivery
    delivery_methods = Column(JSON)  # email, webhook, storage, api
    recipients = Column(JSON)
    delivery_config = Column(JSON)
    
    # Parameters
    report_parameters = Column(JSON)
    filters = Column(JSON)
    format_preferences = Column(JSON)
    
    # Status
    enabled = Column(Boolean, default=True)
    paused = Column(Boolean, default=False)
    last_delivery = Column(DateTime)
    next_delivery = Column(DateTime)
    delivery_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    
    # Metadata
    tags = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)