#!/usr/bin/env python3
"""
Hybrid ZoomInfo Revenue Scraper
Combines automatic search with manual URL mapping for better results
"""

import pandas as pd
from zoominfo_revenue_scraper import ZoomInfoRevenueScraper
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Manual ZoomInfo URL mappings (add URLs as you find them)
MANUAL_ZOOMINFO_URLS = {
    "AIMA - The Alternative Investment Management Association": "https://www.zoominfo.com/c/all-india-management-association/350854624",
    "aima.org": "https://www.zoominfo.com/c/all-india-management-association/350854624",
    # Add more mappings here in the format:
    # "Company Name": "ZoomInfo URL",
    # "domain.com": "ZoomInfo URL",
}

class HybridZoomInfoScraper(ZoomInfoRevenueScraper):
    def __init__(self, manual_urls=None):
        super().__init__()
        self.manual_urls = manual_urls or MANUAL_ZOOMINFO_URLS
    
    def get_revenue_from_zoominfo(self, company_name: str, website_url: str):
        """Enhanced ZoomInfo scraper with manual URL fallback"""
        
        # First, check if we have a manual mapping
        domain = self._extract_domain(website_url)
        
        manual_url = None
        if company_name in self.manual_urls:
            manual_url = self.manual_urls[company_name]
            logger.info(f"Using manual ZoomInfo URL for {company_name}")
        elif domain in self.manual_urls:
            manual_url = self.manual_urls[domain]
            logger.info(f"Using manual ZoomInfo URL for domain {domain}")
        
        if manual_url:
            # Use manual URL directly
            revenue = self._extract_revenue_from_zoominfo_page(manual_url)
            if revenue:
                return {
                    'revenue': revenue,
                    'source': 'ZoomInfo',
                    'source_url': manual_url,
                    'status': 'Success (Manual URL)'
                }
            else:
                return {
                    'revenue': None,
                    'source': 'ZoomInfo',
                    'source_url': manual_url,
                    'status': 'Manual URL found but no revenue extracted'
                }
        
        # Fallback to automatic search
        logger.info(f"No manual URL found, trying automatic search for {company_name}")
        return super().get_revenue_from_zoominfo(company_name, website_url)

def process_test5_with_hybrid_scraper():
    """Process Test5.xlsx with the hybrid scraper"""
    
    # Read the data
    df = pd.read_excel('Test5.xlsx')
    
    # Initialize hybrid scraper
    scraper = HybridZoomInfoScraper()
    
    # Add new columns
    df['Revenue_ZoomInfo'] = None
    df['ZoomInfo_Source_URL'] = None
    df['ZoomInfo_Status'] = None
    
    print("Processing Test5.xlsx with Hybrid ZoomInfo Scraper")
    print("=" * 55)
    
    for index, row in df.iterrows():
        company_name = row['Company Name']
        website_url = row['Website']
        
        print(f"\nProcessing: {company_name}")
        print(f"Website: {website_url}")
        
        # Get revenue
        result = scraper.get_revenue_from_zoominfo(company_name, website_url)
        
        # Update dataframe
        df.at[index, 'Revenue_ZoomInfo'] = result['revenue']
        df.at[index, 'ZoomInfo_Source_URL'] = result['source_url']
        df.at[index, 'ZoomInfo_Status'] = result['status']
        
        print(f"Status: {result['status']}")
        if result['revenue']:
            print(f"Revenue: {result['revenue']}")
        print("-" * 40)
    
    # Save results
    output_file = 'Test5_hybrid_zoominfo_results.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\nResults saved to: {output_file}")
    return df

if __name__ == "__main__":
    process_test5_with_hybrid_scraper()