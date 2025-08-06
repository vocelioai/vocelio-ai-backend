#!/usr/bin/env python3
"""
Railway-optimized FastAPI health check server
Minimal FastAPI app specifically designed for Railway health checks
"""

from fastapi import FastAPI
import uvicorn
import os

# Create FastAPI app
app = FastAPI(
    title="Vocelio API Gateway",
    description="AI Call Center Platform - Health Check Service",
    version="1.0.0"
)

@app.get("/")
def root():
    """Root endpoint - Railway health check"""
    return {
        "message": "Vocelio API Gateway is running 🚀",
        "status": "healthy",
        "service": "api-gateway",
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    """Health check endpoint - Railway health check"""
    return {
        "status": "ok",
        "service": "healthy",
        "message": "All systems operational"
    }

@app.get("/ping")
def ping():
    """Simple ping endpoint"""
    return {"ping": "pong"}

if __name__ == "__main__":
    # Railway provides PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Starting Vocelio API Gateway on port {port}")
    print(f"📊 Health check available at /health")
    print(f"🔗 Root endpoint available at /")
    
    # Run with uvicorn - Railway compatible
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
