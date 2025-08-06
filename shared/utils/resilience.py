"""
Circuit Breaker and Resilience Patterns
Implements circuit breaker, retry logic, and bulkhead isolation for service resilience
"""

import asyncio
import time
import logging
from typing import Callable, Any, Optional, Dict, List
from enum import Enum
from dataclasses import dataclass, field
from functools import wraps
import aiohttp
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"        # Normal operation
    OPEN = "open"           # Failing, blocking requests
    HALF_OPEN = "half_open" # Testing if service recovered

@dataclass
class CircuitBreakerStats:
    """Statistics for circuit breaker"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    consecutive_failures: int = 0
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    state_changes: List[tuple] = field(default_factory=list)

class CircuitBreaker:
    """Circuit breaker implementation for external service calls"""
    
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception,
        success_threshold: int = 3,
        timeout: float = 30.0
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        self.success_threshold = success_threshold
        self.timeout = timeout
        
        self.state = CircuitState.CLOSED
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if self._should_attempt_reset():
                    self._change_state(CircuitState.HALF_OPEN)
                else:
                    raise Exception(f"Circuit breaker '{self.name}' is OPEN")
            
            self.stats.total_requests += 1
            
        try:
            # Execute with timeout
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=self.timeout)
            await self._on_success()
            return result
            
        except self.expected_exception as e:
            await self._on_failure()
            raise e
        except asyncio.TimeoutError:
            await self._on_failure()
            raise Exception(f"Timeout after {self.timeout}s")
    
    async def _on_success(self):
        """Handle successful execution"""
        async with self._lock:
            self.stats.successful_requests += 1
            self.stats.consecutive_failures = 0
            self.stats.last_success_time = datetime.utcnow()
            
            if self.state == CircuitState.HALF_OPEN:
                if self.stats.successful_requests >= self.success_threshold:
                    self._change_state(CircuitState.CLOSED)
    
    async def _on_failure(self):
        """Handle failed execution"""
        async with self._lock:
            self.stats.failed_requests += 1
            self.stats.consecutive_failures += 1
            self.stats.last_failure_time = datetime.utcnow()
            
            if (self.state == CircuitState.CLOSED and 
                self.stats.consecutive_failures >= self.failure_threshold):
                self._change_state(CircuitState.OPEN)
            elif self.state == CircuitState.HALF_OPEN:
                self._change_state(CircuitState.OPEN)
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit should attempt to reset"""
        if self.stats.last_failure_time is None:
            return True
        
        time_since_failure = datetime.utcnow() - self.stats.last_failure_time
        return time_since_failure.total_seconds() >= self.recovery_timeout
    
    def _change_state(self, new_state: CircuitState):
        """Change circuit state and log"""
        old_state = self.state
        self.state = new_state
        self.stats.state_changes.append((old_state, new_state, datetime.utcnow()))
        
        logger.info(f"Circuit breaker '{self.name}' changed from {old_state.value} to {new_state.value}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get circuit breaker statistics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "total_requests": self.stats.total_requests,
            "successful_requests": self.stats.successful_requests,
            "failed_requests": self.stats.failed_requests,
            "success_rate": (
                self.stats.successful_requests / self.stats.total_requests 
                if self.stats.total_requests > 0 else 0
            ),
            "consecutive_failures": self.stats.consecutive_failures,
            "last_failure_time": self.stats.last_failure_time,
            "last_success_time": self.stats.last_success_time
        }

