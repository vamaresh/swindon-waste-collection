"""
UPRN Lookup Service for Swindon Borough Council

Fresh implementation that scrapes the Swindon Borough Council website
to convert UK postcodes into UPRNs (Unique Property Reference Numbers).
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
    """
    Service for looking up UPRNs from postcodes by scraping
    the Swindon Borough Council waste collection website.
    """
    
    BASE_URL = "https://www.swindon.gov.uk"
    COLLECTION_URL = f"{BASE_URL}/info/20122/rubbish_and_recycling_collection_days"
    
    def __init__(self):
        """Initialize the lookup service with proper headers"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def _normalize_postcode(self, postcode: str) -> str:
        """
        Normalize UK postcode format to standard form (e.g., 'SN1 5DX')
        
        Args:
            postcode: Raw postcode string
            
        Returns:
            Normalized postcode with space before last 3 characters
        """
        # Remove all spaces and convert to uppercase
        postcode = postcode.replace(" ", "").upper()
        
        # Add space before last 3 characters if valid length
        if len(postcode) >= 5:
            postcode = f"{postcode[:-3]} {postcode[-3:]}"
        
        return postcode
    
    def validate_postcode(self, postcode: str) -> bool:
        """
        Validate UK postcode format using regex pattern
        
        Args:
            postcode: Postcode to validate
            
        Returns:
            True if valid UK postcode, False otherwise
        """
        # UK postcode regex pattern
        pattern = r'^[A-Z]{1,2}[0-9]{1,2}[A-Z]?\s?[0-9][A-Z]{2}$'
        normalized = self._normalize_postcode(postcode)
        return bool(re.match(pattern, normalized, re.IGNORECASE))
    
    def lookup(self, postcode: str) -> List[Dict[str, str]]:
        """
        Look up addresses and UPRNs for a given postcode
        
        This implementation scrapes the Swindon Council website by:
        1. Getting the initial form page
        2. Submitting the postcode via POST
        3. Parsing the returned address dropdown
        4. Extracting UPRNs and addresses from options
        
        Args:
            postcode: UK postcode (e.g., 'SN1 5DX')
            
        Returns:
            List of dictionaries with 'uprn' and 'address' keys
            Example: [{'uprn': '100121147490', 'address': '1 Nyland Road, SWINDON, SN1 5DX'}]
            
        Raises:
            UPRNLookupError: If postcode is invalid or lookup fails
        """
        # Validate postcode format
        if not self.validate_postcode(postcode):
            raise UPRNLookupError(f"Invalid postcode format: {postcode}")
        
        normalized_postcode = self._normalize_postcode(postcode)
        logger.info(f"Looking up addresses for postcode: {normalized_postcode}")
        
        try:
            # Step 1: GET the initial page to capture form structure and hidden fields
            response = self.session.get(self.COLLECTION_URL, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract form data including hidden fields (common in ASP.NET sites)
            form = soup.find('form')
            form_data = {}
            
            if form:
                # Get all hidden input fields (viewstate, csrf tokens, etc.)
                for input_field in form.find_all('input', type='hidden'):
                    name = input_field.get('name')
                    value = input_field.get('value', '')
                    if name:
                        form_data[name] = value
            
            # Add the postcode field - try common field names used by councils
            form_data['postcode'] = normalized_postcode
            form_data['postcodeSubmit'] = 'Find'
            
            logger.debug(f"Submitting form with {len(form_data)} fields")
            
            # Step 2: POST the form with postcode
            response = self.session.post(
                self.COLLECTION_URL,
                data=form_data,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            
            # Step 3: Parse the response to find address dropdown
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the address select element - try multiple selectors
            address_select = None
            selectors = [
                ('name', 'addressList'),  # Most common
                ('name', 'address'),
                ('name', 'uprn'),
                ('id', 'addressList'),
                ('id', 'address'),
            ]
            
            for attr, value in selectors:
                address_select = soup.find('select', {attr: value})
                if address_select:
                    logger.debug(f"Found address dropdown: {attr}='{value}'")
                    break
            
            # Fallback: search for any select with 'address' in name/id
            if not address_select:
                address_select = soup.find('select', attrs={'name': re.compile(r'address', re.IGNORECASE)})
                if not address_select:
                    address_select = soup.find('select', attrs={'id': re.compile(r'address', re.IGNORECASE)})
            
            # Final fallback: if only one select element exists, use it
            if not address_select:
                all_selects = soup.find_all('select')
                if len(all_selects) == 1:
                    address_select = all_selects[0]
                    logger.debug("Using the only select element found")
            
            if not address_select:
                raise UPRNLookupError(
                    f"No addresses found for postcode: {normalized_postcode}. "
                    "The postcode may be invalid or the website structure has changed."
                )
            
            # Step 4: Extract addresses and UPRNs from dropdown options
            addresses = []
            options = address_select.find_all('option')
            
            logger.debug(f"Found {len(options)} options in address dropdown")
            
            for option in options:
                uprn = option.get('value', '').strip()
                address_text = option.get_text(strip=True)
                
                # Skip empty values or placeholder options
                if not uprn or uprn in ('', '0', '-1'):
                    continue
                
                # Skip placeholder text like "Select an address", "Choose...", etc.
                if any(word in address_text.lower() for word in ['select', 'choose', 'please']):
                    continue
                
                # Validate UPRN - should be numeric and reasonable length
                # UK UPRNs are typically 10-12 digits but can be shorter
                if uprn.isdigit() and len(uprn) >= 8:
                    addresses.append({
                        'uprn': uprn,
                        'address': address_text
                    })
            
            if not addresses:
                raise UPRNLookupError(
                    f"No valid addresses found for postcode: {normalized_postcode}. "
                    "The postcode may not be in the Swindon area."
                )
            
            logger.info(f"Successfully found {len(addresses)} addresses")
            return addresses
            
        except UPRNLookupError:
            # Re-raise our custom errors without modification
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error during lookup: {str(e)}")
            raise UPRNLookupError(f"Failed to connect to Swindon Council website: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during lookup: {str(e)}", exc_info=True)
            raise UPRNLookupError(f"Lookup failed: {str(e)}")
    
    def close(self):
        """Close the HTTP session and release resources"""
        self.session.close()
