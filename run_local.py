#!/usr/bin/env python3
"""
Local development server for Swindon Waste Collection app
Run this to test the application locally before deploying
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import sys
import os
from urllib.parse import urlparse, parse_qs

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.services.uprn_lookup import UPRNLookupService, UPRNLookupError
from api.services.swindon_scraper import SwindonScraper, SwindonScraperError


class LocalHandler(SimpleHTTPRequestHandler):
    """Local development server handler"""
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        # Handle collections API
        if parsed_path.path.startswith('/api/collections/') or parsed_path.path.startswith('/api/waste-collections/'):
            self.handle_collections(parsed_path.path)
        else:
            # Serve static files
            if self.path == '/':
                self.path = '/index.html'
            return SimpleHTTPRequestHandler.do_GET(self)
    
    def do_POST(self):
        """Handle POST requests"""
        parsed_path = urlparse(self.path)
        
        # Handle UPRN lookup API
        if parsed_path.path == '/api/uprn-lookup':
            self.handle_uprn_lookup()
        else:
            self.send_error(404, "Not Found")
    
    def handle_uprn_lookup(self):
        """Handle UPRN lookup request"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body.decode('utf-8'))
            
            postcode = data.get('postcode')
            if not postcode:
                self.send_json_response(400, {"error": "Missing postcode"})
                return
            
            print(f"\n[LOCAL SERVER] Looking up postcode: {postcode}")
            
            # Perform lookup
            service = UPRNLookupService()
            try:
                addresses = service.lookup(postcode)
                self.send_json_response(200, {
                    "addresses": addresses,
                    "postcode": postcode,
                    "count": len(addresses)
                })
            except UPRNLookupError as e:
                self.send_json_response(200, {
                    "addresses": [],
                    "postcode": postcode,
                    "count": 0,
                    "error": str(e),
                    "error_type": "lookup_error"
                })
            finally:
                service.close()
                
        except Exception as e:
            print(f"[LOCAL SERVER] Error: {str(e)}")
            self.send_json_response(500, {"error": str(e)})
    
    def handle_collections(self, path):
        """Handle collections request"""
        try:
            # Extract UPRN from path
            parts = path.split('/')
            uprn = None
            for part in reversed(parts):
                if part and part.isdigit():
                    uprn = part
                    break
            
            if not uprn:
                self.send_json_response(400, {"error": "Missing UPRN"})
                return
            
            print(f"\n[LOCAL SERVER] Fetching collections for UPRN: {uprn}")
            
            # Fetch collections
            scraper = SwindonScraper()
            try:
                collections = scraper.get_collections(uprn)
                self.send_json_response(200, {
                    "collections": collections,
                    "uprn": uprn
                })
            except SwindonScraperError as e:
                self.send_json_response(400, {"error": str(e)})
            finally:
                scraper.close()
                
        except Exception as e:
            print(f"[LOCAL SERVER] Error: {str(e)}")
            self.send_json_response(500, {"error": str(e)})
    
    def send_json_response(self, status_code, data):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        """Handle OPTIONS for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        """Custom log format"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Start the local development server"""
    port = 8000
    server_address = ('', port)
    
    print("=" * 60)
    print("🚀 Swindon Waste Collection - Local Development Server")
    print("=" * 60)
    print(f"\n✓ Server running at: http://localhost:{port}")
    print(f"✓ API endpoint: http://localhost:{port}/api/uprn-lookup")
    print(f"✓ Collections: http://localhost:{port}/api/collections/{{uprn}}")
    print("\n📝 Test with a Swindon postcode (e.g., SN3 4PG, SN1 1JJ)")
    print("\n⏹  Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    try:
        httpd = HTTPServer(server_address, LocalHandler)
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")
        sys.exit(0)


if __name__ == "__main__":
    main()
