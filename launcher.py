#!/usr/bin/env python3.11
"""
Simple Python launcher for Railway deployment
Ensures FastAPI is available and starts the app
"""

import sys
import os
import subprocess

def run_command(cmd):
    """Run a command and return success status"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    print("🚀 Starting Vocelio AI Backend...")
    
    # Check if FastAPI is already available
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ All dependencies already available")
    except ImportError as e:
        print(f"⚠️ Missing dependencies: {e}")
        print("📦 Installing missing packages...")
        
        # Try to install missing packages
        if not run_command("python3.11 -m pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0 pydantic==2.5.0"):
            print("❌ Failed to install packages with pip")
            sys.exit(1)
        
        # Verify again
        try:
            import fastapi
            import uvicorn
            import pydantic
            print("✅ Dependencies installed successfully")
        except ImportError as e:
            print(f"❌ Still missing dependencies after install: {e}")
            sys.exit(1)
    
    # Change to app directory and start
    print("📁 Changing to api-gateway directory...")
    if not os.path.exists("apps/api-gateway"):
        print("❌ apps/api-gateway directory not found")
        sys.exit(1)
    
    os.chdir("apps/api-gateway")
    port = os.getenv("PORT", "8000")
    
    print(f"🎯 Starting FastAPI on port {port}...")
    
    # Start uvicorn
    run_command(f"python3.11 -m uvicorn src.main:app --host 0.0.0.0 --port {port}")

if __name__ == "__main__":
    main()
