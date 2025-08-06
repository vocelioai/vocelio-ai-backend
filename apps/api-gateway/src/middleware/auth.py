# apps/api-gateway/src/middleware/auth.py
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import jwt
import httpx
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

async def auth_middleware(request: Request, call_next):
    """Authentication middleware for gateway"""
    
    # Skip auth for health checks and docs
    skip_auth_paths = [
        "/health",
        "/docs",
        "/redoc", 
        "/openapi.json",
        "/",
        "/webhooks"  # Webhooks have their own auth
    ]
    
    if any(request.url.path.startswith(path) for path in skip_auth_paths):
        return await call_next(request)
    
    # Get authorization header
    authorization = request.headers.get("Authorization")
    
    if not authorization:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": "Missing authorization header",
                "message": "Please provide a valid API key or JWT token"
            }
        )
    
    try:
        # Extract token
        if authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
        else:
            token = authorization
        
        # Validate token (you can customize this based on your auth system)
        if token.startswith("voc_"):  # API Key format
            # Validate API key with developer-api service
            is_valid = await validate_api_key(token)
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid API key")
        else:
            # Validate JWT token
            payload = jwt.decode(token, os.getenv("SECRET_KEY", "secret"), algorithms=["HS256"])
            request.state.user_id = payload.get("user_id")
            request.state.org_id = payload.get("org_id")
    
    except jwt.ExpiredSignatureError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Token expired", "message": "Please refresh your token"}
        )
    except jwt.InvalidTokenError:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Invalid token", "message": "Please provide a valid token"}
        )
    except Exception as e:
        logger.error(f"Auth middleware error: {e}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Authentication failed", "message": "Unable to validate credentials"}
        )
    
    return await call_next(request)

async def validate_api_key(api_key: str) -> bool:
    """Validate API key with developer-api service"""
    try:
        developer_api_url = os.getenv("DEVELOPER_API_SERVICE_URL", "http://localhost:8017")
        
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{developer_api_url}/api/v1/validate-key",
                json={"api_key": api_key}
            )
            return response.status_code == 200
    except:
        # If developer-api service is down, allow request (graceful degradation)
        logger.warning("Could not validate API key - developer-api service unavailable")
        return True

# apps/api-gateway/src/middleware/rate_limiting.py
import time
import json from collections import defaultdict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import redis.asyncio as redis
import logging
import os

logger = logging.getLogger(__name__)

class RateLimiter:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL")
        self.redis_client = None
        self.memory_store = defaultdict(list)  # Fallback to memory if no Redis
        
    async def initialize(self):
        """Initialize Redis connection"""
        if self.redis_url:
            try:
                self.redis_client = redis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info("✅ Redis connected for rate limiting")
            except Exception as e:
                logger.warning(f"⚠️ Redis connection failed, using memory store: {e}")
                self.redis_client = None
    
    async def is_allowed(self, key: str, limit: int, window: int) -> tuple[bool, dict]:
        """Check if request is allowed within rate limits"""
        current_time = time.time()
        
        if self.redis_client:
            return await self._redis_rate_limit(key, limit, window, current_time)
        else:
            return await self._memory_rate_limit(key, limit, window, current_time)
    
    async def _redis_rate_limit(self, key: str, limit: int, window: int, current_time: float) -> tuple[bool, dict]:
        """Redis-based rate limiting with sliding window"""
        try:
            pipe = self.redis_client.pipeline()
            
            # Remove old entries
            pipe.zremrangebyscore(key, 0, current_time - window)
            
            # Count current requests
            pipe.zcard(key)
            
            # Add current request
            pipe.zadd(key, {str(current_time): current_time})
            
            # Set expiry
            pipe.expire(key, window)
            
            results = await pipe.execute()
            current_count = results[1]
            
            allowed = current_count < limit
            
            return allowed, {
                "limit": limit,
                "remaining": max(0, limit - current_count - 1),
                "reset_time": int(current_time + window),
                "retry_after": window if not allowed else None
            }
            
        except Exception as e:
            logger.error(f"Redis rate limiting error: {e}")
            # Fallback to allowing request
            return True, {"limit": limit, "remaining": limit - 1, "reset_time": int(current_time + window)}
    
    async def _memory_rate_limit(self, key: str, limit: int, window: int, current_time: float) -> tuple[bool, dict]:
        """Memory-based rate limiting (fallback)"""
        # Clean old entries
        self.memory_store[key] = [
            timestamp for timestamp in self.memory_store[key]
            if current_time - timestamp < window
        ]
        
        current_count = len(self.memory_store[key])
        allowed = current_count < limit
        
        if allowed:
            self.memory_store[key].append(current_time)
        
        return allowed, {
            "limit": limit,
            "remaining": max(0, limit - current_count - (1 if allowed else 0)),
            "reset_time": int(current_time + window),
            "retry_after": window if not allowed else None
        }

