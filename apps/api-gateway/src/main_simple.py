"""
Minimal FastAPI app for Railway deployment
Fixed port 8000 approach
"""

from fastapi import FastAPI
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Vocelio Debug", version="1.0.0")

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Debug FastAPI", "port": "8000", "status": "running"}

@app.get("/health")
async def health_check():
    """Simple health check"""
    logger.info("Health check called")
    return {"status": "ok"}

@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI app starting up on port 8000")

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting uvicorn on 0.0.0.0:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
