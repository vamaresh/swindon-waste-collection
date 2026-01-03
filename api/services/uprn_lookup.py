"""
UPRN Lookup Service for Swindon Borough Council

This module provides postcode to UPRN (Unique Property Reference Number) lookup
by scraping Swindon Borough Council's address search.
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import logging
import re

logger = logging.getLogger(__name__)


class UPRNLookupError(Exception):
    """Custom exception for UPRN lookup errors"""
    pass


class UPRNLookupService:
    """Service for looking up UPRN from postcode"""
    
    BASE_URL = "https://www.swindon.gov.uk"
    COLLECTION_URL = f"{BASE_URL}/info/20122/rubbish_and_recycling_collection_days"
    
    def __init__(self):
        """Initialize the lookup service"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _normalize_postcode(self, postcode: str) -> str:
        """
        Normalize UK postcode format
        
        Args:
            postcode: Raw postcode string
            
        Returns:
            Normalized postcode
        """
        # Remove spaces and convert to uppercase
        postcode = postcode.replace(" ", "").upper()
        
        # Add space before last 3 characters if missing
        if len(postcode) >= 5:
            postcode = f"{postcode[:-3]} {postcode[-3:]}"
        
        return postcode
    
    def validate_postcode(self, postcode: str) -> bool:
        """
        Validate UK postcode format
        
        Args:
            postcode: Postcode to validate
            
        Returns:
            True if valid, False otherwise
        """
        # UK postcode regex pattern
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
            # First, get the page to extract any necessary form data
            response = self.session.get(self.COLLECTION_URL, timeout=30)
            response.raise_for_status()
            
            # Parse the initial page
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Submit postcode to get address list
            # The form typically has a postcode input field
            data = {
                "postcode": normalized_postcode,
                "postcodeSubmit": "Find Address"
            }
            
            response = self.session.post(
                self.COLLECTION_URL,
                data=data,
                timeout=30
            )
            response.raise_for_status()
            
            # Parse response to find address dropdown
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for address select dropdown
            address_select = soup.find('select', {'name': 'addressList'})
            
            if not address_select:
                # Try alternative approach - look for any select with addresses
                address_select = soup.find('select', id=re.compile(r'address', re.IGNORECASE))
            
            if not address_select:
                logger.warning(f"No addresses found for postcode: {normalized_postcode}")
                return []
            
            addresses = []
            
            # Parse options from select dropdown
            for option in address_select.find_all('option'):
                uprn = option.get('value', '').strip()
                address_text = option.get_text(strip=True)
                
                # Skip empty or placeholder options
                if not uprn or uprn == '' or 'Select' in address_text:
                    continue
                
                # UPRN should be numeric
                if not uprn.isdigit():
                    continue
                
                addresses.append({
                    'uprn': uprn,
                    'address': address_text
                })
            
            logger.info(f"Found {len(addresses)} addresses for postcode {normalized_postcode}")
            return addresses
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for postcode {postcode}: {str(e)}")
            raise UPRNLookupError(f"Failed to lookup postcode: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during lookup: {str(e)}")
            raise UPRNLookupError(f"Lookup failed: {str(e)}")
    
    def close(self):
        """Close the session"""
        self.session.close()
