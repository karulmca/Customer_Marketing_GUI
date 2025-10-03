#!/usr/bin/env python3
"""
Manual ZoomInfo URL Tester - for testing specific ZoomInfo URLs
"""

from zoominfo_revenue_scraper import ZoomInfoRevenueScraper

def test_specific_zoominfo_urls():
    """Test specific ZoomInfo URLs to see if revenue extraction works"""
    scraper = ZoomInfoRevenueScraper()
    
    # Test URLs - you can add more here
    test_urls = [
        "https://www.zoominfo.com/c/all-india-management-association/350854624",
        "https://www.zoominfo.com/c/microsoft-corporation/5113866",
        "https://www.zoominfo.com/c/salesforce-inc/118373266"
    ]
    
    print("Testing specific ZoomInfo URLs for revenue extraction...")
    print("=" * 60)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\nTest {i}: {url}")
        print("-" * 50)
        
        try:
            revenue = scraper._extract_revenue_from_zoominfo_page(url)
            if revenue:
                print(f"✓ Revenue found: {revenue}")
            else:
                print("✗ No revenue found")
        except Exception as e:
            print(f"✗ Error: {str(e)}")

def test_with_manual_zoominfo_urls():
    """Test the scraper by manually providing ZoomInfo URLs"""
    
    # Manual mapping of companies to their ZoomInfo URLs
    # You can find these by manually searching Google for "company_name site:zoominfo.com"
    company_zoominfo_mapping = {
        "AIMA - The Alternative Investment Management Association": "https://www.zoominfo.com/c/all-india-management-association/350854624",
        # Add more mappings here as you find them
    }
    
    scraper = ZoomInfoRevenueScraper()
    
    print("Testing with manually provided ZoomInfo URLs...")
    print("=" * 60)
    
    for company_name, zoominfo_url in company_zoominfo_mapping.items():
        print(f"\nCompany: {company_name}")
        print(f"ZoomInfo URL: {zoominfo_url}")
        print("-" * 50)
        
        try:
            revenue = scraper._extract_revenue_from_zoominfo_page(zoominfo_url)
            if revenue:
                print(f"✓ Revenue found: {revenue}")
            else:
                print("✗ No revenue found")
        except Exception as e:
            print(f"✗ Error: {str(e)}")

if __name__ == "__main__":
    print("Manual ZoomInfo Testing")
    print("=" * 30)
    
    # Test 1: Specific URLs
    test_specific_zoominfo_urls()
    
    print("\n" + "=" * 60)
    
    # Test 2: Manual mappings
    test_with_manual_zoominfo_urls()
    
    print("\n" + "=" * 60)
    print("MANUAL APPROACH:")
    print("If the automatic Google search isn't finding ZoomInfo pages,")
    print("you can manually search Google for each company:")
    print('1. Search: "company_name site:zoominfo.com"')
    print("2. Copy the ZoomInfo URL from the results")
    print("3. Add it to the company_zoominfo_mapping dictionary above")
    print("4. Run this test again")