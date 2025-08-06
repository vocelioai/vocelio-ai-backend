"""
Minimal FastAPI app for Railway deployment debugging
Ultra-simple version with debug logging
"""

from fastapi import FastAPI
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Log environment info
logger.info(f"PORT environment variable: {os.getenv('PORT', 'NOT SET')}")
logger.info(f"All env vars with PORT: {[k for k in os.environ.keys() if 'PORT' in k.upper()]}")

app = FastAPI(title="Vocelio Debug", version="1.0.0")

@app.get("/")
async def root():
    port = os.getenv("PORT", "8000")
    logger.info(f"Root endpoint called, PORT={port}")
    return {"message": "Debug FastAPI", "port": port, "status": "running"}

@app.get("/health")
async def health_check():
    """Ultra simple health check with logging"""
    port = os.getenv("PORT", "8000")
    logger.info(f"Health check called, PORT={port}")
    return {"status": "healthy", "port": port}

@app.on_event("startup")
async def startup_event():
    port = os.getenv("PORT", "8000")
    logger.info(f"FastAPI app starting up on port {port}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    logger.info(f"Starting uvicorn on 0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
