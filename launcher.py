#!/usr/bin/env python3.11
"""
Simple Python launcher for Railway deployment
Direct FastAPI startup without shell dependencies
"""

import sys
import os

def main():
    print("🚀 Starting Vocelio AI Backend...")
    
    # Verify FastAPI is available
    try:
        import fastapi
        import uvicorn
        import pydantic
        print(f"✅ FastAPI {fastapi.__version__} available")
        print(f"✅ Uvicorn available")
        print(f"✅ Pydantic {pydantic.__version__} available")
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        sys.exit(1)
    
    # Change to app directory
    print("📁 Changing to api-gateway directory...")
    api_gateway_path = os.path.join(os.getcwd(), "apps", "api-gateway")
    
    if not os.path.exists(api_gateway_path):
        print(f"❌ Directory not found: {api_gateway_path}")
        print("Available directories:")
        for item in os.listdir(os.getcwd()):
            if os.path.isdir(item):
                print(f"  - {item}")
        sys.exit(1)
    
    os.chdir(api_gateway_path)
    print(f"✅ Changed to {os.getcwd()}")
    
    # Get port from environment
    port = int(os.getenv("PORT", "8000"))
    print(f"🎯 Starting FastAPI on port {port}...")
    
    # Start uvicorn directly (no subprocess)
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

if __name__ == "__main__":
    main()
