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
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
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
            # Step 1: Get the initial page to capture any hidden fields
            logger.info(f"Fetching initial page for postcode: {normalized_postcode}")
            response = self.session.get(self.COLLECTION_URL, timeout=30)
            response.raise_for_status()
            
            # Parse the initial page
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the form
            form = soup.find('form')
            form_data = {}
            
            # Extract all hidden form fields (important for ASP.NET sites)
            if form:
                for input_field in form.find_all('input', type='hidden'):
                    name = input_field.get('name')
                    value = input_field.get('value', '')
                    if name:
                        form_data[name] = value
                        logger.debug(f"Found hidden field: {name}")
            
            # Add postcode - try common field names
            form_data['postcode'] = normalized_postcode
            form_data['postcodeSubmit'] = 'Find'
            
            logger.info(f"Submitting postcode lookup with {len(form_data)} form fields")
            
            # Step 2: Submit the postcode
            response = self.session.post(
                self.COLLECTION_URL,
                data=form_data,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()
            
            logger.debug(f"Response status: {response.status_code}, Content length: {len(response.content)}")
            
            # Step 3: Parse response to find address dropdown
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple possible selectors for address dropdown
            address_select = None
            selectors = [
                ('name', 'addressList'),
                ('name', 'address'),
                ('name', 'uprn'),
                ('id', 'addressList'),
                ('id', 'address'),
            ]
            
            for attr, value in selectors:
                address_select = soup.find('select', {attr: value})
                if address_select:
                    logger.info(f"Found address dropdown with {attr}='{value}'")
                    break
            
            # If still not found, try regex pattern
            if not address_select:
                address_select = soup.find('select', attrs={'name': re.compile(r'address', re.IGNORECASE)})
                if address_select:
                    logger.info(f"Found address dropdown with regex pattern")
            
            # If still not found, get ANY select on the page and log it
            if not address_select:
                all_selects = soup.find_all('select')
                logger.warning(f"No address dropdown found. Found {len(all_selects)} select elements total")
                for sel in all_selects:
                    logger.debug(f"Select found: name={sel.get('name')}, id={sel.get('id')}")
                
                # If there's only one select, use it
                if len(all_selects) == 1:
                    address_select = all_selects[0]
                    logger.info("Using the only select element found")
            
            if not address_select:
                logger.warning(f"No address dropdown found for postcode: {normalized_postcode}")
                # Log part of the HTML for debugging
                logger.debug(f"HTML snippet: {soup.prettify()[:1000]}")
                raise UPRNLookupError(f"No addresses found for postcode: {normalized_postcode}. The website structure may have changed.")
            
            addresses = []
            
            # Parse options from select dropdown
            options = address_select.find_all('option')
            logger.info(f"Found {len(options)} options in address dropdown")
            
            for option in options:
                uprn = option.get('value', '').strip()
                address_text = option.get_text(strip=True)
                
                logger.debug(f"Processing option: value='{uprn}', text='{address_text}'")
                
                # Skip empty or placeholder options
                if not uprn or uprn == '' or uprn == '0':
                    continue
                
                if any(word in address_text.lower() for word in ['select', 'choose', 'please']):
                    continue
                
                # UPRN validation - should be numeric and reasonable length
                if uprn.isdigit() and len(uprn) >= 8:  # UK UPRNs are typically 10-12 digits
                    addresses.append({
                        'uprn': uprn,
                        'address': address_text
                    })
                    logger.debug(f"Added address: {address_text}")
            
            if not addresses:
                raise UPRNLookupError(f"No valid addresses found for postcode: {normalized_postcode}")
            
            logger.info(f"Successfully found {len(addresses)} addresses for postcode {normalized_postcode}")
            return addresses
            
        except UPRNLookupError:
            # Re-raise our custom errors
            raise
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed for postcode {postcode}: {str(e)}")
            raise UPRNLookupError(f"Failed to connect to Swindon Council website: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during lookup: {str(e)}", exc_info=True)
            raise UPRNLookupError(f"Lookup failed: {str(e)}")
    
    def close(self):
        """Close the session"""
        self.session.close()