# Global rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting middleware"""
    
    # Skip rate limiting for health checks
    skip_paths = ["/health", "/docs", "/redoc", "/openapi.json"]
    if any(request.url.path.startswith(path) for path in skip_paths):
        return await call_next(request)
    
    # Initialize rate limiter if not done
    if rate_limiter.redis_client is None and rate_limiter.redis_url:
        await rate_limiter.initialize()
    
    # Determine rate limit key (IP + user if available)
    client_ip = request.client.host
    user_id = getattr(request.state, "user_id", None)
    
    if user_id:
        rate_key = f"rate_limit:user:{user_id}"
        limit = 5000  # Higher limit for authenticated users
    else:
        rate_key = f"rate_limit:ip:{client_ip}"
        limit = 1000  # Lower limit for anonymous users
    
    window = 3600  # 1 hour window
    
    try:
        allowed, info = await rate_limiter.is_allowed(rate_key, limit, window)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for {rate_key}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Limit: {limit} per hour",
                    "retry_after": info.get("retry_after"),
                    "reset_time": info.get("reset_time")
                },
                headers={
                    "X-RateLimit-Limit": str(info["limit"]),
                    "X-RateLimit-Remaining": str(info["remaining"]),
                    "X-RateLimit-Reset": str(info["reset_time"]),
                    "Retry-After": str(info.get("retry_after", window))
                }
            )
        
        # Add rate limit headers to response
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(info["limit"])
        response.headers["X-RateLimit-Remaining"] = str(info["remaining"])
        response.headers["X-RateLimit-Reset"] = str(info["reset_time"])
        
        return response
        
    except Exception as e:
        logger.error(f"Rate limiting error: {e}")
        # Allow request if rate limiting fails
        return await call_next(request)

# apps/api-gateway/src/middleware/logging.py
import time
import uuid
import json
import logging
from fastapi import Request
from datetime import datetime

logger = logging.getLogger(__name__)

async def request_logging_middleware(request: Request, call_next):
    """Request logging middleware with detailed metrics"""
    
    # Generate unique request ID
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    
    # Start timing
    start_time = time.time()
    
    # Log incoming request
    logger.info(
        f"🌐 Incoming Request",
        extra={
            "request_id": request_id,
            "method": request.method,
            "url": str(request.url),
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent", ""),
            "content_length": request.headers.get("content-length", 0),
            "referer": request.headers.get("referer", ""),
            "timestamp": datetime.utcnow().isoformat()
        }
    )
    
    try:
        # Process request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response
        logger.info(
            f"✅ Request Completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "status_code": response.status_code,
                "process_time": round(process_time, 3),
                "response_size": response.headers.get("content-length", 0),
                "user_id": getattr(request.state, "user_id", None),
                "org_id": getattr(request.state, "org_id", None),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response
        
    except Exception as e:
        # Calculate processing time for errors too
        process_time = time.time() - start_time
        
        # Log error
        logger.error(
            f"❌ Request Failed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "error": str(e),
                "process_time": round(process_time, 3),
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        # Re-raise the exception
        raise

# apps/api-gateway/src/middleware/__init__.py
"""
API Gateway Middleware Collection

This module contains all middleware for the Vocelio.ai API Gateway:
- Authentication and authorization
- Rate limiting and throttling  
- Request/response logging
- Error handling and metrics
"""

from .auth import auth_middleware
from .rate_limiting import rate_limit_middleware, rate_limiter
from .logging import request_logging_middleware

__all__ = [
    "auth_middleware",
    "rate_limit_middleware", 
    "rate_limiter",
    "request_logging_middleware"
]