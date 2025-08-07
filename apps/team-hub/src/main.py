# apps/team-hub/src/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Team Hub Service starting up...")
    logger.info("✅ Team Hub Service initialized")
    
    yield
    
    logger.info("🔄 Team Hub Service shutting down...")
    logger.info("✅ Team Hub Service shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Vocelio.ai Team Hub Service",
    description="👥 Enterprise Team Management & Performance Center",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health endpoints
@app.get("/")
async def root():
    return {
        "service": "team-hub", 
        "status": "healthy", 
        "version": "1.0.0",
        "description": "👥 Enterprise Team Management & Performance Center"
    }

@app.get("/health")
async def health_check():
    return {
        "service": "team-hub",
        "status": "healthy",
        "version": "1.0.0",
        "description": "👥 Enterprise Team Management & Performance Center"
    }

@app.get("/metrics")
async def get_service_metrics():
    """Get service metrics for monitoring"""
    return {
        "service": "team-hub",
        "status": "healthy",
        "active_connections": 0,
        "total_requests": 0,
        "avg_response_time": 0.0
    }

# Team management endpoints
@app.get("/api/v1/teams")
async def get_teams():
    """Get all teams"""
    return {
        "teams": [
            {"id": 1, "name": "Sales Team", "members": 5, "performance": "excellent"},
            {"id": 2, "name": "Support Team", "members": 3, "performance": "good"},
            {"id": 3, "name": "Management", "members": 2, "performance": "excellent"}
        ],
        "total": 3
    }

@app.get("/api/v1/performance")
async def get_performance():
    """Get team performance metrics"""
    return {
        "overall_performance": "excellent",
        "metrics": {
            "calls_handled": 1250,
            "avg_response_time": "2.3s",
            "customer_satisfaction": "94%",
            "team_efficiency": "87%"
        }
    }

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8018))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
        log_level="info"
    )
