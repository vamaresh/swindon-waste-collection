#!/usr/bin/env python3
"""
Test direct form submission to Swindon site
"""

import requests
from bs4 import BeautifulSoup
import json

URL = "https://www.swindon.gov.uk/info/20122/rubbish_and_recycling_collection_days"
postcode = "SN1 1JJ"

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
})

print(f"Testing form submission for: {postcode}\n")

# Step 1: Get the page
print("Step 1: Fetching initial page...")
response = session.get(URL)
print(f"Status: {response.status_code}\n")

soup = BeautifulSoup(response.content, 'html.parser')

# Step 2: Try to trigger JavaScript by looking for the actual form implementation
# The site uses AJAX, so we need to call the iShare API directly

# Let's try to emulate what the JavaScript does
print("Step 2: Attempting direct iShare API call...")

# Based on the widget code, it calls:
# iShareMapsURL + '/getdata.aspx?callback=?&type=jsonp&service=LocationSearch&RequestType=LocationSearch&location=' + query

# Try without JSONP first
params = {
    'service': 'LocationSearch',
    'RequestType': 'LocationSearch',
    'location': postcode,
    'pagesize': '150',
    'mapsource': 'mapsources/LocalInfoLookup'
}

ishare_url = "https://maps.swindon.gov.uk/getdata.aspx"

print(f"Calling: {ishare_url}")
print(f"Params: {json.dumps(params, indent=2)}\n")

try:
    response2 = session.get(ishare_url, params=params, timeout=30)
    print(f"Response status: {response2.status_code}")
    print(f"Response length: {len(response2.content)} bytes")
    print(f"Response content: {response2.text[:500]}\n")
    
    if response2.status_code == 200:
        try:
            data = response2.json()
            print("JSON Response:")
            print(json.dumps(data, indent=2)[:1000])
        except:
            print("Not JSON response")
            
except Exception as e:
    print(f"Error: {str(e)}\n")

# Step 3: Try with Referer header (maybe it's checking)
print("Step 3: Trying with Referer header...")
session.headers['Referer'] = URL

try:
    response3 = session.get(ishare_url, params=params, timeout=30)
    print(f"Response status: {response3.status_code}")
    print(f"Response: {response3.text[:300]}\n")
except Exception as e:
    print(f"Error: {str(e)}\n")

# Step 4: Maybe we need to actually use JSONP callback parameter
print("Step 4: Trying JSONP format...")
params_jsonp = {
    'type': 'jsonp',
    'callback': 'jQuery123',
    'service': 'LocationSearch',
    'RequestType': 'LocationSearch', 
    'location': postcode,
    'pagesize': '150',
    'startnum': '1',
    'mapsource': 'mapsources/LocalInfoLookup'
}

try:
    response4 = session.get(ishare_url, params=params_jsonp, timeout=30)
    print(f"Response status: {response4.status_code}")
    print(f"Response: {response4.text[:500]}\n")
    
    # Parse JSONP (remove callback wrapper)
    text = response4.text
    if text.startswith('jQuery'):
        # Extract JSON from JSONP
        start = text.find('(')
        end = text.rfind(')')
        if start != -1 and end != -1:
            json_str = text[start+1:end]
            data = json.loads(json_str)
            print("Parsed JSONP data:")
            print(json.dumps(data, indent=2)[:2000])
            
            if 'data' in data:
                print(f"\nFound {len(data['data'])} results!")
                for i, item in enumerate(data['data'][:3]):
                    print(f"\n  Result {i+1}:")
                    print(f"    UPRN (val[0]): {item[0]}")
                    print(f"    Name (val[1]): {item[1]}")
                    print(f"    Address (val[2]): {item[2]}")
                    
except Exception as e:
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
