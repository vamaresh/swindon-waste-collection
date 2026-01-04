#!/usr/bin/env python3
"""
Debug script to inspect the Swindon website structure
"""

import requests
from bs4 import BeautifulSoup

URL = "https://www.swindon.gov.uk/info/20122/rubbish_and_recycling_collection_days"

print("Fetching Swindon waste collection page...")
print(f"URL: {URL}\n")

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

try:
    # Get initial page
    response = session.get(URL, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Content Length: {len(response.content)} bytes\n")
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all forms
    print("="*60)
    print("FORMS ON PAGE:")
    print("="*60)
    forms = soup.find_all('form')
    print(f"Found {len(forms)} form(s)\n")
    
    for i, form in enumerate(forms, 1):
        print(f"Form {i}:")
        print(f"  Action: {form.get('action')}")
        print(f"  Method: {form.get('method')}")
        print(f"  ID: {form.get('id')}")
        print()
    
    # Find all input fields
    print("="*60)
    print("INPUT FIELDS:")
    print("="*60)
    inputs = soup.find_all('input')
    print(f"Found {len(inputs)} input(s)\n")
    
    for inp in inputs[:20]:  # First 20
        print(f"  Type: {inp.get('type', 'text'):15} Name: {inp.get('name', 'N/A'):30} ID: {inp.get('id', 'N/A')}")
    
    if len(inputs) > 20:
        print(f"  ... and {len(inputs) - 20} more\n")
    
    # Find all select dropdowns
    print("\n" + "="*60)
    print("SELECT DROPDOWNS:")
    print("="*60)
    selects = soup.find_all('select')
    print(f"Found {len(selects)} select dropdown(s)\n")
    
    for sel in selects:
        print(f"  Name: {sel.get('name', 'N/A')}")
        print(f"  ID: {sel.get('id', 'N/A')}")
        options = sel.find_all('option')
        print(f"  Options: {len(options)}")
        print()
    
    # Look for postcode-related elements
    print("="*60)
    print("POSTCODE-RELATED ELEMENTS:")
    print("="*60)
    
    postcode_inputs = soup.find_all(['input', 'button'], attrs={'name': lambda x: x and 'postcode' in x.lower()})
    postcode_inputs += soup.find_all(['input', 'button'], attrs={'id': lambda x: x and 'postcode' in x.lower()})
    postcode_inputs += soup.find_all(['input', 'button'], attrs={'value': lambda x: x and 'postcode' in str(x).lower()})
    
    print(f"Found {len(postcode_inputs)} postcode-related element(s)\n")
    for elem in postcode_inputs:
        print(f"  Tag: {elem.name}")
        print(f"  Type: {elem.get('type', 'N/A')}")
        print(f"  Name: {elem.get('name', 'N/A')}")
        print(f"  ID: {elem.get('id', 'N/A')}")
        print(f"  Value: {elem.get('value', 'N/A')}")
        print()
    
    # Save HTML for manual inspection
    with open('/tmp/swindon_page.html', 'w') as f:
        f.write(soup.prettify())
    print("\n✓ Full HTML saved to /tmp/swindon_page.html for inspection")
    
    # Test postcode submission
    print("\n" + "="*60)
    print("TESTING POSTCODE SUBMISSION:")
    print("="*60)
    
    test_postcode = "SN1 1JJ"
    
    # Try to find the form and extract all fields
    form = soup.find('form')
    if form:
        form_data = {}
        
        # Get all hidden fields
        for hidden in form.find_all('input', type='hidden'):
            name = hidden.get('name')
            value = hidden.get('value', '')
            if name:
                form_data[name] = value
                print(f"  Hidden field: {name} = {value[:50]}")
        
        # Add postcode
        form_data['postcode'] = test_postcode
        form_data['postcodeSubmit'] = 'Find'
        
        print(f"\nSubmitting with postcode: {test_postcode}")
        print(f"Total form fields: {len(form_data)}\n")
        
        # Submit
        response2 = session.post(URL, data=form_data, timeout=30, allow_redirects=True)
        print(f"Response status: {response2.status_code}")
        print(f"Response URL: {response2.url}")
        print(f"Content length: {len(response2.content)} bytes")
        
        soup2 = BeautifulSoup(response2.content, 'html.parser')
        
        # Check for select dropdowns in response
        selects2 = soup2.find_all('select')
        print(f"\nSelect dropdowns in response: {len(selects2)}")
        
        for sel in selects2:
            print(f"  Name: {sel.get('name', 'N/A')}, ID: {sel.get('id', 'N/A')}")
            options = sel.find_all('option')
            print(f"  Options: {len(options)}")
            for opt in options[:5]:
                print(f"    - {opt.get_text(strip=True)[:60]}")
            if len(options) > 5:
                print(f"    ... and {len(options) - 5} more")
        
        # Save response for inspection
        with open('/tmp/swindon_response.html', 'w') as f:
            f.write(soup2.prettify())
        print("\n✓ Response HTML saved to /tmp/swindon_response.html")
    
except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()
