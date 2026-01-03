"""
Swindon Borough Council Waste Collection Scraper

Fresh implementation that scrapes waste collection schedules from the
Swindon Borough Council website.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
from typing import List, Dict
import time
import logging

logger = logging.getLogger(__name__)


class SwindonScraperError(Exception):
    """Custom exception for scraper errors"""
    pass


class SwindonScraper:
    """
    Scraper for Swindon Borough Council waste collection data
    
    This scraper fetches collection schedules by:
    1. Submitting a POST request with UPRN as query parameters
    2. Parsing the HTML response for collection information
    3. Extracting dates and waste types from specific HTML elements
    """
    
    BASE_URL = "https://www.swindon.gov.uk"
    COLLECTION_URL = f"{BASE_URL}/info/20122/rubbish_and_recycling_collection_days"
    
    # Icon mapping for different waste types
    WASTE_TYPE_ICONS = {
        "Rubbish bin": "trash-can",
        "Recycling boxes": "recycle",
        "Garden waste bin": "leaf",
        "Plastics": "bottle"
    }
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize the scraper with retry configuration
        
        Args:
            max_retries: Maximum number of retry attempts for failed requests
            retry_delay: Base delay in seconds between retries (uses exponential backoff)
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })
    
    def _make_request(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """
        Make HTTP request with retry logic and exponential backoff
        
        Args:
            url: URL to request
            method: HTTP method (GET or POST)
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Response object
            
        Raises:
            SwindonScraperError: If request fails after all retries
        """
        for attempt in range(self.max_retries):
            try:
                if method == "GET":
                    response = self.session.get(url, timeout=30, **kwargs)
                else:
                    response = self.session.post(url, timeout=30, **kwargs)
                
                # Check for rate limiting
                if response.status_code == 403:
                    logger.warning(f"Rate limited (403) on attempt {attempt + 1}")
                    if attempt < self.max_retries - 1:
                        delay = min(self.retry_delay * (2 ** attempt), 30)
                        time.sleep(delay)
                        continue
                    raise SwindonScraperError("Rate limited by server (403)")
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    delay = min(self.retry_delay * (2 ** attempt), 30)
                    time.sleep(delay)
                else:
                    raise SwindonScraperError(f"Failed to fetch data: {str(e)}")
        
        raise SwindonScraperError("Max retries exceeded")
    
    def get_collections(self, uprn: str) -> List[Dict]:
        """
        Get waste collection schedule for a given UPRN
        
        This method:
        1. Sends POST request with UPRN as query parameters (not form data)
        2. Parses HTML to find div.bin-collection-content elements
        3. Extracts collection dates and waste types
        4. Calculates days until each collection
        
        Args:
            uprn: Unique Property Reference Number
            
        Returns:
            List of collection dictionaries with keys:
            - date (str): ISO format date (YYYY-MM-DD)
            - type (str): Waste type (e.g., "Rubbish bin", "Recycling boxes")
            - icon (str): Icon identifier
            - days_until (int): Days until collection
            
        Raises:
            SwindonScraperError: If scraping fails
        """
        logger.info(f"Fetching collections for UPRN: {uprn}")
        
        try:
            # Use query parameters, not form data
            # This matches the actual website behavior
            params = {
                "uprnSubmit": "Yes",
                "addressList": uprn
            }
            
            response = self._make_request(
                self.COLLECTION_URL,
                method="POST",
                params=params
            )
            
            # Parse HTML response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all bin collection content divs
            bin_sections = soup.find_all('div', class_='bin-collection-content')
            
            if not bin_sections:
                logger.warning(f"No collection sections found for UPRN {uprn}")
                return []
            
            collections = []
            today = datetime.now().date()
            
            for section in bin_sections:
                try:
                    # Extract waste type from h3 inside content-left div
                    content_left = section.find('div', class_='content-left')
                    if not content_left:
                        continue
                    
                    waste_type_elem = content_left.find('h3')
                    if not waste_type_elem:
                        continue
                    
                    waste_type = waste_type_elem.get_text(strip=True)
                    
                    # Extract collection date from span with class nextCollectionDate
                    date_elem = section.find('span', class_='nextCollectionDate')
                    if not date_elem:
                        continue
                    
                    date_text = date_elem.get_text(strip=True)
                    
                    # Parse date using dateutil parser for flexibility
                    # This handles various date formats automatically
                    collection_date = parser.parse(date_text, dayfirst=True).date()
                    
                    # Calculate days until collection
                    days_until = (collection_date - today).days
                    
                    # Get icon for waste type
                    icon = self.WASTE_TYPE_ICONS.get(waste_type, "trash-can")
                    
                    collections.append({
                        "date": collection_date.isoformat(),
                        "type": waste_type,
                        "icon": icon,
                        "days_until": days_until
                    })
                    
                except (ValueError, TypeError, AttributeError) as e:
                    logger.warning(f"Failed to parse collection entry: {str(e)}")
                    continue
            
            # Sort by date (earliest first)
            collections.sort(key=lambda x: x['date'])
            
            logger.info(f"Found {len(collections)} collections for UPRN {uprn}")
            return collections
            
        except SwindonScraperError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            logger.error(f"Error scraping collections for UPRN {uprn}: {str(e)}", exc_info=True)
            raise SwindonScraperError(f"Failed to get collections: {str(e)}")
    
    def close(self):
        """Close the HTTP session and release resources"""
        self.session.close()
