#!/usr/bin/env python3
"""
Simple Railway-compatible Overview Service
Minimal implementation that works reliably on Railway
"""

import os
import json
from datetime import datetime

# Simple HTTP server using built-in modules
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

class OverviewHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            health_data = {
                "service": "Vocelio Overview Service",
                "version": "1.0.0",
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "description": "Dashboard Metrics and System Overview",
                "port": os.environ.get("PORT", "8001"),
                "environment": os.environ.get("ENVIRONMENT", "production")
            }
            
            self.wfile.write(json.dumps(health_data, indent=2).encode())
        else:
            # Default response
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            welcome_data = {
                "message": "Vocelio.ai Overview Service",
                "status": "operational",
                "endpoints": ["/health"],
                "timestamp": datetime.now().isoformat()
            }
            
            self.wfile.write(json.dumps(welcome_data, indent=2).encode())

    def log_message(self, format, *args):
        # Simple logging
        print(f"[{datetime.now().isoformat()}] {format % args}")

def main():
    port = int(os.environ.get("PORT", 8001))
    host = "0.0.0.0"
    
    print(f"🚀 Starting Vocelio Overview Service")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🌐 Railway Environment: {os.environ.get('RAILWAY_ENVIRONMENT', 'local')}")
    
    server = HTTPServer((host, port), OverviewHandler)
    
    print(f"✅ Overview Service running on http://{host}:{port}")
    print(f"🔍 Health check: http://{host}:{port}/health")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Overview Service")
        server.shutdown()

if __name__ == "__main__":
    main()
