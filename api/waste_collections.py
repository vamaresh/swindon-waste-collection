"""
Collections endpoint

GET /api/collections/[uprn]
Response: { "collections": [...], "uprn": "..." }
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import urlparse, parse_qs

# Add parent directory to path to import services
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from api.services.swindon_scraper import SwindonScraper, SwindonScraperError
except ImportError:
    from services.swindon_scraper import SwindonScraper, SwindonScraperError


class handler(BaseHTTPRequestHandler):
    """Serverless function handler for collections"""
    
    def do_GET(self):
        """Handle GET request"""
        print(f"[COLLECTIONS] GET request received: {self.path}")
        try:
            # Extract UPRN from path
            # Path will be like /api/collections or /api/collections/123456
            path = self.path
            parts = path.split('/')
            print(f"[COLLECTIONS] Path parts: {parts}")
            
            # Find UPRN in path
            uprn = None
            for part in reversed(parts):
                if part and part.isdigit():
                    uprn = part
                    break
            
            print(f"[COLLECTIONS] Extracted UPRN: {uprn}")
            if not uprn:
                print("[COLLECTIONS] No UPRN found in path")
                self.send_error_response(400, "Missing UPRN in path")
                return
            
            # Fetch collections
            scraper = SwindonScraper()
            try:
                print(f"[COLLECTIONS] Fetching collections for UPRN: {uprn}")
                collections = scraper.get_collections(uprn)
                print(f"[COLLECTIONS] Found {len(collections)} collections")
                
                response_data = {
                    "collections": collections,
                    "uprn": uprn
                }
                
                print(f"[COLLECTIONS] Sending success response")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                self.wfile.write(json.dumps(response_data).encode())
                
            except SwindonScraperError as e:
                self.send_error_response(400, str(e))
            finally:
                scraper.close()
                
        except Exception as e:
            self.send_error_response(500, f"Internal server error: {str(e)}")
    
    def do_OPTIONS(self):
        """Handle OPTIONS request for CORS"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def send_error_response(self, status_code: int, message: str):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        error_response = {
            "error": message
        }
        self.wfile.write(json.dumps(error_response).encode())
