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
    
    # Icon class to image URL mapping (from Swindon website)
    BIN_ICON_IMAGES = {
        "black-food-bin-icon": f"{BASE_URL}/images/black_wheelie_food_bin_swindon.png",
        "recycle-blue-weighted-food-icon": f"{BASE_URL}/images/recycling_blue_food_swindon.png",
        "recycle-blue-weighted-icon": f"{BASE_URL}/images/recycling_blue_weighted_swindon.png",
        "rubbish-blue-bag-food-icon": f"{BASE_URL}/images/rubbish_blue_bag_food_swindon.png",
        "garden-bin-icon": f"{BASE_URL}/images/green_waste_wheelie_swindon.png",
        "garden-bag-icon": f"{BASE_URL}/images/plastic_bag_green_swindon.png",
        "black-bin-icon": f"{BASE_URL}/images/black_wheelie_swindon.png",
        "refuse-communal-bin-icon": f"{BASE_URL}/images/communal_bin_swindon.png",
        "recycling-communal-bin-icon": f"{BASE_URL}/images/communal_recyling_swindon.png"
    }
    
    # Waste type to icon mapping (fallback)
    WASTE_TYPE_ICONS = {
        "Rubbish bin": "trash-can",
        "Rubbish bin and food waste": "trash-can",
        "Recycling boxes": "recycle",
        "Recycling and food waste": "recycle",
        "Garden waste bin": "leaf",
        "Garden waste": "leaf",
        "Plastics": "bottle"
    }
    
    # Waste type to color mapping
    WASTE_TYPE_COLORS = {
        "Rubbish bin": "rubbish",
        "Rubbish bin and food waste": "rubbish",
        "Recycling boxes": "recycling",
        "Recycling and food waste": "recycling",
        "Garden waste bin": "garden",
        "Garden waste": "garden",
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
                        delay = min(self.retry_delay * (2 ** attempt), 30)  # Cap at 30 seconds
                        time.sleep(delay)
                        continue
                    raise SwindonScraperError("Rate limited by server (403)")
                
                response.raise_for_status()
                return response
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed on attempt {attempt + 1}: {str(e)}")
                if attempt < self.max_retries - 1:
                    delay = min(self.retry_delay * (2 ** attempt), 30)  # Cap at 30 seconds
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
            # Make GET request with UPRN params (not POST!)
            params = {
                "uprnSubmit": "Yes",
                "addressList": uprn
            }
            
            logger.info(f"Fetching collections for UPRN {uprn}")
            print(f"[SCRAPER] GET request to {self.COLLECTION_URL} with UPRN {uprn}")
            
            response = self._make_request(
                self.COLLECTION_URL,
                method="GET",
                params=params
            )
            
            print(f"[SCRAPER] Response received, status: {response.status_code}")
            
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
                
                # Extract bin icon from bin-icons div
                bin_image_url = None
                bin_icons_div = section.find('div', class_='bin-icons')
                if bin_icons_div:
                    classes = bin_icons_div.get('class', [])
                    # Find which icon class is used
                    for icon_class in self.BIN_ICON_IMAGES.keys():
                        if icon_class in classes:
                            bin_image_url = self.BIN_ICON_IMAGES[icon_class]
                            print(f"[SCRAPER] Found bin icon: {icon_class} -> {bin_image_url}")
                            break
                
                # Get fallback icon and color for waste type
                icon = self.WASTE_TYPE_ICONS.get(waste_type, "trash-can")
                color = self.WASTE_TYPE_COLORS.get(waste_type, "")
                
                # Collect all dates for this bin type
                all_dates = []
                
                # Get next collection date
                date_elem = section.find('span', class_='nextCollectionDate')
                if date_elem:
                    date_text = date_elem.get_text(strip=True)
                    try:
                        collection_date = datetime.strptime(date_text, "%A, %d %B %Y").date()
                        all_dates.append(collection_date)
                    except ValueError:
                        try:
                            collection_date = datetime.strptime(date_text, "%d %B %Y").date()
                            all_dates.append(collection_date)
                        except ValueError:
                            logger.warning(f"Could not parse next date: {date_text}")
                
                # Get future collection dates
                future_div = section.find('div', class_='collection-next')
                if future_div:
                    future_dates = future_div.find_all('span', class_=['even', 'odd'])
                    for future_date_elem in future_dates:
                        date_text = future_date_elem.get_text(strip=True)
                        try:
                            collection_date = datetime.strptime(date_text, "%A, %d %B %Y").date()
                            all_dates.append(collection_date)
                        except ValueError:
                            try:
                                collection_date = datetime.strptime(date_text, "%d %B %Y").date()
                                all_dates.append(collection_date)
                            except ValueError:
                                logger.warning(f"Could not parse future date: {date_text}")
                
                # Create a collection entry with all dates
                if all_dates:
                    # Calculate days until first collection
                    days_until = (all_dates[0] - today).days
                    
                    collections.append({
                        "date": all_dates[0].isoformat(),  # Primary date (next collection)
                        "dates": [d.isoformat() for d in all_dates],  # All dates
                        "type": waste_type,
                        "icon": icon,
                        "color": color,
                        "days_until": days_until,
                        "bin_image": bin_image_url
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
