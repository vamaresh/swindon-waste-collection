"""
Collections endpoint for Vercel serverless function

GET /api/waste-collections?uprn=[uprn]
Response: { "collections": [...], "uprn": "..." }
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import urlparse, parse_qs

# Setup paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import scraper
from services.swindon_scraper import SwindonScraper, SwindonScraperError


class handler(BaseHTTPRequestHandler):
    """Serverless function handler for collections"""
    
    def do_GET(self):
        """Handle GET request"""
        try:
            # Parse URL to get query parameters or path
            parsed_url = urlparse(self.path)
            query_params = parse_qs(parsed_url.query)
            
            # Try to get UPRN from query parameter first
            uprn = query_params.get('uprn', [None])[0]
            
            # If not in query, try to extract from path
            if not uprn:
                parts = parsed_url.path.split('/')
                for part in reversed(parts):
                    if part and part.isdigit():
                        uprn = part
                        break
            
            if not uprn:
                self.send_error_response(400, "Missing UPRN in path or query")
                return
            
            # Fetch collections
            scraper = SwindonScraper()
            try:
                collections = scraper.get_collections(uprn)
                
                response_data = {
                    "collections": collections,
                    "uprn": uprn
                }
                
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
