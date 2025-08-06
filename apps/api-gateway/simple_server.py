#!/usr/bin/env python3
"""
Simple HTTP server for Railway testing
"""
import http.server
import socketserver
import os
import json
import sys

def main():
    # Get port from Railway environment
    PORT = int(os.environ.get('PORT', 8000))
    HOST = '0.0.0.0'
    
    print(f'🚀 Starting Vocelio test server...')
    print(f'📍 Host: {HOST}')
    print(f'🔌 Port: {PORT}')
    print(f'🌐 URL: http://{HOST}:{PORT}')
    print(f'🐍 Python: {sys.version}')
    print(f'📁 Working directory: {os.getcwd()}')
    print(f'📝 Environment PORT: {os.environ.get("PORT", "not set")}')

    class VocelioHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            print(f'📨 Request: {self.path}')
            
            if self.path == '/':
                response = {
                    "message": "🎉 Vocelio Railway Test - SUCCESS!", 
                    "status": "working",
                    "port": PORT,
                    "host": HOST,
                    "service": "simple-test"
                }
                self.send_json_response(200, response)
                
            elif self.path == '/health':
                response = {
                    "status": "healthy", 
                    "service": "vocelio-simple-test",
                    "port": PORT,
                    "timestamp": str(os.times())
                }
                self.send_json_response(200, response)
                
            elif self.path == '/info':
                response = {
                    "python_version": sys.version,
                    "working_directory": os.getcwd(),
                    "environment_port": os.environ.get("PORT", "not set"),
                    "current_port": PORT,
                    "host": HOST
                }
                self.send_json_response(200, response)
                
            else:
                response = {"error": "Not found", "path": self.path}
                self.send_json_response(404, response)
                
        def send_json_response(self, code, data):
            self.send_response(code)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(data, indent=2).encode())

    try:
        # Create server
        with socketserver.TCPServer((HOST, PORT), VocelioHTTPRequestHandler) as httpd:
            print(f'✅ Server successfully started!')
            print(f'🌍 Listening on http://{HOST}:{PORT}')
            print(f'🔗 Try: http://{HOST}:{PORT}/health')
            print('🚀 Server ready to handle requests...')
            httpd.serve_forever()
            
    except OSError as e:
        print(f'❌ Failed to start server: {e}')
        print(f'💡 Port {PORT} might be in use or unavailable')
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down server...")
    except Exception as e:
        print(f'❌ Unexpected error: {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()
