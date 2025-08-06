"""
Reports Schemas
Pydantic models for reports and data export structures
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ReportStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExportFormat(str, Enum):
    PDF = "pdf"
    EXCEL = "excel"
    CSV = "csv"
    JSON = "json"

class ReportType(str, Enum):
    DASHBOARD_SUMMARY = "dashboard_summary"
    METRICS_ANALYSIS = "metrics_analysis"
    PERFORMANCE_REPORT = "performance_report"
    AGENT_PERFORMANCE = "agent_performance"
    CAMPAIGN_ANALYSIS = "campaign_analysis"
    REVENUE_REPORT = "revenue_report"
    CUSTOM_QUERY = "custom_query"
    COMPLIANCE_REPORT = "compliance_report"
    SYSTEM_HEALTH = "system_health"

class ScheduleFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"

class ReportRequest(BaseModel):
    """Report generation request"""
    report_type: ReportType
    format: ExportFormat = ExportFormat.PDF
    parameters: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    time_range: str = "30d"
    include_charts: bool = True
    include_raw_data: bool = False
    custom_title: Optional[str] = None
    sections: List[str] = Field(default_factory=list)
    email_delivery: bool = False
    recipient_emails: List[str] = Field(default_factory=list)

class ReportResponse(BaseModel):
    """Report generation response"""
    report_id: str
    status: ReportStatus
    message: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_completion_time: Optional[datetime] = None
    download_url: Optional[str] = None
    file_size: Optional[int] = None
    file_format: Optional[ExportFormat] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None

class ScheduledReportRequest(BaseModel):
    """Scheduled report request"""
    report_type: ReportType
    format: ExportFormat = ExportFormat.PDF
    frequency: ScheduleFrequency
    parameters: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    schedule_time: str = Field(..., description="Time in HH:MM format")
    timezone: str = "UTC"
    recipient_emails: List[str]
    report_name: str
    description: Optional[str] = None
    enabled: bool = True

class ScheduledReport(BaseModel):
    """Scheduled report model"""
    id: str
    organization_id: str
    user_id: str
    report_type: ReportType
    format: ExportFormat
    frequency: ScheduleFrequency
    schedule_time: str
    timezone: str
    recipient_emails: List[str]
    report_name: str
    description: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0
    created_at: datetime
    updated_at: datetime

class ReportTemplate(BaseModel):
    """Report template model"""
    id: str
    name: str
    description: str
    category: str
    report_type: ReportType
    default_format: ExportFormat
    default_parameters: Dict[str, Any] = Field(default_factory=dict)
    required_parameters: List[str] = Field(default_factory=list)
    sections: List[str] = Field(default_factory=list)
    preview_image_url: Optional[str] = None
    is_premium: bool = False
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

class ExportConfiguration(BaseModel):
    """Export configuration options"""
    format: ExportFormat
    include_headers: bool = True
    include_footer: bool = True
    include_charts: bool = True
    include_raw_data: bool = False
    page_orientation: str = "portrait"  # portrait, landscape
    paper_size: str = "A4"  # A4, letter, legal
    font_size: int = 10
    margins: Dict[str, int] = Field(default_factory=lambda: {"top": 20, "bottom": 20, "left": 20, "right": 20})
    watermark_text: Optional[str] = None
    custom_styling: Dict[str, Any] = Field(default_factory=dict)

class ReportSection(BaseModel):
    """Report section definition"""
    section_id: str
    title: str
    description: Optional[str] = None
    section_type: str = Field(..., description="summary, chart, table, text, image")
    data_source: str
    configuration: Dict[str, Any] = Field(default_factory=dict)
    order: int = 0
    visible: bool = True
    required: bool = False

class DashboardExportRequest(BaseModel):
    """Dashboard data export request"""
    format: ExportFormat = ExportFormat.CSV
    time_range: str = "30d"
    include_charts: bool = False
    include_insights: bool = True
    include_metrics: bool = True
    include_agents: bool = True
    include_campaigns: bool = True
    custom_filters: Dict[str, Any] = Field(default_factory=dict)
    email_delivery: bool = False
    recipient_email: Optional[str] = None

class MetricsExportData(BaseModel):
    """Metrics export data structure"""
    timestamp: datetime
    metric_name: str
    metric_value: float
    metric_unit: str
    category: str
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentPerformanceExportData(BaseModel):
    """Agent performance export data"""
    agent_id: str
    agent_name: str
    total_calls: int
    successful_calls: int
    success_rate: float
    revenue_generated: float
    average_call_duration: int
    utilization_rate: float
    customer_rating: Optional[float] = None
    period_start: datetime
    period_end: datetime

class CampaignExportData(BaseModel):
    """Campaign export data"""
    campaign_id: str
    campaign_name: str
    status: str
    start_date: datetime
    end_date: Optional[datetime] = None
    total_calls: int
    successful_calls: int
    success_rate: float
    conversion_rate: float
    revenue_generated: float
    cost: float
    roi: float
    target_audience: str
    industry: str

class ComplianceReportData(BaseModel):
    """Compliance report data"""
    organization_id: str
    report_period: str
    gdpr_compliance_score: float = Field(..., ge=0.0, le=100.0)
    tcpa_compliance_score: float = Field(..., ge=0.0, le=100.0)
    dnc_compliance_score: float = Field(..., ge=0.0, le=100.0)
    recording_consent_rate: float = Field(..., ge=0.0, le=100.0)
    data_retention_compliance: float = Field(..., ge=0.0, le=100.0)
    violations_count: int
    violations_resolved: int
    audit_trail_entries: int
    consent_records: int
    opt_out_requests: int
    data_deletion_requests: int

class SystemHealthReportData(BaseModel):
    """System health report data"""
    service_name: str
    uptime_percentage: float = Field(..., ge=0.0, le=100.0)
    average_response_time: float
    error_rate: float = Field(..., ge=0.0, le=100.0)
    throughput: float
    cpu_usage: float = Field(..., ge=0.0, le=100.0)
    memory_usage: float = Field(..., ge=0.0, le=100.0)
    disk_usage: float = Field(..., ge=0.0, le=100.0)
    network_latency: float
    incidents_count: int
    resolved_incidents: int
    maintenance_windows: int
    report_period: str

class CustomQueryRequest(BaseModel):
    """Custom query request for reports"""
    query_name: str
    description: Optional[str] = None
    sql_query: Optional[str] = None
    api_endpoints: List[str] = Field(default_factory=list)
    data_sources: List[str] = Field(default_factory=list)
    filters: Dict[str, Any] = Field(default_factory=dict)
    aggregations: List[str] = Field(default_factory=list)
    group_by: List[str] = Field(default_factory=list)
    sort_by: List[Dict[str, str]] = Field(default_factory=list)
    limit: Optional[int] = None
    format: ExportFormat = ExportFormat.JSON

class ReportAnalytics(BaseModel):
    """Report usage analytics"""
    report_id: Optional[str] = None
    report_type: ReportType
    generation_count: int
    total_downloads: int
    average_generation_time: float
    success_rate: float = Field(..., ge=0.0, le=100.0)
    popular_formats: List[Dict[str, Any]]
    user_feedback_score: Optional[float] = None
    most_requested_sections: List[str]
    error_categories: Dict[str, int] = Field(default_factory=dict)
    performance_metrics: Dict[str, float] = Field(default_factory=dict)

class BulkExportRequest(BaseModel):
    """Bulk export request for multiple reports"""
    export_requests: List[ReportRequest]
    archive_format: str = "zip"  # zip, tar
    notification_email: Optional[str] = None
    priority: str = "normal"  # low, normal, high
    retention_days: int = 7
    encryption_enabled: bool = False

class ReportSummary(BaseModel):
    """Report summary statistics"""
    organization_id: str
    period: str
    total_reports_generated: int
    successful_reports: int
    failed_reports: int
    most_popular_format: ExportFormat
    most_popular_type: ReportType
    total_data_exported_mb: float
    average_generation_time: float
    user_satisfaction_score: Optional[float] = None
    cost_breakdown: Dict[str, float] = Field(default_factory=dict)