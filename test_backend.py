#!/usr/bin/env python3
"""
Test script for backend scraping functionality
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.services.uprn_lookup import UPRNLookupService, UPRNLookupError
from api.services.swindon_scraper import SwindonScraper, SwindonScraperError

def test_uprn_lookup(postcode):
    """Test UPRN lookup for a postcode"""
    print(f"\n{'='*60}")
    print(f"Testing UPRN Lookup for postcode: {postcode}")
    print(f"{'='*60}\n")
    
    service = UPRNLookupService()
    try:
        addresses = service.lookup(postcode)
        print(f"\n✓ SUCCESS: Found {len(addresses)} addresses\n")
        
        for i, addr in enumerate(addresses, 1):
            print(f"{i}. {addr['address']}")
            print(f"   UPRN: {addr['uprn']}\n")
        
        return addresses
    except UPRNLookupError as e:
        print(f"\n✗ ERROR: {str(e)}\n")
        return []
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return []
    finally:
        service.close()

def test_collections(uprn):
    """Test collection scraping for a UPRN"""
    print(f"\n{'='*60}")
    print(f"Testing Collections for UPRN: {uprn}")
    print(f"{'='*60}\n")
    
    scraper = SwindonScraper()
    try:
        collections = scraper.get_collections(uprn)
        print(f"\n✓ SUCCESS: Found {len(collections)} collections\n")
        
        for col in collections:
            print(f"• {col['type']}")
            print(f"  Date: {col['date']}")
            print(f"  Days until: {col['days_until']}")
            print(f"  Icon: {col['icon']}")
            print(f"  Color: {col.get('color', 'N/A')}\n")
        
        return collections
    except SwindonScraperError as e:
        print(f"\n✗ ERROR: {str(e)}\n")
        return []
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return []
    finally:
        scraper.close()

if __name__ == "__main__":
    # Test with a Swindon postcode (SN1 is Swindon area)
    test_postcode = "SN1 1JJ"  # Example: Swindon Borough Council address
    
    if len(sys.argv) > 1:
        test_postcode = sys.argv[1]
    
    print("\n" + "="*60)
    print("SWINDON WASTE COLLECTION BACKEND TEST")
    print("="*60)
    
    # Step 1: Test UPRN lookup
    addresses = test_uprn_lookup(test_postcode)
    
    # Step 2: If addresses found, test collections for first address
    if addresses:
        print("\n" + "-"*60)
        print("Now testing collections for the first address...")
        print("-"*60)
        
        first_uprn = addresses[0]['uprn']
        collections = test_collections(first_uprn)
        
        if collections:
            print("\n" + "="*60)
            print("✓ ALL TESTS PASSED!")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("✗ Collections test failed")
            print("="*60)
    else:
        print("\n" + "="*60)
        print("✗ No addresses found - cannot test collections")
        print("="*60)
