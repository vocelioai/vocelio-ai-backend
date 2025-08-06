#!/usr/bin/env python3
"""
Ultra-simple HTTP server test - no FastAPI dependencies
"""
import http.server
import socketserver
import json
from urllib.parse import urlparse

class HealthHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"status": "ok", "message": "Simple HTTP server"}
            self.wfile.write(json.dumps(response).encode())
        elif parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            response = {"message": "Vocelio AI - Simple Server", "status": "running"}
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        print(f"[HTTP] {format % args}")

if __name__ == "__main__":
    PORT = 8000
    print(f"Starting simple HTTP server on port {PORT}")
    
    with socketserver.TCPServer(("0.0.0.0", PORT), HealthHandler) as httpd:
        print(f"Server running at http://0.0.0.0:{PORT}")
        print("Health check available at /health")
        httpd.serve_forever()
