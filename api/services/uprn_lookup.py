"""
UPRN Lookup Service for Swindon Borough Council

This module provides postcode to UPRN (Unique Property Reference Number) lookup
using the iShare Maps API.
"""

import requests
from typing import List, Dict
import logging
import re
import json

logger = logging.getLogger(__name__)


class UPRNLookupError(Exception):
    """Custom exception for UPRN lookup errors"""
    pass


class UPRNLookupService:
    """Service for looking up UPRN from postcode using iShare Maps API"""
    
    BASE_URL = "https://www.swindon.gov.uk"
    COLLECTION_PAGE = f"{BASE_URL}/info/20122/rubbish_and_recycling_collection_days"
    ISHARE_SEARCH_URL = "https://maps.swindon.gov.uk/getdata.aspx"
    
    def __init__(self):
        """Initialize the lookup service"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Referer': self.COLLECTION_PAGE
        })
    
    def _normalize_postcode(self, postcode: str) -> str:
        """Normalize UK postcode format"""
        postcode = postcode.replace(" ", "").upper()
        if len(postcode) >= 5:
            postcode = f"{postcode[:-3]} {postcode[-3:]}"
        return postcode
    
    def validate_postcode(self, postcode: str) -> bool:
        """Validate UK postcode format"""
        pattern = r'^[A-Z]{1,2}[0-9]{1,2}[A-Z]?\s?[0-9][A-Z]{2}$'
        normalized = self._normalize_postcode(postcode)
        return bool(re.match(pattern, normalized, re.IGNORECASE))
    
    def lookup(self, postcode: str) -> List[Dict[str, str]]:
        """
        Look up addresses and UPRNs for a given postcode
        
        Args:
            postcode: UK postcode
            
        Returns:
            List of dictionaries with 'uprn' and 'address' keys
            
        Raises:
            UPRNLookupError: If lookup fails
        """
        if not self.validate_postcode(postcode):
            raise UPRNLookupError(f"Invalid postcode format: {postcode}")
        
        normalized_postcode = self._normalize_postcode(postcode)
        
        try:
            print(f"[UPRN LOOKUP SERVICE] Searching for: {normalized_postcode}")
            
            # iShare API JSONP request
            params = {
                'type': 'jsonp',
                'callback': 'processLocationResults',
                'service': 'LocationSearch',
                'RequestType': 'LocationSearch',
                'location': normalized_postcode,
                'pagesize': '150',
                'startnum': '1',
                'mapsource': 'mapsources/LocalInfoLookup'
            }
            
            print(f"[UPRN LOOKUP SERVICE] Calling: {self.ISHARE_SEARCH_URL}")
            
            response = self.session.get(
                self.ISHARE_SEARCH_URL,
                params=params,
                timeout=30
            )
            
            print(f"[UPRN LOOKUP SERVICE] Status: {response.status_code}")
            print(f"[UPRN LOOKUP SERVICE] Preview: {response.text[:200]}")
            
            response.raise_for_status()
            
            # Parse JSONP: processLocationResults({...})
            response_text = response.text.strip()
            
            if not response_text or len(response_text) < 10:
                raise UPRNLookupError("Empty response from iShare API")
            
            # Extract JSON from JSONP wrapper
            start = response_text.find('(')
            end = response_text.rfind(')')
            
            if start == -1 or end == -1:
                raise UPRNLookupError("Invalid JSONP format")
            
            json_str = response_text[start+1:end]
            
            if not json_str.strip():
                raise UPRNLookupError("No data in JSONP response")
            
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"[UPRN LOOKUP SERVICE] JSON error: {str(e)}")
                raise UPRNLookupError(f"Invalid JSON: {str(e)}")
            
            # iShare format: {"name": "...", "columns": [...], "data": [[uprn, parent, displayname, ...]]}
            if not isinstance(data, dict) or 'data' not in data:
                print(f"[UPRN LOOKUP SERVICE] Unexpected format: {json.dumps(data, indent=2)[:300]}")
                raise UPRNLookupError("Unexpected response format")
            
            locations = data.get('data', [])
            print(f"[UPRN LOOKUP SERVICE] Found {len(locations)} results")
            
            if not locations:
                raise UPRNLookupError(f"No addresses found for postcode: {normalized_postcode}")
            
            # Parse array format: [UniqueId, Parent, DisplayName, Type, X, Y, Rank, Name, Zoom]
            # Index 0 = UPRN, Index 2 = Display Name (address)
            addresses = []
            
            for i, loc in enumerate(locations):
                if not isinstance(loc, list) or len(loc) < 3:
                    continue
                
                uprn = str(loc[0]).strip() if loc[0] else None
                display_name = str(loc[2]).strip() if loc[2] else None
                
                if uprn and display_name:
                    # Clean HTML tags
                    display_name = re.sub(r'<[^>]*>', ' ', display_name)
                    display_name = re.sub(r'\s+', ' ', display_name).strip()
                    
                    # Validate UPRN
                    if uprn.isdigit() and len(uprn) >= 8:
                        addresses.append({
                            'uprn': uprn,
                            'address': display_name
                        })
                        print(f"[UPRN LOOKUP SERVICE] Added: {display_name[:60]}")
            
            if not addresses:
                raise UPRNLookupError(f"No valid addresses found for: {normalized_postcode}")
            
            print(f"[UPRN LOOKUP SERVICE] Returning {len(addresses)} addresses")
            return addresses
            
        except UPRNLookupError:
            raise
        except requests.exceptions.RequestException as e:
            print(f"[UPRN LOOKUP SERVICE] Request error: {str(e)}")
            raise UPRNLookupError(f"Failed to connect to iShare Maps API: {str(e)}")
        except Exception as e:
            print(f"[UPRN LOOKUP SERVICE] Unexpected error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise UPRNLookupError(f"Lookup failed: {str(e)}")
    
    def close(self):
        """Close the session"""
        self.session.close()
