#!/usr/bin/env python3
"""
Railway Launcher for Vocelio AI Backend
Handles the hyphenated folder names in import paths
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Change to the api-gateway directory and import the app
api_gateway_path = project_root / "apps" / "api-gateway"
sys.path.insert(0, str(api_gateway_path))

try:
    # Import the FastAPI app from the api-gateway service
    from src.main import app
    
    if __name__ == "__main__":
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        uvicorn.run(
            "main:app",
            host="0.0.0.0", 
            port=port,
            workers=1,
            reload=False
        )
        
except ImportError as e:
    print(f"Error importing FastAPI app: {e}")
    sys.exit(1)
