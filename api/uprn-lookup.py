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
        print("[UPRN LOOKUP] POST request received")
        try:
            # Read request body
            content_length = int(self.headers.get('Content-Length', 0))
            print(f"[UPRN LOOKUP] Content-Length: {content_length}")
            body = self.rfile.read(content_length)
            
            # Parse JSON
            try:
                data = json.loads(body.decode('utf-8'))
                print(f"[UPRN LOOKUP] Parsed request data: {data}")
            except json.JSONDecodeError as e:
                print(f"[UPRN LOOKUP] JSON decode error: {str(e)}")
                self.send_error_response(400, f"Invalid JSON: {str(e)}")
                return
            
            # Validate input
            postcode = data.get('postcode')
            if not postcode:
                print("[UPRN LOOKUP] Missing postcode in request")
                self.send_error_response(400, "Missing postcode field")
                return
            
            print(f"[UPRN LOOKUP] Looking up postcode: {postcode}")
            
            # Perform lookup
            service = UPRNLookupService()
            try:
                print(f"[UPRN LOOKUP] Starting lookup service...")
                addresses = service.lookup(postcode)
                print(f"[UPRN LOOKUP] Found {len(addresses)} addresses")
                
                # If no addresses found, return empty list with 200 (not error)
                response_data = {
                    "addresses": addresses,
                    "postcode": postcode,
                    "count": len(addresses)
                }
                
                print(f"[UPRN LOOKUP] Sending success response with {len(addresses)} addresses")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(response_data).encode())
                
            except UPRNLookupError as e:
                # Return 200 with error details instead of 400
                # This helps with frontend error handling
                print(f"[UPRN LOOKUP] Lookup error: {str(e)}")
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
            except Exception as e:
                print(f"[UPRN LOOKUP] Unexpected service error: {str(e)}")
                import traceback
                traceback.print_exc()
                self.send_error_response(500, f"Service error: {str(e)}")
            finally:
                service.close()
                
        except Exception as e:
            # Log full traceback for debugging
            print(f"[UPRN LOOKUP] Handler exception: {str(e)}")
            import traceback
            error_trace = traceback.format_exc()
            print(f"[UPRN LOOKUP] ERROR TRACE: {error_trace}")
            
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
