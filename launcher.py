#!/usr/bin/env python3.11
"""
Ultra-simple Python launcher for Railway deployment
Uses only pre-installed Nix packages
"""

import sys
import os

def main():
    print("🚀 Starting Vocelio AI Backend...")
    
    # Check if FastAPI is available (should be from Nix packages)
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__} found")
    except ImportError:
        print("❌ FastAPI not available")
        sys.exit(1)
    
    # Check if uvicorn is available
    try:
        import uvicorn
        print(f"✅ Uvicorn found")
    except ImportError:
        print("❌ Uvicorn not available")
        sys.exit(1)
    
    # Check if pydantic is available
    try:
        import pydantic
        print(f"✅ Pydantic found")
    except ImportError:
        print("❌ Pydantic not available")
        sys.exit(1)
    
    # Change to app directory and start
    print("📁 Changing to api-gateway directory...")
    if not os.path.exists("apps/api-gateway"):
        print("❌ apps/api-gateway directory not found")
        sys.exit(1)
    
    os.chdir("apps/api-gateway")
    port = os.getenv("PORT", "8000")
    
    print(f"🎯 Starting FastAPI on port {port}...")
    
    # Start uvicorn directly
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(port),
        workers=1
    )

if __name__ == "__main__":
    main()