class RetryPolicy:
    """Retry policy with exponential backoff and jitter"""
    
    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
        retryable_exceptions: tuple = (Exception,)
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt"""
        delay = self.base_delay * (self.exponential_base ** attempt)
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            # Add jitter to prevent thundering herd
            jitter_range = delay * 0.1
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0, delay)
    
    def should_retry(self, exception: Exception, attempt: int) -> bool:
        """Check if should retry based on exception and attempt count"""
        if attempt >= self.max_attempts:
            return False
        
        return isinstance(exception, self.retryable_exceptions)

async def retry_with_policy(policy: RetryPolicy, func: Callable, *args, **kwargs) -> Any:
    """Execute function with retry policy"""
    last_exception = None
    
    for attempt in range(policy.max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            
            if not policy.should_retry(e, attempt):
                logger.error(f"Max retries exceeded or non-retryable exception: {str(e)}")
                raise e
            
            if attempt < policy.max_attempts - 1:  # Don't delay on last attempt
                delay = policy.calculate_delay(attempt)
                logger.warning(f"Attempt {attempt + 1} failed, retrying in {delay:.2f}s: {str(e)}")
                await asyncio.sleep(delay)
    
    # This should never be reached, but just in case
    raise last_exception

class BulkheadIsolation:
    """Bulkhead isolation pattern to limit resource usage"""
    
    def __init__(self, name: str, max_concurrent: int = 10):
        self.name = name
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.active_requests = 0
        self.total_requests = 0
        self.rejected_requests = 0
    
    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with bulkhead isolation"""
        self.total_requests += 1
        
        try:
            # Try to acquire semaphore (non-blocking)
            acquired = self.semaphore.acquire_nowait()
            if not acquired:
                self.rejected_requests += 1
                raise Exception(f"Bulkhead '{self.name}' is at capacity ({self.max_concurrent})")
            
            self.active_requests += 1
            try:
                return await func(*args, **kwargs)
            finally:
                self.active_requests -= 1
                self.semaphore.release()
                
        except Exception as e:
            logger.warning(f"Bulkhead '{self.name}' rejected request: {str(e)}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        """Get bulkhead statistics"""
        return {
            "name": self.name,
            "max_concurrent": self.max_concurrent,
            "active_requests": self.active_requests,
            "total_requests": self.total_requests,
            "rejected_requests": self.rejected_requests,
            "rejection_rate": (
                self.rejected_requests / self.total_requests 
                if self.total_requests > 0 else 0
            )
        }

class ResilientServiceClient:
    """Service client with circuit breaker, retry, and bulkhead patterns"""
    
    def __init__(self, service_name: str, base_url: str):
        self.service_name = service_name
        self.base_url = base_url.rstrip("/")
        
        # Initialize resilience components
        self.circuit_breaker = CircuitBreaker(
            name=f"{service_name}_circuit",
            failure_threshold=5,
            recovery_timeout=60
        )
        
        self.retry_policy = RetryPolicy(
            max_attempts=3,
            base_delay=1.0,
            retryable_exceptions=(aiohttp.ClientError, asyncio.TimeoutError)
        )
        
        self.bulkhead = BulkheadIsolation(
            name=f"{service_name}_bulkhead",
            max_concurrent=10
        )
        
        # HTTP session
        self.session = None
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self.session is None or self.session.closed:
            connector = aiohttp.TCPConnector(
                limit=100,
                limit_per_host=20,
                ttl_dns_cache=300,
                use_dns_cache=True,
            )
            
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout,
                headers={"User-Agent": f"VocelioServiceClient/{self.service_name}"}
            )
        
        return self.session
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make HTTP request with resilience patterns"""
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        
        async def _request():
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                return response
        
        # Apply bulkhead isolation
        return await self.bulkhead.execute(
            lambda: self.circuit_breaker.call(
                lambda: retry_with_policy(self.retry_policy, _request)
            )
        )
    
    async def get(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make GET request"""
        return await self._make_request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make POST request"""
        return await self._make_request("POST", endpoint, **kwargs)
    
    async def put(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make PUT request"""
        return await self._make_request("PUT", endpoint, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> aiohttp.ClientResponse:
        """Make DELETE request"""
        return await self._make_request("DELETE", endpoint, **kwargs)
    
    async def close(self):
        """Close HTTP session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def get_health_stats(self) -> Dict[str, Any]:
        """Get comprehensive health statistics"""
        return {
            "service_name": self.service_name,
            "base_url": self.base_url,
            "circuit_breaker": self.circuit_breaker.get_stats(),
            "bulkhead": self.bulkhead.get_stats()
        }

# Decorators for easy use
def circuit_breaker(
    name: str,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    timeout: float = 30.0
):
    """Decorator to add circuit breaker to function"""
    cb = CircuitBreaker(name, failure_threshold, recovery_timeout, timeout=timeout)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await cb.call(func, *args, **kwargs)
        return wrapper
    return decorator

def retry_on_failure(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    retryable_exceptions: tuple = (Exception,)
):
    """Decorator to add retry logic to function"""
    policy = RetryPolicy(max_attempts, base_delay, retryable_exceptions=retryable_exceptions)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await retry_with_policy(policy, func, *args, **kwargs)
        return wrapper
    return decorator

def bulkhead_isolate(name: str, max_concurrent: int = 10):
    """Decorator to add bulkhead isolation to function"""
    bulkhead = BulkheadIsolation(name, max_concurrent)
    
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await bulkhead.execute(func, *args, **kwargs)
        return wrapper
    return decorator
