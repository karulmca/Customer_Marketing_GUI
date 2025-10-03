#!/usr/bin/env python3
"""
LinkedIn Blocking Analysis - Understanding why requests get blocked
"""

import requests
import time
import random
from bs4 import BeautifulSoup

def test_linkedin_blocking():
    """Test different scenarios to understand LinkedIn's blocking behavior"""
    
    test_urls = [
        "http://www.linkedin.com/company/2150vc",
        "http://www.linkedin.com/company/microsoft",
        "http://www.linkedin.com/company/google"
    ]
    
    print("🔍 LINKEDIN BLOCKING ANALYSIS")
    print("=" * 50)
    
    # Test 1: Single request
    print("\n📋 TEST 1: Single Request")
    print("-" * 30)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    })
    
    try:
        response = session.get(test_urls[0], timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"URL: {response.url}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            if "employees" in soup.get_text().lower():
                print("✅ Employee data found!")
            else:
                print("❌ No employee data found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Multiple requests from same session
    print("\n📋 TEST 2: Multiple Requests (Same Session)")
    print("-" * 45)
    
    for i, url in enumerate(test_urls[:2], 1):
        print(f"\nRequest {i}: {url}")
        try:
            response = session.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 999:
                print("  🚫 BLOCKED! LinkedIn detected automated behavior")
                break
            elif response.status_code == 200:
                print("  ✅ Success")
            else:
                print(f"  ⚠️  Unexpected status: {response.status_code}")
                
            time.sleep(5)  # Short delay
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    # Test 3: Fresh sessions
    print("\n📋 TEST 3: Fresh Sessions for Each Request")
    print("-" * 45)
    
    for i, url in enumerate(test_urls[:2], 1):
        print(f"\nRequest {i}: {url}")
        
        # Create fresh session
        fresh_session = requests.Session()
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0'
        ]
        
        fresh_session.headers.update({
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
        
        try:
            response = fresh_session.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            if response.status_code == 999:
                print("  🚫 BLOCKED! Even fresh sessions are detected")
            elif response.status_code == 200:
                print("  ✅ Success with fresh session")
            else:
                print(f"  ⚠️  Unexpected status: {response.status_code}")
                
            time.sleep(10)  # Longer delay
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 ANALYSIS SUMMARY:")
    print("=" * 50)
    print("• First request usually succeeds")
    print("• Subsequent requests get HTTP 999 (blocked)")
    print("• LinkedIn tracks IP + request patterns")
    print("• Fresh sessions may help but limited")
    print("• Consider: VPN, proxies, or longer delays")
    print("=" * 50)

if __name__ == "__main__":
    test_linkedin_blocking()