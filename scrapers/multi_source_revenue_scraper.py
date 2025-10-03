#!/usr/bin/env python3
"""
Multi-Source Revenue Scraper
Tries multiple sources: Company websites, Crunchbase, SEC filings, etc.
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import Optional, Dict
import random
from urllib.parse import urlparse, urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiSourceRevenueScraper:
    def __init__(self):
        self.timeout = 30
        self.delay_range = (2, 5)
        
        # Enhanced revenue patterns
        self.revenue_patterns = [
            r'revenue[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'annual revenue[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)\s*(?:in\s*)?(?:revenue|sales)',
            r'(\d{4})\s+revenue[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            r'net sales[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
            r'total revenue[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B)',
        ]
    
    def _create_session(self):
        session = requests.Session()
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        return session
    
    def _find_revenue_in_text(self, text: str) -> Optional[str]:
        if not text:
            return None
        
        text_lower = text.lower()
        for pattern in self.revenue_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                revenue_text = match.group(0)
                return re.sub(r'\s+', ' ', revenue_text).strip()
        return None
    
    def get_revenue_from_company_website(self, company_name: str, website_url: str) -> Dict:
        """Extract revenue from company's own website"""
        result = {
            'revenue': None,
            'source': 'Company Website',
            'source_url': None,
            'status': 'Not Found'
        }
        
        try:
            session = self._create_session()
            
            # Pages to check for revenue information
            pages_to_check = [
                '',  # Homepage
                '/about',
                '/about-us',
                '/company',
                '/investors',
                '/investor-relations',
                '/press',
                '/news',
                '/financials',
                '/financial-information',
                '/annual-report',
                '/sec-filings'
            ]
            
            base_url = website_url.rstrip('/')
            
            for page in pages_to_check:
                try:
                    url = base_url + page
                    
                    time.sleep(random.uniform(*self.delay_range))
                    response = session.get(url, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        text_content = soup.get_text()
                        
                        revenue = self._find_revenue_in_text(text_content)
                        if revenue:
                            result.update({
                                'revenue': revenue,
                                'source_url': url,
                                'status': 'Success'
                            })
                            logger.info(f"Found revenue on {url}: {revenue}")
                            return result
                
                except Exception as e:
                    logger.debug(f"Failed to check {url}: {str(e)}")
                    continue
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting website revenue for {company_name}: {str(e)}")
            result['status'] = f'Error: {str(e)}'
            return result
    
    def get_revenue_from_crunchbase(self, company_name: str) -> Dict:
        """Try to find revenue from Crunchbase"""
        result = {
            'revenue': None,
            'source': 'Crunchbase',
            'source_url': None,
            'status': 'Not Found'
        }
        
        try:
            session = self._create_session()
            
            # Try to find Crunchbase page
            search_query = f'"{company_name}" site:crunchbase.com'
            google_url = f"https://www.google.com/search?q={search_query}"
            
            time.sleep(random.uniform(*self.delay_range))
            response = session.get(google_url, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for Crunchbase links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if 'crunchbase.com/organization/' in href:
                        if href.startswith('/url?q='):
                            actual_url = href.split('/url?q=')[1].split('&')[0]
                        else:
                            actual_url = href
                        
                        # Try to get revenue from Crunchbase page
                        time.sleep(random.uniform(*self.delay_range))
                        cb_response = session.get(actual_url, timeout=self.timeout)
                        
                        if cb_response.status_code == 200:
                            cb_soup = BeautifulSoup(cb_response.content, 'html.parser')
                            cb_text = cb_soup.get_text()
                            
                            revenue = self._find_revenue_in_text(cb_text)
                            if revenue:
                                result.update({
                                    'revenue': revenue,
                                    'source_url': actual_url,
                                    'status': 'Success'
                                })
                                return result
                        break
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting Crunchbase revenue for {company_name}: {str(e)}")
            result['status'] = f'Error: {str(e)}'
            return result
    
    def get_company_revenue(self, company_name: str, website_url: str) -> Dict:
        """Get revenue from multiple sources"""
        logger.info(f"Getting revenue for {company_name}")
        
        # Try different sources in order
        sources = [
            lambda: self.get_revenue_from_company_website(company_name, website_url),
            lambda: self.get_revenue_from_crunchbase(company_name),
        ]
        
        for source_func in sources:
            try:
                result = source_func()
                if result['revenue']:
                    logger.info(f"✓ Found revenue for {company_name} from {result['source']}: {result['revenue']}")
                    return result
            except Exception as e:
                logger.debug(f"Source failed: {str(e)}")
                continue
        
        # No revenue found from any source
        return {
            'revenue': None,
            'source': 'Multiple Sources',
            'source_url': None,
            'status': 'No revenue found from any source'
        }

def process_test5_with_multi_source():
    """Process Test5.xlsx with multi-source revenue scraper"""
    
    df = pd.read_excel('Test5.xlsx')
    scraper = MultiSourceRevenueScraper()
    
    # Add new columns
    df['Revenue_MultiSource'] = None
    df['Revenue_Source'] = None
    df['Revenue_Source_URL'] = None
    df['Revenue_Status'] = None
    
    print("Processing Test5.xlsx with Multi-Source Revenue Scraper")
    print("=" * 60)
    
    for index, row in df.iterrows():
        company_name = row['Company Name']
        website_url = row['Website']
        
        print(f"\nProcessing: {company_name}")
        print(f"Website: {website_url}")
        
        # Get revenue from multiple sources
        result = scraper.get_company_revenue(company_name, website_url)
        
        # Update dataframe
        df.at[index, 'Revenue_MultiSource'] = result['revenue']
        df.at[index, 'Revenue_Source'] = result['source']
        df.at[index, 'Revenue_Source_URL'] = result['source_url']
        df.at[index, 'Revenue_Status'] = result['status']
        
        print(f"Status: {result['status']}")
        if result['revenue']:
            print(f"Revenue: {result['revenue']}")
            print(f"Source: {result['source']}")
        print("-" * 50)
    
    # Save results
    output_file = 'Test5_multi_source_revenue.xlsx'
    df.to_excel(output_file, index=False)
    
    print(f"\nResults saved to: {output_file}")
    return df

if __name__ == "__main__":
    process_test5_with_multi_source()