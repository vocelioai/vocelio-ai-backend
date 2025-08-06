#!/usr/bin/env python3
"""
Simple HTTP server for Railway testing
"""
import http.server
import socketserver
import os
import json
import sys
import traceback

def main():
    try:
        # Get port from Railway environment
        PORT = int(os.environ.get('PORT', 8000))
        HOST = '0.0.0.0'  # Must bind to all interfaces for Railway
        
        print(f'🚀 Starting Vocelio test server...', flush=True)
        print(f'📍 Host: {HOST}', flush=True)
        print(f'🔌 Port: {PORT}', flush=True)
        print(f'🌐 URL: http://{HOST}:{PORT}', flush=True)
        print(f'🐍 Python: {sys.version}', flush=True)
        print(f'📁 Working directory: {os.getcwd()}', flush=True)
        print(f'📝 Environment PORT: {os.environ.get("PORT", "not set")}', flush=True)

        class VocelioHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                print(f'📨 Request: {self.path}', flush=True)
                
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
                        "timestamp": "ok"
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
            
            def log_message(self, format, *args):
                # Override to ensure logs are flushed
                print(f"[{self.address_string()}] {format % args}", flush=True)

        # Create server with SO_REUSEADDR to avoid "Address already in use" errors
        print(f'🔧 Creating server...', flush=True)
        
        # Use threading server for better Railway compatibility
        from socketserver import ThreadingTCPServer
        
        class ThreadedHTTPServer(ThreadingTCPServer):
            allow_reuse_address = True
            daemon_threads = True
        
        with ThreadedHTTPServer((HOST, PORT), VocelioHTTPRequestHandler) as httpd:
            print(f'✅ Server successfully started!', flush=True)
            print(f'🌍 Listening on http://{HOST}:{PORT}', flush=True)
            print(f'🔗 Try: http://{HOST}:{PORT}/health', flush=True)
            print('🚀 Server ready to handle requests...', flush=True)
            
            # Force flush all output
            sys.stdout.flush()
            sys.stderr.flush()
            
            httpd.serve_forever()
            
    except Exception as e:
        print(f'❌ Fatal error: {e}', flush=True)
        print(f'� Traceback: {traceback.format_exc()}', flush=True)
        sys.stdout.flush()
        sys.stderr.flush()
        # Exit with error code
        sys.exit(1)

if __name__ == "__main__":
    main()
