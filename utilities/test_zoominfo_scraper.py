#!/usr/bin/env python3
"""
Test script for ZoomInfo Revenue Scraper
"""

import pandas as pd
import os
from zoominfo_revenue_scraper import ZoomInfoRevenueScraper
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_company():
    """Test the scraper with a single company"""
    scraper = ZoomInfoRevenueScraper()
    
    # Test companies - you can modify these
    test_companies = [
        {
            'company_name': 'Microsoft',
            'website_url': 'https://www.microsoft.com'
        },
        {
            'company_name': 'Salesforce',
            'website_url': 'https://www.salesforce.com'
        },
        {
            'company_name': 'Adobe',
            'website_url': 'https://www.adobe.com'
        }
    ]
    
    print("Testing ZoomInfo Revenue Scraper with sample companies...")
    print("=" * 60)
    
    for i, company in enumerate(test_companies, 1):
        print(f"\nTest {i}: {company['company_name']}")
        print(f"Website: {company['website_url']}")
        print("-" * 40)
        
        result = scraper.get_revenue_from_zoominfo(
            company['company_name'], 
            company['website_url']
        )
        
        print(f"Status: {result['status']}")
        if result['revenue']:
            print(f"Revenue: {result['revenue']}")
            print(f"Source URL: {result['source_url']}")
        else:
            print("No revenue found")
        
        # Wait between tests
        if i < len(test_companies):
            print("Waiting 10 seconds before next test...")
            time.sleep(10)

def create_test_excel():
    """Create a test Excel file with sample companies"""
    test_data = [
        {
            'Company_Name': 'Microsoft Corporation',
            'Website_URL': 'https://www.microsoft.com'
        },
        {
            'Company_Name': 'Salesforce',
            'Website_URL': 'https://www.salesforce.com'
        },
        {
            'Company_Name': 'Adobe Inc.',
            'Website_URL': 'https://www.adobe.com'
        },
        {
            'Company_Name': 'ServiceNow',
            'Website_URL': 'https://www.servicenow.com'
        },
        {
            'Company_Name': 'Zoom Video Communications',
            'Website_URL': 'https://zoom.us'
        }
    ]
    
    df = pd.DataFrame(test_data)
    test_file = 'test_zoominfo_companies.xlsx'
    df.to_excel(test_file, index=False)
    
    print(f"Created test Excel file: {test_file}")
    print("You can now run the scraper with:")
    print(f"python zoominfo_revenue_scraper.py {test_file}")
    print("or")
    print(f"run_zoominfo_revenue_scraper.bat {test_file}")
    
    return test_file

def main():
    """Main test function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test ZoomInfo Revenue Scraper')
    parser.add_argument('--create-test-file', action='store_true', 
                       help='Create a test Excel file with sample companies')
    parser.add_argument('--test-single', action='store_true',
                       help='Test with single companies interactively')
    
    args = parser.parse_args()
    
    if args.create_test_file:
        create_test_excel()
    elif args.test_single:
        test_single_company()
    else:
        print("ZoomInfo Revenue Scraper Test Options:")
        print("=" * 40)
        print("1. Create test Excel file: python test_zoominfo_scraper.py --create-test-file")
        print("2. Test single companies: python test_zoominfo_scraper.py --test-single")
        print()
        print("Or run both:")
        create_test_excel()
        print()
        test_single_company()

if __name__ == '__main__':
    main()