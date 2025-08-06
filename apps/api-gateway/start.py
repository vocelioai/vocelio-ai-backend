#!/usr/bin/env python3
"""
Railway startup script for Vocelio API Gateway
Handles dynamic PORT environment variable
"""
import os
import subprocess
import sys

def main():
    # Debug information
    print("🚀 Starting Vocelio API Gateway...")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Get port from environment
    port = os.environ.get('PORT', '8000')
    print(f"Port: {port}")
    
    # List files in current directory
    print(f"Files in current directory: {os.listdir('.')}")
    
    # Check if src directory exists
    if os.path.exists('src'):
        print(f"Files in src: {os.listdir('src')}")
    else:
        print("❌ src directory not found!")
        return 1
    
    # Start uvicorn
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'src.main:app',
        '--host', '0.0.0.0',
        '--port', port
    ]
    
    print(f"🚀 Starting command: {' '.join(cmd)}")
    
    try:
        # Execute uvicorn
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting application: {e}")
        return 1
    except KeyboardInterrupt:
        print("👋 Shutting down...")
        return 0

if __name__ == "__main__":
    sys.exit(main())
