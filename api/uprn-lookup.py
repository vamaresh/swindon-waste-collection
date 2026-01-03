"""
UPRN Lookup endpoint

POST /api/uprn-lookup
Body: { "postcode": "SN1 1XX" }
Response: { "addresses": [{ "uprn": "...", "address": "..." }] }
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os
import traceback

# Add parent directory to path to import services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from api.services.uprn_lookup import UPRNLookupService, UPRNLookupError
except ImportError:
    from services.uprn_lookup import UPRNLookupService, UPRNLookupError


class handler(BaseHTTPRequestHandler):
    """Serverless function handler for UPRN lookup"""
    
    def do_POST(self):
        """Handle POST request"""
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            
            # Parse JSON
            try:
                data = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError as e:
                self.send_error_response(400, f"Invalid JSON: {str(e)}")
                return
            
            # Validate input
            postcode = data.get('postcode')
            if not postcode:
                self.send_error_response(400, "Missing postcode field")
                return
            
            # Perform lookup
            service = UPRNLookupService()
            try:
                addresses = service.lookup(postcode)
                
                # If no addresses found, return empty list with 200 (not error)
                response_data = {
                    "addresses": addresses,
                    "postcode": postcode,
                    "count": len(addresses)
                }
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(response_data).encode())
                
            except UPRNLookupError as e:
                # Return 200 with error details instead of 400
                # This helps with frontend error handling
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {
                    "addresses": [],
                    "postcode": postcode,
                    "count": 0,
                    "error": str(e),
                    "error_type": "lookup_error"
                }
                self.wfile.write(json.dumps(error_response).encode())
            finally:
                service.close()
                
        except Exception as e:
            # Log full traceback for debugging
            error_trace = traceback.format_exc()
            print(f"ERROR: {error_trace}")
            
            self.send_error_response(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_error_response(self, status_code: int, message: str):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            "error": message,
            "addresses": [],
            "count": 0
        }
        self.wfile.write(json.dumps(error_response).encode())
