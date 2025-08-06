"""
Minimal FastAPI app for Railway testing
"""
from fastapi import FastAPI

app = FastAPI(title="Vocelio Test", version="1.0.0")

@app.get("/")
async def root():
    return {"message": "Vocelio API Gateway - Basic Test", "status": "working"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "vocelio-test"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
