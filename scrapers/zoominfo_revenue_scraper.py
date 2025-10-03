#!/usr/bin/env python3
"""
ZoomInfo Revenue Scraper
Extracts company revenue data from ZoomInfo based on company website URLs
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import Optional, Dict, List
import random
from urllib.parse import urlparse, quote_plus, unquote
import os
import sys
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('zoominfo_revenue_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ZoomInfoRevenueScraper:
    def __init__(self, delay_range=(3, 7)):
        """Initialize ZoomInfo revenue scraper with enhanced patterns"""
        self.delay_range = delay_range
        self.timeout = 30
        
        # Enhanced revenue patterns - more comprehensive
        self.revenue_patterns = [
            # Standard currency formats with more variations
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K|M\b|B\b)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)\s*(?:in\s*)?(?:revenue|sales|turnover|annual|yearly)',
            r'(?:revenue|sales|turnover|annual revenue|yearly revenue)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            
            # Annual revenue patterns with years
            r'(?:annual|yearly)\s+(?:revenue|sales)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'(\d{4})\s+(?:revenue|sales)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'(?:fiscal year|fy)\s*(\d{4})[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            
            # Range patterns
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:-|to)\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'between\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:and|to)\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            
            # European and other currencies
            r'€(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'£(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            
            # Without currency symbol but with context
            r'(?:revenue|sales|turnover|annual revenue)[\s:]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'(?:generates|generated)\s*(?:approximately|about|over|around)?\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            
            # More specific ZoomInfo patterns
            r'estimated revenue[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'annual sales[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
        ]
    
    def _create_session(self):
        """Create session with rotating headers for better stealth"""
        session = requests.Session()
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504, 999],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Enhanced user agents rotation
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        
        # Enhanced headers with more realistic browser behavior
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Random referrers for more realistic browsing
        referrers = [
            'https://www.google.com/',
            'https://www.bing.com/',
            'https://www.linkedin.com/',
            'https://www.crunchbase.com/',
        ]
        
        if random.random() < 0.7:  # 70% chance to add referrer
            headers['Referer'] = random.choice(referrers)
        
        session.headers.update(headers)
        return session
    
    def _extract_domain(self, website_url: str) -> str:
        """Extract clean domain from URL"""
        try:
            if not website_url.startswith(('http://', 'https://')):
                website_url = 'https://' + website_url
            
            parsed = urlparse(website_url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return website_url.replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]
    
    def _find_revenue_in_text(self, text: str) -> Optional[str]:
        """Find revenue in text using enhanced patterns"""
        if not text:
            return None
            
        # Clean text and normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        text_lower = text.lower()
        
        # Look for revenue patterns
        for pattern in self.revenue_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                revenue_text = match.group(0).strip()
                
                # Skip very small numbers that are likely not revenue
                if any(word in revenue_text.lower() for word in ['thousand', 'k']):
                    # Extract number to check if it's reasonable
                    nums = re.findall(r'\d+(?:,\d{3})*(?:\.\d+)?', revenue_text)
                    if nums and float(nums[0].replace(',', '')) < 100:  # Less than 100K
                        continue
                
                # Clean and format the match
                revenue_text = re.sub(r'\s+', ' ', revenue_text).strip()
                return revenue_text
        
        return None
    
    def _search_zoominfo_direct(self, company_name: str, domain: str) -> List[str]:
        """Direct search on ZoomInfo site"""
        zoominfo_urls = []
        
        try:
            session = self._create_session()
            
            # Try direct ZoomInfo search
            search_url = f"https://www.zoominfo.com/c/{domain.replace('.', '-')}"
            
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            response = session.get(search_url, timeout=self.timeout)
            if response.status_code == 200:
                zoominfo_urls.append(search_url)
                logger.info(f"Found direct ZoomInfo URL: {search_url}")
            
        except Exception as e:
            logger.debug(f"Direct ZoomInfo search failed: {str(e)}")
        
        return zoominfo_urls
    
    def _search_google_for_zoominfo(self, company_name: str, website_url: str) -> List[str]:
        """Search Google for ZoomInfo pages using website URL + zoominfo keyword"""
        zoominfo_urls = []
        
        try:
            session = self._create_session()
            
            # Primary search strategy: website URL + zoominfo (as per requirement)
            # Extract clean domain from website URL
            clean_url = website_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            
            # Search queries in order of preference
            search_queries = [
                f'{clean_url} zoominfo',  # Primary requirement: website + zoominfo
                f'"{clean_url}" zoominfo',
                f'{website_url} zoominfo',
                f'"{company_name}" {clean_url} zoominfo',
                f'"{company_name}" site:zoominfo.com'
            ]
            
            for query in search_queries:
                try:
                    # Encode query properly
                    encoded_query = quote_plus(query)
                    google_url = f"https://www.google.com/search?q={encoded_query}&num=10"
                    
                    logger.info(f"Searching Google: {query}")
                    
                    delay = random.uniform(*self.delay_range)
                    time.sleep(delay)
                    
                    response = session.get(google_url, timeout=self.timeout)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for ZoomInfo result links - find the FIRST one as per requirement
                        # Try multiple ways to find Google search results
                        
                        # Method 1: Standard Google result divs
                        search_results = soup.find_all('div', class_='g')
                        if not search_results:
                            # Method 2: Look for any divs with search result patterns
                            search_results = soup.find_all('div', class_=re.compile(r'result|search'))
                        if not search_results:
                            # Method 3: Find all links and filter for ZoomInfo
                            search_results = [soup]  # Use the whole page
                        
                        for result_container in search_results:
                            # Find all links in this container
                            links = result_container.find_all('a', href=True)
                            for link in links:
                                href = link.get('href', '')
                                
                                # Check if this is a ZoomInfo company profile link
                                if 'zoominfo.com/c/' in href or 'zoominfo.com%2Fc%2F' in href:
                                    actual_url = None
                                    
                                    if href.startswith('/url?q='):
                                        # Extract actual URL from Google redirect
                                        try:
                                            actual_url = href.split('/url?q=')[1].split('&')[0]
                                            actual_url = unquote(actual_url)
                                        except:
                                            continue
                                    elif href.startswith('https://www.zoominfo.com/c/') or href.startswith('http://www.zoominfo.com/c/'):
                                        actual_url = href
                                    elif 'zoominfo.com' in href and '/c/' in href:
                                        # Handle other ZoomInfo URL formats
                                        actual_url = href
                                    
                                    if actual_url and 'zoominfo.com/c/' in actual_url and actual_url not in zoominfo_urls:
                                        logger.info(f"Found ZoomInfo URL: {actual_url}")
                                        zoominfo_urls.append(actual_url)
                                        
                                        # For the primary search (website + zoominfo), take the first result
                                        if query == search_queries[0]:
                                            logger.info(f"Using first ZoomInfo result for primary search")
                                            return [actual_url]  # Return immediately with first result
                        
                        # If we found URLs with primary search, use them
                        if zoominfo_urls and query == search_queries[0]:
                            break
                
                except Exception as e:
                    logger.debug(f"Google search failed for query '{query}': {str(e)}")
                    continue
        
        except Exception as e:
            logger.debug(f"Google search for ZoomInfo failed: {str(e)}")
        
        return zoominfo_urls
    
    def _extract_revenue_from_zoominfo_page(self, url: str) -> Optional[str]:
        """Extract revenue from a ZoomInfo page - enhanced for the specific ZoomInfo format"""
        try:
            session = self._create_session()
            
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            logger.info(f"Accessing ZoomInfo page: {url}")
            response = session.get(url, timeout=self.timeout)
            if response.status_code != 200:
                logger.debug(f"Failed to access ZoomInfo page: {url} (Status: {response.status_code})")
                return None
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Method 1: Look for the exact "Revenue" label followed by the value (as seen in screenshot)
            revenue_labels = soup.find_all(text=re.compile(r'^Revenue\s*$', re.I))
            for label in revenue_labels:
                # Look for the next sibling or parent's next sibling that contains the amount
                parent = label.parent
                if parent:
                    # Check siblings for revenue amount
                    for sibling in parent.find_next_siblings():
                        text = sibling.get_text().strip()
                        if text and ('$' in text or 'million' in text.lower() or 'billion' in text.lower()):
                            logger.info(f"Found revenue near 'Revenue' label: {text}")
                            return text
                    
                    # Check parent's siblings
                    parent_parent = parent.parent
                    if parent_parent:
                        for sibling in parent_parent.find_next_siblings():
                            text = sibling.get_text().strip()
                            if text and ('$' in text or 'million' in text.lower() or 'billion' in text.lower()):
                                logger.info(f"Found revenue near 'Revenue' label: {text}")
                                return text
            
            # Method 2: Look for specific revenue patterns in the page
            text_content = soup.get_text()
            
            # Split into lines and look for revenue information
            lines = text_content.split('\n')
            for i, line in enumerate(lines):
                if 'revenue' in line.lower():
                    # Check current line and next few lines
                    for j in range(max(0, i-2), min(len(lines), i+3)):
                        revenue = self._find_revenue_in_text(lines[j])
                        if revenue:
                            logger.info(f"Found revenue in line {j}: {revenue}")
                            return revenue
            
            # Method 3: General revenue pattern search
            revenue = self._find_revenue_in_text(text_content)
            if revenue:
                logger.info(f"Found revenue in general content: {revenue}")
                return revenue
            
            # Method 4: Look for specific ZoomInfo structure elements
            # ZoomInfo often uses specific classes or div structures
            potential_revenue_elements = soup.find_all(['div', 'span', 'td', 'li'], 
                                                     text=re.compile(r'\$[\d,]+\.?\d*\s*(million|billion|M|B)', re.I))
            
            for element in potential_revenue_elements:
                text = element.get_text().strip()
                logger.info(f"Found potential revenue element: {text}")
                return text
            
            logger.debug(f"No revenue found in ZoomInfo page: {url}")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting revenue from ZoomInfo page {url}: {str(e)}")
            return None
    
    def get_revenue_from_zoominfo(self, company_name: str, website_url: str) -> Dict[str, any]:
        """Get revenue from ZoomInfo with multiple search strategies"""
        result = {
            'revenue': None,
            'source': 'ZoomInfo',
            'source_url': None,
            'status': 'Not Found'
        }
        
        if not company_name or not website_url:
            result['status'] = 'Missing company name or website URL'
            return result
        
        try:
            domain = self._extract_domain(website_url)
            logger.info(f"Searching ZoomInfo for {company_name} (domain: {domain})")
            
            # Strategy 1: Try direct ZoomInfo URL construction
            zoominfo_urls = self._search_zoominfo_direct(company_name, domain)
            
            # Strategy 2: Google search for ZoomInfo pages (primary method as per requirement)
            zoominfo_urls = self._search_google_for_zoominfo(company_name, website_url)
            
            if not zoominfo_urls:
                logger.info(f"No ZoomInfo pages found for {company_name}")
                result['status'] = 'No ZoomInfo pages found'
                return result
            
            # Try to extract revenue from found ZoomInfo pages
            for zoominfo_url in zoominfo_urls[:3]:  # Try up to 3 URLs
                logger.info(f"Checking ZoomInfo page: {zoominfo_url}")
                revenue = self._extract_revenue_from_zoominfo_page(zoominfo_url)
                
                if revenue:
                    result.update({
                        'revenue': revenue,
                        'source_url': zoominfo_url,
                        'status': 'Success'
                    })
                    logger.info(f"✓ Found revenue for {company_name}: {revenue}")
                    return result
            
            result['status'] = 'Revenue not found in ZoomInfo pages'
            return result
        
        except Exception as e:
            logger.error(f"Error getting ZoomInfo revenue for {company_name}: {str(e)}")
            result['status'] = f'Error: {str(e)}'
            return result

def process_excel_file(input_file: str, 
                      company_column: str = 'Company_Name',
                      website_column: str = 'Website_URL',
                      output_file: str = None,
                      wait_min: int = 5,
                      wait_max: int = 10) -> pd.DataFrame:
    """Process Excel file to extract revenue data from ZoomInfo"""
    
    try:
        # Read input file
        logger.info(f"Reading input file: {input_file}")
        df = pd.read_excel(input_file)
        logger.info(f"Found {len(df)} companies to process")
        
        # Validate required columns
        if company_column not in df.columns:
            raise ValueError(f"Required column '{company_column}' not found in Excel file")
        
        if website_column not in df.columns:
            raise ValueError(f"Required column '{website_column}' not found in Excel file")
        
        # Prepare output file name
        if not output_file:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_zoominfo_revenue.xlsx"
        
        # Initialize scraper
        scraper = ZoomInfoRevenueScraper()
        
        # Add new columns for results
        df['Revenue'] = None
        df['Revenue_Source'] = None
        df['Revenue_Source_URL'] = None
        df['Revenue_Status'] = None
        
        # Process each company
        processed_count = 0
        success_count = 0
        
        for index, row in df.iterrows():
            company_name = row.get(company_column)
            website_url = row.get(website_column)
            
            if pd.isna(company_name) or pd.isna(website_url):
                logger.warning(f"Skipping row {index + 1}: Missing company name or website URL")
                df.at[index, 'Revenue_Status'] = 'Missing data'
                continue
            
            logger.info(f"Processing {company_name} ({processed_count + 1}/{len(df)})")
            
            # Get revenue data
            result = scraper.get_revenue_from_zoominfo(str(company_name), str(website_url))
            
            # Update DataFrame
            df.at[index, 'Revenue'] = result['revenue']
            df.at[index, 'Revenue_Source'] = result['source']
            df.at[index, 'Revenue_Source_URL'] = result['source_url']
            df.at[index, 'Revenue_Status'] = result['status']
            
            if result['revenue']:
                success_count += 1
            
            processed_count += 1
            
            # Add wait time between requests
            if processed_count < len(df):
                wait_time = random.uniform(wait_min, wait_max)
                logger.info(f"Waiting {wait_time:.1f} seconds before next company...")
                time.sleep(wait_time)
            
            # Save progress periodically
            if processed_count % 5 == 0:
                df.to_excel(output_file, index=False)
                logger.info(f"Progress saved: {processed_count}/{len(df)} processed, {success_count} successful")
        
        # Save final results
        df.to_excel(output_file, index=False)
        logger.info(f"Processing complete!")
        logger.info(f"Total processed: {processed_count}")
        logger.info(f"Successful revenue extractions: {success_count}")
        logger.info(f"Success rate: {(success_count/processed_count)*100:.1f}%")
        logger.info(f"Results saved to: {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        raise

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ZoomInfo Revenue Scraper')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('--company-column', default='Company_Name', help='Name of column containing company names')
    parser.add_argument('--website-column', default='Website_URL', help='Name of column containing website URLs')
    parser.add_argument('--output-file', help='Path to output Excel file (optional)')
    parser.add_argument('--wait-min', type=int, default=5, help='Minimum wait time between requests (seconds)')
    parser.add_argument('--wait-max', type=int, default=10, help='Maximum wait time between requests (seconds)')
    
    args = parser.parse_args()
    
    try:
        process_excel_file(
            input_file=args.input_file,
            company_column=args.company_column,
            website_column=args.website_column,
            output_file=args.output_file,
            wait_min=args.wait_min,
            wait_max=args.wait_max
        )
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
