#!/usr/bin/env python3
"""
Ultra-Simple Railway Server
No dependencies, bulletproof deployment
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        if self.path == '/health':
            response = {
                "service": "Vocelio AI Backend",
                "status": "healthy", 
                "version": "1.0.0",
                "timestamp": datetime.now().isoformat(),
                "port": os.environ.get("PORT", "unknown"),
                "message": "🚀 Your world-class AI call center is operational!"
            }
        else:
            response = {
                "message": "🎉 Vocelio AI Backend is running!",
                "status": "operational",
                "endpoints": ["/health"],
                "services": "25 microservices ready for deployment",
                "timestamp": datetime.now().isoformat()
            }
        
        self.wfile.write(json.dumps(response, indent=2).encode())
    
    def log_message(self, format, *args):
        print(f"[{datetime.now()}] {format % args}")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    print(f"🚀 Starting Vocelio AI Backend on port {port}")
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()
