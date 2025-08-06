"""
Minimal FastAPI app for Railway deployment debugging
Simplified version without complex dependencies
"""

from fastapi import FastAPI
import os

app = FastAPI(title="Vocelio AI Gateway", version="2.0.0")

@app.get("/")
async def root():
    return {"message": "Vocelio AI Call Center - API Gateway", "status": "running"}

@app.get("/health")
async def health_check():
    """Simple health check"""
    return {
        "status": "healthy",
        "service": "api-gateway",
        "port": os.getenv("PORT", "8000")
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
