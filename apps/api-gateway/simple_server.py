#!/usr/bin/env python3
"""
Simple HTTP server for Railway testing
"""
import http.server
import socketserver
import os
import json

def main():
    PORT = int(os.environ.get('PORT', 8000))
    print(f'Starting simple HTTP server on port {PORT}')

    class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                response = {"message": "Vocelio Railway Test", "status": "working"}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            elif self.path == '/health':
                response = {"status": "healthy", "service": "vocelio-simple-test"}
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode())
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"error": "Not found"}')

    with socketserver.TCPServer(('', PORT), MyHTTPRequestHandler) as httpd:
        print(f'Server running on http://0.0.0.0:{PORT}')
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")

if __name__ == "__main__":
    main()
