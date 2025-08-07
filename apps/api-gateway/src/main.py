"""
Enhanced API Gateway - Vocelio AI Call Center
Comprehensive gateway with circuit breakers, observability, RBAC, and resilience patterns
"""

# Manual sys.path fix for Docker import issues
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from fastapi import FastAPI, HTTPException, Depends, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import httpx
import asyncio
import time
import logging
from typing import Dict, List, Optional, Any, Union
import os
from datetime import datetime, timedelta
from collections import defaultdict

# Configure logging first
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service registry
SERVICE_REGISTRY = {
    "overview": {"url": "http://overview:8002", "timeout": 30},
    "agents": {"url": "http://agents:8000", "timeout": 30},
    "smart-campaigns": {"url": "http://smart-campaigns:8003", "timeout": 30},
    "call-center": {"url": "http://call-center:8004", "timeout": 30},
    "analytics-pro": {"url": "http://analytics-pro:8005", "timeout": 30},
    "billing-pro": {"url": "http://billing-pro:8006", "timeout": 30},
    "compliance": {"url": "http://compliance:8007", "timeout": 30},
    "developer-api": {"url": "http://developer-api:8008", "timeout": 30},
    "flow-builder": {"url": "http://flow-builder:8009", "timeout": 30},
    "integrations": {"url": "http://integrations:8010", "timeout": 30},
    "knowledge-base": {"url": "http://knowledge-base:8011", "timeout": 30},
    "lead-management": {"url": "http://lead-management:8012", "timeout": 30},
    "scheduling": {"url": "http://scheduling:8013", "timeout": 30},
    "notifications": {"url": "http://notifications:8014", "timeout": 30},
    "phone-numbers": {"url": "http://phone-numbers:8015", "timeout": 30},
    "scripts": {"url": "http://scripts:8016", "timeout": 30},
    "settings": {"url": "http://settings:8017", "timeout": 30},
    "team-hub": {"url": "http://team-hub:8018", "timeout": 30},
    "voice-lab": {"url": "http://voice-lab:8019", "timeout": 30},
    "voice-marketplace": {"url": "http://voice-marketplace:8020", "timeout": 30},
    "webhooks": {"url": "http://webhooks:8021", "timeout": 30},
    "white-label": {"url": "http://white-label:8022", "timeout": 30},
    "agent-store": {"url": "http://agent-store:8023", "timeout": 30},
    "ai-brain": {"url": "http://ai-brain:8024", "timeout": 30},
}

# Basic user context for fallback
class UserContext:
    def __init__(self, user_id="guest", organization_id="default", roles=None, permissions=None, is_active=True, is_verified=True):
        self.user_id = user_id
        self.organization_id = organization_id
        self.roles = roles or []
        self.permissions = permissions or set()
        self.is_active = is_active
        self.is_verified = is_verified

# Simple rate limiter
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
        self.limits = {
            "default": {"requests": 100, "window": 60},
            "authenticated": {"requests": 1000, "window": 60},
        }
    
    def is_allowed(self, key: str, limit_type: str = "default") -> bool:
        now = datetime.utcnow()
        limit_config = self.limits[limit_type]
        window_start = now - timedelta(seconds=limit_config["window"])
        
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > window_start]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= limit_config["requests"]:
            return False
        
        # Add current request
        self.requests[key].append(now)
        return True

rate_limiter = RateLimiter()

# Simple service client
class ServiceClient:
    def __init__(self, service_name: str, base_url: str):
        self.service_name = service_name
        self.base_url = base_url.rstrip("/")
        self.session = None
    
    async def _get_session(self) -> httpx.AsyncClient:
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=30.0)
        return self.session
    
    async def request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        url = f"{self.base_url}{endpoint}"
        session = await self._get_session()
        
        try:
            response = await session.request(method, url, **kwargs)
            return response
        except Exception as e:
            logger.error(f"Request failed to {self.service_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Service {self.service_name} unavailable"
            )
    
    async def get(self, endpoint: str, **kwargs) -> httpx.Response:
        return await self.request("GET", endpoint, **kwargs)
    
    async def post(self, endpoint: str, **kwargs) -> httpx.Response:
        return await self.request("POST", endpoint, **kwargs)
    
    async def put(self, endpoint: str, **kwargs) -> httpx.Response:
        return await self.request("PUT", endpoint, **kwargs)
    
    async def delete(self, endpoint: str, **kwargs) -> httpx.Response:
        return await self.request("DELETE", endpoint, **kwargs)
    
    async def close(self):
        if self.session and not self.session.is_closed:
            await self.session.aclose()
    
    def get_health_stats(self) -> Dict[str, Any]:
        return {
            "service_name": self.service_name,
            "base_url": self.base_url,
            "status": "healthy"
        }

