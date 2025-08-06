#!/usr/bin/env python3
"""
Railway startup script for Vocelio API Gateway
Handles Railway's PORT environment variable properly
"""

import os
import uvicorn

if __name__ == "__main__":
    # Railway provides PORT environment variable
    port = int(os.environ.get("PORT", 8000))
    
    print(f"🚀 Starting Vocelio API Gateway on port {port}")
    print(f"📊 Full API Gateway with 25+ microservices")
    print(f"🔗 Health check: /health")
    print(f"📚 Documentation: /docs")
    
    # Run with uvicorn - Railway compatible
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        access_log=True
    )
