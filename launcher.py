#!/usr/bin/env python3.11
"""
Simple Python launcher for Railway deployment
Installs minimal dependencies and starts the FastAPI app
"""

import subprocess
import sys
import os

def run_command(cmd):
    """Run a command and print output"""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr)
    return result.returncode == 0

def main():
    print("🚀 Starting Vocelio AI Backend...")
    
    # Install minimal dependencies
    print("📦 Installing FastAPI dependencies...")
    packages = [
        "fastapi==0.104.1",
        "uvicorn==0.24.0", 
        "pydantic==2.5.0"
    ]
    
    for package in packages:
        if not run_command(f"python3.11 -m pip install {package}"):
            print(f"Failed to install {package}")
            sys.exit(1)
    
    # Verify imports work
    try:
        import fastapi
        import uvicorn
        import pydantic
        print("✅ All dependencies imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        sys.exit(1)
    
    # Change to app directory and start
    os.chdir("apps/api-gateway")
    port = os.getenv("PORT", "8000")
    
    print(f"🎯 Starting FastAPI on port {port}...")
    run_command(f"python3.11 -m uvicorn src.main:app --host 0.0.0.0 --port {port}")

if __name__ == "__main__":
    main()