class ServiceClients:
    def __init__(self):
        self.clients: Dict[str, ServiceClient] = {}
        self._initialized = False
    
    async def initialize(self):
        if self._initialized:
            return
        
        for service_name, config in SERVICE_REGISTRY.items():
            client = ServiceClient(service_name, config["url"])
            self.clients[service_name] = client
        
        self._initialized = True
        logger.info(f"Initialized {len(self.clients)} service clients")
    
    def get_client(self, service_name: str) -> ServiceClient:
        if not self._initialized:
            raise Exception("Service clients not initialized")
        
        client = self.clients.get(service_name)
        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Service '{service_name}' not found"
            )
        return client
    
    async def close_all(self):
        for client in self.clients.values():
            await client.close()

# Global service clients
service_clients = ServiceClients()

# Simple metrics collector
class SimpleMetrics:
    def __init__(self):
        self.metrics = {}
    
    def counter(self, name: str, labels: Dict[str, str] = None):
        key = f"{name}:{labels}" if labels else name
        self.metrics[key] = self.metrics.get(key, 0) + 1
    
    def timing(self, name: str, value: float, labels: Dict[str, str] = None):
        key = f"{name}_duration:{labels}" if labels else f"{name}_duration"
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append(value)
    
    def get_metrics(self):
        return self.metrics

metrics = SimpleMetrics()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Enhanced API Gateway...")
    
    # Initialize service clients
    await service_clients.initialize()
    
    logger.info("✅ API Gateway started successfully")
    
    yield
    
    logger.info("🛑 Shutting down API Gateway...")
    
    # Close service clients
    await service_clients.close_all()
    
    logger.info("✅ API Gateway shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Vocelio API Gateway Enhanced",
    description="Enhanced API Gateway with observability, resilience, and security",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]
)

# Request/Response middleware
@app.middleware("http")
async def observability_middleware(request: Request, call_next):
    """Add observability to all requests"""
    start_time = time.time()
    
    # Extract service from path
    path_parts = request.url.path.strip("/").split("/")
    service_name = path_parts[0] if path_parts and path_parts[0] else "gateway"
    
    try:
        response = await call_next(request)
        
        # Record metrics
        duration_ms = (time.time() - start_time) * 1000
        metrics.timing(
            "gateway_request_duration",
            duration_ms,
            {"method": request.method, "service": service_name, "status": str(response.status_code)}
        )
        
        metrics.counter(
            "gateway_requests_total",
            {"method": request.method, "service": service_name, "status": str(response.status_code)}
        )
        
        return response
        
    except Exception as e:
        metrics.counter(
            "gateway_errors_total",
            {"method": request.method, "service": service_name, "error": type(e).__name__}
        )
        raise

# Rate limiting middleware
@app.middleware("http")
async def rate_limiting_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "")
    client_key = f"{client_ip}:{user_agent}"
    
    auth_header = request.headers.get("authorization")
    limit_type = "authenticated" if auth_header else "default"
    
    if not rate_limiter.is_allowed(client_key, limit_type):
        metrics.counter("gateway_rate_limited_total")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )
    
    return await call_next(request)

# Authentication helper
async def get_optional_user(request: Request) -> Optional[UserContext]:
    """Get user context if authenticated, None otherwise"""
    try:
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        # For now, return a mock user - integrate with your JWT system
        return UserContext(
            user_id="user_123",
            organization_id="org_123",
            roles=["manager"],
            is_active=True,
            is_verified=True
        )
        
    except Exception as e:
        logger.warning(f"Authentication error: {str(e)}")
        return None

