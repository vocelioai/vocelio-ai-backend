#!/usr/bin/env python3
"""
Railway-optimized startup script
Fixes port binding issue for Railway deployment
"""

import os
import sys
import uvicorn
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    # Railway provides PORT environment variable - this is crucial!
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting Vocelio API Gateway")
    logger.info(f"📍 Host: {host}")
    logger.info(f"🔌 Port: {port}")
    logger.info(f"📁 Working directory: {os.getcwd()}")
    logger.info(f"🐍 Python path: {sys.executable}")
    logger.info(f"📊 Environment variables:")
    logger.info(f"   - PORT: {os.environ.get('PORT', 'Not set')}")
    logger.info(f"   - HOST: {os.environ.get('HOST', 'Not set')}")
    logger.info(f"   - RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'Not set')}")
    
    # Add current directory to Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    
    try:
        # Try to import the main module
        logger.info("📦 Attempting to import main module...")
        
        # First try the simple approach
        if os.path.exists("src/minimal_test.py"):
            logger.info("🔧 Using src.minimal_test for Railway")
            from src import minimal_test
            app = minimal_test.app
        elif os.path.exists("src/main.py"):
            logger.info("🔧 Using src.main for Railway")
            from src import main
            app = main.app
        elif os.path.exists("minimal_test.py"):
            logger.info("🔧 Using minimal_test.py for Railway")
            import minimal_test
            app = minimal_test.app
        elif os.path.exists("main.py"):
            logger.info("🔧 Using main.py for Railway")
            import main
            app = main.app
        else:
            logger.error("❌ No suitable main module found!")
            sys.exit(1)
        
        logger.info("✅ Successfully imported application")
        
        # Start the server with Railway-specific configuration
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="info",
            access_log=True,
            # Railway-specific optimizations
            workers=1,  # Railway works best with single worker
            loop="asyncio",
            http="httptools",
        )
        
    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.info("🔧 Falling back to simple HTTP server...")
        
        # Fallback to simple HTTP server
        import http.server
        import socketserver
        import json
        from urllib.parse import urlparse
        
        class HealthHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                parsed_path = urlparse(self.path)
                
                response_data = {
                    "message": "Vocelio API Gateway",
                    "status": "running",
                    "service": "api-gateway",
                    "version": "1.0.0",
                    "port": port,
                    "path": parsed_path.path
                }
                
                if parsed_path.path in ['/', '/health', '/ping']:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode())
                else:
                    self.send_response(404)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    error_response = {"error": "Not found", "path": parsed_path.path}
                    self.wfile.write(json.dumps(error_response).encode())
            
            def log_message(self, format, *args):
                logger.info(f"[HTTP] {format % args}")
        
        logger.info(f"🌐 Starting fallback HTTP server on {host}:{port}")
        with socketserver.TCPServer((host, port), HealthHandler) as httpd:
            logger.info(f"✅ Fallback server running at http://{host}:{port}")
            httpd.serve_forever()
    
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        logger.error("📋 Exception details:", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
