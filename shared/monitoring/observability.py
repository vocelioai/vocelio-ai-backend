"""
Comprehensive Observability and Monitoring System
Centralized logging, metrics collection, tracing, and alerting
"""

import logging
import json
import time
import asyncio
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
from enum import Enum
import uuid
import structlog
from functools import wraps
import psutil
import aiohttp

class LogLevel(str, Enum):
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class MetricType(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

@dataclass
class TraceSpan:
    """Distributed tracing span"""
    trace_id: str
    span_id: str
    parent_span_id: Optional[str]
    operation_name: str
    service_name: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: Optional[float] = None
    tags: Dict[str, Any] = field(default_factory=dict)
    logs: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "ok"
    error: Optional[str] = None

@dataclass
class Metric:
    """System metric"""
    name: str
    value: float
    metric_type: MetricType
    labels: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    help_text: str = ""

class StructuredLogger:
    """Enhanced structured logging with context"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = self._setup_logger()
        self.context_stack = []
    
    def _setup_logger(self) -> structlog.stdlib.BoundLogger:
        """Setup structured logger"""
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.StackInfoRenderer(),
                structlog.dev.set_exc_info,
                structlog.processors.JSONRenderer()
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        return structlog.get_logger(service=self.service_name)
    
    def add_context(self, **kwargs):
        """Add context to all subsequent logs"""
        self.context_stack.append(kwargs)
        return self.logger.bind(**kwargs)
    
    @asynccontextmanager
    async def context(self, **kwargs):
        """Context manager for temporary context"""
        self.context_stack.append(kwargs)
        try:
            yield self.logger.bind(**kwargs)
        finally:
            if self.context_stack:
                self.context_stack.pop()
    
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self._log(LogLevel.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        """Log info message"""
        self._log(LogLevel.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self._log(LogLevel.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message"""
        self._log(LogLevel.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message"""
        self._log(LogLevel.CRITICAL, message, **kwargs)
    
    def _log(self, level: LogLevel, message: str, **kwargs):
        """Internal log method with context"""
        # Merge all context
        context = {}
        for ctx in self.context_stack:
            context.update(ctx)
        context.update(kwargs)
        
        # Add standard fields
        context.update({
            "timestamp": datetime.utcnow().isoformat(),
            "service": self.service_name,
            "level": level.value
        })
        
        getattr(self.logger, level.value)(message, **context)

class MetricsCollector:
    """Metrics collection and aggregation"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.metrics: Dict[str, Metric] = {}
        self._counters: Dict[str, float] = {}
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = {}
        
    def counter(self, name: str, value: float = 1.0, labels: Dict[str, str] = None):
        """Increment counter metric"""
        labels = labels or {}
        key = f"{name}:{self._labels_to_string(labels)}"
        
        self._counters[key] = self._counters.get(key, 0) + value
        
        self.metrics[key] = Metric(
            name=name,
            value=self._counters[key],
            metric_type=MetricType.COUNTER,
            labels=labels
        )
    
    def gauge(self, name: str, value: float, labels: Dict[str, str] = None):
        """Set gauge metric"""
        labels = labels or {}
        key = f"{name}:{self._labels_to_string(labels)}"
        
        self._gauges[key] = value
        
        self.metrics[key] = Metric(
            name=name,
            value=value,
            metric_type=MetricType.GAUGE,
            labels=labels
        )
    
    def histogram(self, name: str, value: float, labels: Dict[str, str] = None):
        """Add value to histogram"""
        labels = labels or {}
        key = f"{name}:{self._labels_to_string(labels)}"
        
        if key not in self._histograms:
            self._histograms[key] = []
        
        self._histograms[key].append(value)
        
        # Calculate percentiles
        values = sorted(self._histograms[key])
        count = len(values)
        
        self.metrics[f"{key}_count"] = Metric(
            name=f"{name}_count",
            value=count,
            metric_type=MetricType.COUNTER,
            labels=labels
        )
        
        if count > 0:
            self.metrics[f"{key}_sum"] = Metric(
                name=f"{name}_sum",
                value=sum(values),
                metric_type=MetricType.COUNTER,
                labels=labels
            )
            
            # Percentiles
            for p in [50, 90, 95, 99]:
                idx = int((p / 100) * count) - 1
                idx = max(0, min(idx, count - 1))
                
                self.metrics[f"{key}_p{p}"] = Metric(
                    name=f"{name}_p{p}",
                    value=values[idx],
                    metric_type=MetricType.GAUGE,
                    labels=labels
                )
    
    def timing(self, name: str, duration_ms: float, labels: Dict[str, str] = None):
        """Record timing metric"""
        self.histogram(f"{name}_duration_ms", duration_ms, labels)
    
    def _labels_to_string(self, labels: Dict[str, str]) -> str:
        """Convert labels to string for keying"""
        return ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
    
    def get_metrics(self) -> List[Metric]:
        """Get all current metrics"""
        return list(self.metrics.values())
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.metrics.clear()
        self._counters.clear()
        self._gauges.clear()
        self._histograms.clear()

class DistributedTracer:
    """Distributed tracing implementation"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.spans: Dict[str, TraceSpan] = {}
        self.active_spans: List[str] = []
    
    def start_span(
        self,
        operation_name: str,
        parent_span_id: Optional[str] = None,
        tags: Dict[str, Any] = None
    ) -> TraceSpan:
        """Start a new trace span"""
        # Generate IDs
        if not parent_span_id and not self.active_spans:
            trace_id = str(uuid.uuid4())
        else:
            # Use trace ID from parent or current active span
            parent_id = parent_span_id or (self.active_spans[-1] if self.active_spans else None)
            if parent_id and parent_id in self.spans:
                trace_id = self.spans[parent_id].trace_id
            else:
                trace_id = str(uuid.uuid4())
        
        span_id = str(uuid.uuid4())
        
        span = TraceSpan(
            trace_id=trace_id,
            span_id=span_id,
            parent_span_id=parent_span_id,
            operation_name=operation_name,
            service_name=self.service_name,
            start_time=datetime.utcnow(),
            tags=tags or {}
        )
        
        self.spans[span_id] = span
        self.active_spans.append(span_id)
        
        return span
    
    def finish_span(self, span_id: str, error: Optional[str] = None):
        """Finish a trace span"""
        if span_id not in self.spans:
            return
        
        span = self.spans[span_id]
        span.end_time = datetime.utcnow()
        span.duration_ms = (span.end_time - span.start_time).total_seconds() * 1000
        
        if error:
            span.status = "error"
            span.error = error
        
        # Remove from active spans
        if span_id in self.active_spans:
            self.active_spans.remove(span_id)
    
    def add_span_log(self, span_id: str, message: str, **kwargs):
        """Add log to span"""
        if span_id in self.spans:
            self.spans[span_id].logs.append({
                "timestamp": datetime.utcnow().isoformat(),
                "message": message,
                **kwargs
            })
    
    def add_span_tag(self, span_id: str, key: str, value: Any):
        """Add tag to span"""
        if span_id in self.spans:
            self.spans[span_id].tags[key] = value
    
    @asynccontextmanager
    async def trace(self, operation_name: str, **tags):
        """Context manager for tracing"""
        span = self.start_span(operation_name, tags=tags)
        try:
            yield span
        except Exception as e:
            self.finish_span(span.span_id, error=str(e))
            raise
        else:
            self.finish_span(span.span_id)
    
    def get_trace(self, trace_id: str) -> List[TraceSpan]:
        """Get all spans for a trace"""
        return [span for span in self.spans.values() if span.trace_id == trace_id]

class SystemMonitor:
    """System resource monitoring"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.metrics_collector = MetricsCollector(service_name)
    
    def collect_system_metrics(self):
        """Collect system-level metrics"""
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        self.metrics_collector.gauge("system_cpu_percent", cpu_percent)
        
        # Memory metrics
        memory = psutil.virtual_memory()
        self.metrics_collector.gauge("system_memory_percent", memory.percent)
        self.metrics_collector.gauge("system_memory_used_bytes", memory.used)
        self.metrics_collector.gauge("system_memory_available_bytes", memory.available)
        
        # Disk metrics
        disk = psutil.disk_usage('/')
        self.metrics_collector.gauge("system_disk_percent", disk.percent)
        self.metrics_collector.gauge("system_disk_used_bytes", disk.used)
        self.metrics_collector.gauge("system_disk_free_bytes", disk.free)
        
        # Network metrics
        network = psutil.net_io_counters()
        self.metrics_collector.counter("system_network_bytes_sent", network.bytes_sent)
        self.metrics_collector.counter("system_network_bytes_recv", network.bytes_recv)
        
        # Process metrics
        process = psutil.Process()
        self.metrics_collector.gauge("process_cpu_percent", process.cpu_percent())
        self.metrics_collector.gauge("process_memory_percent", process.memory_percent())
        self.metrics_collector.gauge("process_num_threads", process.num_threads())

class ObservabilityManager:
    """Central observability management"""
    
    def __init__(self, service_name: str):
        self.service_name = service_name
        self.logger = StructuredLogger(service_name)
        self.metrics = MetricsCollector(service_name)
        self.tracer = DistributedTracer(service_name)
        self.monitor = SystemMonitor(service_name)
        
        # Background tasks
        self._monitoring_task = None
        self._is_monitoring = False
    
    async def start_monitoring(self, interval: int = 60):
        """Start background monitoring"""
        self._is_monitoring = True
        self._monitoring_task = asyncio.create_task(self._monitoring_loop(interval))
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self._is_monitoring = False
        if self._monitoring_task:
            self._monitoring_task.cancel()
            try:
                await self._monitoring_task
            except asyncio.CancelledError:
                pass
    
    async def _monitoring_loop(self, interval: int):
        """Background monitoring loop"""
        while self._is_monitoring:
            try:
                self.monitor.collect_system_metrics()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error("Error in monitoring loop", error=str(e))
                await asyncio.sleep(interval)
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status"""
        metrics = self.metrics.get_metrics()
        
        # Calculate health score based on metrics
        health_score = 100.0
        warnings = []
        
        for metric in metrics:
            if metric.name == "system_cpu_percent" and metric.value > 80:
                health_score -= 20
                warnings.append("High CPU usage")
            elif metric.name == "system_memory_percent" and metric.value > 80:
                health_score -= 20
                warnings.append("High memory usage")
            elif metric.name == "system_disk_percent" and metric.value > 90:
                health_score -= 30
                warnings.append("Low disk space")
        
        status = "healthy"
        if health_score < 70:
            status = "unhealthy"
        elif health_score < 90:
            status = "degraded"
        
        return {
            "service": self.service_name,
            "status": status,
            "health_score": health_score,
            "warnings": warnings,
            "timestamp": datetime.utcnow().isoformat(),
            "metrics_count": len(metrics),
            "active_spans": len(self.tracer.active_spans)
        }

# Decorators for observability
def observe_function(operation_name: str = None):
    """Decorator to add observability to functions"""
    def decorator(func):
        op_name = operation_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get observability manager from context or create new one
            obs = getattr(async_wrapper, '_observability', None)
            if not obs:
                obs = ObservabilityManager("unknown_service")
            
            async with obs.tracer.trace(op_name) as span:
                start_time = time.time()
                
                try:
                    result = await func(*args, **kwargs)
                    obs.metrics.counter(f"{op_name}_success")
                    return result
                except Exception as e:
                    obs.metrics.counter(f"{op_name}_error")
                    obs.logger.error(f"Error in {op_name}", error=str(e))
                    raise
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    obs.metrics.timing(op_name, duration_ms)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # For sync functions, just add metrics
            obs = getattr(sync_wrapper, '_observability', None)
            if not obs:
                obs = ObservabilityManager("unknown_service")
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                obs.metrics.counter(f"{op_name}_success")
                return result
            except Exception as e:
                obs.metrics.counter(f"{op_name}_error")
                obs.logger.error(f"Error in {op_name}", error=str(e))
                raise
            finally:
                duration_ms = (time.time() - start_time) * 1000
                obs.metrics.timing(op_name, duration_ms)
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Global observability manager
_global_observability: Dict[str, ObservabilityManager] = {}

def get_observability(service_name: str) -> ObservabilityManager:
    """Get or create observability manager for service"""
    if service_name not in _global_observability:
        _global_observability[service_name] = ObservabilityManager(service_name)
    return _global_observability[service_name]
