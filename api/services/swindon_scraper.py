"""
Swindon Borough Council Waste Collection Scraper

Adapted from: https://github.com/mampfes/hacs_waste_collection_schedule
Original Author: Steffen Zimmermann
Original License: MIT License

This module scrapes waste collection information from Swindon Borough Council's website.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time
import logging

logger = logging.getLogger(__name__)


class SwindonScraperError(Exception):
    """Custom exception for scraper errors"""
    pass


class SwindonScraper:
    """Scraper for Swindon Borough Council waste collection data"""
    
    BASE_URL = "https://www.swindon.gov.uk"
    COLLECTION_URL = f"{BASE_URL}/info/20122/rubbish_and_recycling_collection_days"
    
    # Waste type to icon mapping
    WASTE_TYPE_ICONS = {
        "Rubbish bin": "trash-can",
        "Recycling boxes": "recycle",
        "Garden waste bin": "leaf",
        "Plastics": "bottle"
    }
    
    # Waste type to color mapping
    WASTE_TYPE_COLORS = {
        "Rubbish bin": "rubbish",
        "Recycling boxes": "recycling",
        "Garden waste bin": "garden",
        "Plastics": "plastics"
    }
    
    def __init__(self, max_retries: int = 3, retry_delay: int = 2):
        """
        Initialize the scraper
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Base delay between retries in seconds
        """
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _make_request(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """
        Make HTTP request with retry logic
        
        Args:
            url: URL to request
            method: HTTP method
            **kwargs: Additional arguments for requests
            
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
                
                if response.status_code == 403:
                    logger.warning(f"Rate limited (403) on attempt {attempt + 1}")
                    if attempt < self.max_retries - 1:
                        delay = self.retry_delay * (2 ** attempt)  # Exponential backoff
                        time.sleep(delay)
                        continue
                    raise SwindonScraperError("Rate limited by server (403)")
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    delay = self.retry_delay * (2 ** attempt)
                    time.sleep(delay)
                else:
                    raise SwindonScraperError(f"Failed to fetch data: {str(e)}")
        
        raise SwindonScraperError("Max retries exceeded")
    
    def get_collections(self, uprn: str) -> List[Dict]:
        """
        Get waste collection schedule for a given UPRN
        
        Args:
            uprn: Unique Property Reference Number
            
        Returns:
            List of collection dictionaries with date, type, icon, and days_until
            
        Raises:
            SwindonScraperError: If scraping fails
        """
        try:
            # Make POST request to get collection data
            data = {
                "uprnSubmit": "Yes",
                "addressList": uprn
            }
            
            response = self._make_request(
                self.COLLECTION_URL,
                method="POST",
                data=data
            )
            
            # Parse HTML response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            collections = []
            today = datetime.now().date()
            
            # Find all bin collection content divs
            bin_sections = soup.find_all('div', class_='bin-collection-content')
            
            if not bin_sections:
                logger.warning(f"No collection sections found for UPRN {uprn}")
                return []
            
            for section in bin_sections:
                # Extract waste type from h3
                waste_type_elem = section.find('h3')
                if not waste_type_elem:
                    continue
                
                waste_type = waste_type_elem.get_text(strip=True)
                
                # Extract collection date
                date_elem = section.find('span', class_='nextCollectionDate')
                if not date_elem:
                    continue
                
                date_text = date_elem.get_text(strip=True)
                
                # Parse date - format is typically "Day, DD Month YYYY"
                try:
                    collection_date = datetime.strptime(date_text, "%A, %d %B %Y").date()
                except ValueError:
                    # Try alternative format
                    try:
                        collection_date = datetime.strptime(date_text, "%d %B %Y").date()
                    except ValueError:
                        logger.warning(f"Could not parse date: {date_text}")
                        continue
                
                # Calculate days until collection
                days_until = (collection_date - today).days
                
                # Get icon and color for waste type
                icon = self.WASTE_TYPE_ICONS.get(waste_type, "trash-can")
                
                collections.append({
                    "date": collection_date.isoformat(),
                    "type": waste_type,
                    "icon": icon,
                    "days_until": days_until
                })
            
            # Sort by date
            collections.sort(key=lambda x: x['date'])
            
            return collections
            
        except Exception as e:
            logger.error(f"Error scraping collections for UPRN {uprn}: {str(e)}")
            raise SwindonScraperError(f"Failed to get collections: {str(e)}")
    
    def close(self):
        """Close the session"""
        self.session.close()
