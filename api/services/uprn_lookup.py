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
import traceback

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
        logger.debug(f"Looking up postcode: {normalized_postcode}")
        
        try:
            # Step 1: Get the initial page to extract any hidden form fields
            response = self.session.get(self.COLLECTION_URL, timeout=30)
            response.raise_for_status()
            logger.debug(f"Initial page loaded, status: {response.status_code}")
            
            # Parse the initial page
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Step 2: Extract hidden form fields (common in many council websites)
            form = soup.find('form')
            form_data = {}
            
            if form:
                for input_field in form.find_all('input', type='hidden'):
                    name = input_field.get('name')
                    value = input_field.get('value', '')
                    if name:
                        form_data[name] = value
                        logger.debug(f"Found hidden field: {name}")
            
            # Step 3: Try multiple possible field names for postcode submission
            # Different councils use different field names
            postcode_field_names = ['postcode', 'Postcode', 'POSTCODE', 'pc', 'PostCode']
            submit_field_names = ['postcodeSubmit', 'submit', 'Submit', 'find', 'Find', 'search']
            
            # Add postcode to form data - try the most common field name first
            form_data['postcode'] = normalized_postcode
            
            # Also try adding common submit button values
            form_data['postcodeSubmit'] = 'Find Address'
            
            # Log form field names for debugging (not values to protect sensitive data)
            logger.debug(f"Form fields being submitted: {list(form_data.keys())}")
            
            # Step 4: Submit the form
            response = self.session.post(
                self.COLLECTION_URL,
                data=form_data,
                timeout=30
            )
            response.raise_for_status()
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response content length: {len(response.content)}")
            
            # Step 5: Parse the response to find address dropdown
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple selectors to find the address dropdown
            address_select = None
            
            # Common selector patterns for UK council websites
            selectors = [
                ('name', 'addressList'),
                ('name', 'address'),
                ('name', 'uprn'),
                ('name', 'addressSelect'),
                ('id', 'addressList'),
                ('id', 'address'),
                ('id', 'uprn'),
            ]
            
            for attr_type, attr_value in selectors:
                address_select = soup.find('select', {attr_type: attr_value})
                if address_select:
                    logger.debug(f"Found address select with {attr_type}='{attr_value}'")
                    break
            
            # If still not found, try regex search
            if not address_select:
                address_select = soup.find('select', id=re.compile(r'address', re.IGNORECASE))
                if address_select:
                    logger.debug(f"Found address select with regex match")
            
            if not address_select:
                # Log sanitized HTML structure for debugging (without content to avoid exposing sensitive data)
                form_tags = soup.find_all('form')
                select_tags = soup.find_all('select')
                logger.warning(f"No address dropdown found. Found {len(form_tags)} form(s) and {len(select_tags)} select element(s)")
                
                # Check if there's an error message on the page
                error_msg = soup.find('div', class_=re.compile(r'error', re.IGNORECASE))
                if error_msg:
                    logger.error(f"Error message found: {error_msg.get_text(strip=True)}")
                
                raise UPRNLookupError(f"No addresses found for postcode: {normalized_postcode}")
            
            addresses = []
            
            # Step 6: Parse options from select dropdown
            for option in address_select.find_all('option'):
                uprn = option.get('value', '').strip()
                address_text = option.get_text(strip=True)
                
                # Skip empty or placeholder options
                if not uprn or 'Select' in address_text or 'Choose' in address_text or '--' in address_text:
                    continue
                
                # UPRN validation - UK UPRNs are typically 10-12 digits
                if uprn.isdigit() and len(uprn) >= 10:
                    addresses.append({
                        'uprn': uprn,
                        'address': address_text
                    })
                    logger.debug(f"Found valid address: UPRN={uprn}, Address={address_text[:50]}...")
            
            if not addresses:
                logger.warning(f"No valid addresses found in dropdown for postcode: {normalized_postcode}")
                raise UPRNLookupError(f"No valid addresses found for postcode: {normalized_postcode}")
            
            logger.info(f"Found {len(addresses)} addresses for postcode {normalized_postcode}")
            return addresses
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for postcode {postcode}: {str(e)}")
            raise UPRNLookupError(f"Failed to connect to Swindon Council website: {str(e)}")
        except UPRNLookupError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            logger.error(f"Unexpected error during lookup: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise UPRNLookupError(f"Lookup failed: {str(e)}")
    
    def close(self):
        """Close the session"""
        self.session.close()
