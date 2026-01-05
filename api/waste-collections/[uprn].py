"""
Collections endpoint

GET /api/waste-collections/[uprn]
Response: { "collections": [...], "uprn": "..." }
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
import os

# Add parent directories to path to import services
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, parent_dir)
sys.path.insert(0, grandparent_dir)

try:
    from api.services.swindon_scraper import SwindonScraper, SwindonScraperError
except ImportError:
    try:
        from services.swindon_scraper import SwindonScraper, SwindonScraperError
    except ImportError:
        # When running in Vercel
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "swindon_scraper",
            os.path.join(parent_dir, "services", "swindon_scraper.py")
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        SwindonScraper = module.SwindonScraper
        SwindonScraperError = module.SwindonScraperError


class handler(BaseHTTPRequestHandler):
    """Serverless function handler for collections"""
    
    def do_GET(self):
        """Handle GET request"""
        try:
            # Extract UPRN from path
            # Path will be like /api/collections or /api/collections/123456
            path = self.path
            parts = path.split('/')
            
            # Find UPRN in path
            uprn = None
            for part in reversed(parts):
                if part and part.isdigit():
                    uprn = part
                    break
            
            if not uprn:
                self.send_error_response(400, "Missing UPRN in path")
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
