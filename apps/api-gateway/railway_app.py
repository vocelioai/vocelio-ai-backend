#!/usr/bin/env python3
"""
Ultra-simple Railway FastAPI app
Minimal dependencies, guaranteed to work
"""

import os
import logging
from fastapi import FastAPI
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Vocelio API Gateway",
    description="AI Call Center Platform - Railway Production",
    version="1.0.0"
)

@app.get("/")
async def root():
    """Root endpoint - Railway health check"""
    port = os.environ.get("PORT", "unknown")
    environment = os.environ.get("RAILWAY_ENVIRONMENT", "unknown")
    
    logger.info(f"Root endpoint called! Port: {port}, Env: {environment}")
    
    return {
        "message": "🚀 Vocelio API Gateway - LIVE on Railway!",
        "status": "running",
        "service": "api-gateway",
        "version": "1.0.0",
        "port": port,
        "environment": environment,
        "railway": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check called!")
    return {
        "status": "healthy",
        "service": "vocelio-api-gateway",
        "railway": "production"
    }

@app.get("/ping")
async def ping():
    """Simple ping endpoint"""
    return {"ping": "pong", "timestamp": "live"}

@app.get("/test")
async def test():
    """Test endpoint to verify routing"""
    return {
        "test": "success",
        "message": "Railway routing is working!",
        "endpoints": ["/", "/health", "/ping", "/test"]
    }

if __name__ == "__main__":
    # Get port from Railway environment variable
    port = int(os.environ.get("PORT", 8000))
    host = "0.0.0.0"
    
    logger.info(f"🚀 Starting Vocelio API Gateway on Railway")
    logger.info(f"📍 Host: {host}")
    logger.info(f"🔌 Port: {port}")
    logger.info(f"🌍 Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'unknown')}")
    
    # Start with uvicorn - Railway optimized
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info",
        access_log=True,
        # Use asyncio loop - more compatible
        loop="asyncio"
    )