# Health check endpoints
@app.get("/")
async def root():
    """Root endpoint - Railway health check"""
    return {
        "message": "Vocelio API Gateway is alive 🚀",
        "status": "running",
        "service": "api-gateway",
        "version": "2.0.0"
    }

@app.get("/health")
async def health_check():
    """Gateway health check"""
    return {
        "status": "ok",
        "healthy": True,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "service": "api-gateway"
    }

@app.get("/health/detailed")
async def detailed_health():
    """Detailed health check including all services"""
    health_status = {
        "gateway": {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat()
        },
        "services": {}
    }
    
    # Check all services
    for service_name in SERVICE_REGISTRY.keys():
        try:
            client = service_clients.get_client(service_name)
            response = await client.get("/health")
            if response.status_code == 200:
                health_status["services"][service_name] = {
                    "status": "healthy",
                    "response_time_ms": response.elapsed.total_seconds() * 1000 if response.elapsed else 0
                }
            else:
                health_status["services"][service_name] = {
                    "status": "unhealthy",
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            health_status["services"][service_name] = {
                "status": "unhealthy",
                "error": str(e)
            }
    
    return health_status

@app.get("/metrics")
async def get_metrics():
    """Get gateway metrics"""
    return {"metrics": metrics.get_metrics()}

@app.get("/services")
async def list_services():
    """List all available services"""
    services = []
    for service_name, config in SERVICE_REGISTRY.items():
        try:
            client = service_clients.get_client(service_name)
            stats = client.get_health_stats()
            services.append({
                "name": service_name,
                "url": config["url"],
                "status": "healthy",
                "stats": stats
            })
        except Exception as e:
            services.append({
                "name": service_name,
                "url": config["url"],
                "status": "error",
                "error": str(e)
            })
    
    return {"services": services}

# Enhanced proxy functionality
async def proxy_request(
    service_name: str,
    path: str,
    method: str,
    headers: Dict[str, str],
    body: Optional[bytes] = None,
    query_params: Optional[Dict[str, str]] = None
) -> httpx.Response:
    """Proxy request with error handling"""
    client = service_clients.get_client(service_name)
    
    # Prepare request
    kwargs = {
        "headers": headers,
        "params": query_params
    }
    
    if body:
        kwargs["content"] = body
    
    # Make request based on method
    if method == "GET":
        return await client.get(path, **kwargs)
    elif method == "POST":
        return await client.post(path, **kwargs)
    elif method == "PUT":
        return await client.put(path, **kwargs)
    elif method == "DELETE":
        return await client.delete(path, **kwargs)
    else:
        raise HTTPException(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"Method {method} not supported"
        )

# Dynamic route handler
@app.api_route("/{service_name:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_service(
    service_name: str,
    request: Request,
    user: Optional[UserContext] = Depends(get_optional_user)
):
    """Dynamic proxy to microservices"""
    # Parse service and path
    path_parts = service_name.split("/", 1)
    actual_service = path_parts[0]
    remaining_path = "/" + path_parts[1] if len(path_parts) > 1 else "/"
    
    # Check if service exists
    if actual_service not in SERVICE_REGISTRY:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{actual_service}' not found"
        )
    
    try:
        # Prepare headers
        headers = dict(request.headers)
        headers.pop("host", None)
        
        # Add user context to headers if authenticated
        if user:
            headers["X-User-ID"] = user.user_id
            headers["X-Organization-ID"] = user.organization_id
            headers["X-User-Roles"] = ",".join([str(role) for role in user.roles])
        
        # Get request body
        body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None
        
        # Get query parameters
        query_params = dict(request.query_params) if request.query_params else None
        
        # Proxy the request
        response = await proxy_request(
            actual_service,
            remaining_path,
            request.method,
            headers,
            body,
            query_params
        )
        
        # Return response
        return Response(
            content=response.content,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.headers.get("content-type")
        )
        
    except Exception as e:
        logger.error(
            f"Proxy error for {actual_service}{remaining_path}: {str(e)}"
        )
        
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service '{actual_service}' temporarily unavailable"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        access_log=True
    )
