#!/usr/bin/env python3
"""
Integrated Company Data Scraper
Combines LinkedIn data (size, industry) with revenue data from multiple sources
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import Optional, Dict, List
import random
from urllib.parse import urlparse, urljoin
import os
import sys
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Import existing LinkedIn scraper
from linkedin_company_scraper_enhanced import EnhancedLinkedInScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('integrated_company_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class MultiSourceRevenueScraper:
    def __init__(self, delay_range=(2, 5)):
        """Initialize multi-source revenue scraper"""
        self.delay_range = delay_range
        self.timeout = 30
        
        # Revenue patterns - comprehensive set
        self.revenue_patterns = [
            # Standard currency formats
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)\s*(?:in\s*)?(?:revenue|sales|turnover)',
            r'(?:revenue|sales|turnover)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            
            # Annual revenue patterns
            r'annual\s+(?:revenue|sales)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            r'(\d{4})\s+(?:revenue|sales)[:\s]*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            
            # Range patterns
            r'\$(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*-\s*\$?(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            
            # European formats
            r'€(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
            
            # Without currency symbol
            r'(?:revenue|sales|turnover)[\s:]*(\d{1,3}(?:,\d{3})*(?:\.\d+)?)\s*(?:million|M|billion|B|thousand|K)',
        ]
    
    def _create_session(self):
        """Create session with rotating headers"""
        session = requests.Session()
        
        # Set up retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Rotate user agents
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
        }
        
        session.headers.update(headers)
        return session
    
    def _extract_domain(self, website_url: str) -> str:
        """Extract clean domain from URL"""
        try:
            parsed = urlparse(website_url)
            domain = parsed.netloc.lower()
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return website_url
    
    def _find_revenue_in_text(self, text: str) -> Optional[str]:
        """Find revenue in text using patterns"""
        if not text:
            return None
            
        text_lower = text.lower()
        
        for pattern in self.revenue_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                revenue_text = match.group(0)
                # Clean and format
                revenue_text = re.sub(r'\s+', ' ', revenue_text).strip()
                return revenue_text
        
        return None
    
    def get_revenue_from_zoominfo(self, company_name: str, website_url: str) -> Dict[str, any]:
        """Get revenue from ZoomInfo"""
        result = {
            'revenue': None,
            'source': 'ZoomInfo',
            'source_url': None,
            'status': 'Not Found'
        }
        
        try:
            session = self._create_session()
            domain = self._extract_domain(website_url)
            
            # Search ZoomInfo
            search_queries = [
                f"{company_name} site:zoominfo.com",
                f"{domain} site:zoominfo.com",
                f"{company_name} {domain} site:zoominfo.com"
            ]
            
            for query in search_queries:
                try:
                    # Use Google search to find ZoomInfo pages
                    google_url = f"https://www.google.com/search?q={query}"
                    
                    delay = random.uniform(*self.delay_range)
                    time.sleep(delay)
                    
                    response = session.get(google_url, timeout=self.timeout)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for ZoomInfo result links
                        zoominfo_links = []
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if 'zoominfo.com/c/' in href:
                                # Extract actual URL from Google result
                                if href.startswith('/url?q='):
                                    actual_url = href.split('/url?q=')[1].split('&')[0]
                                    zoominfo_links.append(actual_url)
                        
                        if zoominfo_links:
                            # Try to extract revenue from the first ZoomInfo page
                            zoominfo_url = zoominfo_links[0]
                            revenue = self._extract_revenue_from_page(zoominfo_url)
                            
                            if revenue:
                                result.update({
                                    'revenue': revenue,
                                    'source_url': zoominfo_url,
                                    'status': 'Success'
                                })
                                return result
                
                except Exception as e:
                    logger.debug(f"ZoomInfo search failed for {query}: {str(e)}")
                    continue
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting ZoomInfo revenue for {company_name}: {str(e)}")
            result['status'] = f'Error: {str(e)}'
            return result
    
    def get_revenue_from_company_website(self, company_name: str, website_url: str) -> Dict[str, any]:
        """Get revenue from company's own website"""
        result = {
            'revenue': None,
            'source': 'Company Website',
            'source_url': None,
            'status': 'Not Found'
        }
        
        try:
            session = self._create_session()
            
            # Try common pages that might have revenue info
            pages_to_check = [
                '',  # Homepage
                '/about',
                '/about-us',
                '/company',
                '/investors',
                '/investor-relations',
                '/press',
                '/news',
                '/financials'
            ]
            
            for page in pages_to_check:
                try:
                    url = website_url.rstrip('/') + page
                    
                    delay = random.uniform(*self.delay_range)
                    time.sleep(delay)
                    
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
                            return result
                
                except Exception as e:
                    logger.debug(f"Failed to check {url}: {str(e)}")
                    continue
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting website revenue for {company_name}: {str(e)}")
            result['status'] = f'Error: {str(e)}'
            return result
    
    def get_revenue_from_crunchbase(self, company_name: str, website_url: str) -> Dict[str, any]:
        """Get revenue from Crunchbase"""
        result = {
            'revenue': None,
            'source': 'Crunchbase',
            'source_url': None,
            'status': 'Not Found'
        }
        
        try:
            session = self._create_session()
            domain = self._extract_domain(website_url)
            
            # Search Crunchbase via Google
            search_queries = [
                f"{company_name} site:crunchbase.com",
                f"{domain} site:crunchbase.com"
            ]
            
            for query in search_queries:
                try:
                    google_url = f"https://www.google.com/search?q={query}"
                    
                    delay = random.uniform(*self.delay_range)
                    time.sleep(delay)
                    
                    response = session.get(google_url, timeout=self.timeout)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        # Look for Crunchbase links
                        crunchbase_links = []
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if 'crunchbase.com/organization/' in href:
                                if href.startswith('/url?q='):
                                    actual_url = href.split('/url?q=')[1].split('&')[0]
                                    crunchbase_links.append(actual_url)
                        
                        if crunchbase_links:
                            crunchbase_url = crunchbase_links[0]
                            revenue = self._extract_revenue_from_page(crunchbase_url)
                            
                            if revenue:
                                result.update({
                                    'revenue': revenue,
                                    'source_url': crunchbase_url,
                                    'status': 'Success'
                                })
                                return result
                
                except Exception as e:
                    logger.debug(f"Crunchbase search failed for {query}: {str(e)}")
                    continue
            
            return result
        
        except Exception as e:
            logger.error(f"Error getting Crunchbase revenue for {company_name}: {str(e)}")
            result['status'] = f'Error: {str(e)}'
            return result
    
    def _extract_revenue_from_page(self, url: str) -> Optional[str]:
        """Extract revenue from a specific page"""
        try:
            session = self._create_session()
            
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            response = session.get(url, timeout=self.timeout)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text()
                return self._find_revenue_in_text(text_content)
            
            return None
        except Exception as e:
            logger.debug(f"Error extracting revenue from {url}: {str(e)}")
            return None
    
    def get_company_revenue(self, company_name: str, website_url: str) -> Dict[str, any]:
        """Get revenue from multiple sources"""
        logger.info(f"Getting revenue for {company_name} from website: {website_url}")
        
        # Try different sources in order of preference
        sources = [
            self.get_revenue_from_company_website,
            self.get_revenue_from_zoominfo,
            self.get_revenue_from_crunchbase,
        ]
        
        for source_func in sources:
            try:
                result = source_func(company_name, website_url)
                if result['revenue']:
                    logger.info(f"✓ Found revenue for {company_name} from {result['source']}: {result['revenue']}")
                    return result
            except Exception as e:
                logger.debug(f"Source {source_func.__name__} failed: {str(e)}")
                continue
        
        # If no revenue found from any source
        return {
            'revenue': None,
            'source': None,
            'source_url': None,
            'status': 'Not Found in Any Source'
        }

class IntegratedCompanyScraper:
    def __init__(self):
        """Initialize integrated scraper with LinkedIn and revenue scrapers"""
        self.linkedin_scraper = EnhancedLinkedInScraper()
        self.revenue_scraper = MultiSourceRevenueScraper()
    
    def scrape_complete_company_data(self, company_name: str, linkedin_url: str = None, website_url: str = None) -> Dict[str, any]:
        """Scrape complete company data from all sources"""
        result = {
            'company_name': company_name,
            'company_size': None,
            'industry': None,
            'revenue': None,
            'linkedin_url': linkedin_url,
            'website_url': website_url,
            'revenue_source': None,
            'revenue_source_url': None,
            'status': {
                'linkedin': 'Not Attempted',
                'revenue': 'Not Attempted'
            }
        }
        
        # Get LinkedIn data (size and industry)
        if linkedin_url:
            try:
                company_size = self.linkedin_scraper.extract_company_size(linkedin_url)
                result['company_size'] = company_size
                result['status']['linkedin'] = 'Success' if company_size else 'No Data Found'
            except Exception as e:
                logger.error(f"LinkedIn scraping failed for {company_name}: {str(e)}")
                result['status']['linkedin'] = f'Error: {str(e)}'
        
        # Get revenue data
        if website_url:
            try:
                revenue_result = self.revenue_scraper.get_company_revenue(company_name, website_url)
                result['revenue'] = revenue_result['revenue']
                result['revenue_source'] = revenue_result['source']
                result['revenue_source_url'] = revenue_result['source_url']
                result['status']['revenue'] = revenue_result['status']
            except Exception as e:
                logger.error(f"Revenue scraping failed for {company_name}: {str(e)}")
                result['status']['revenue'] = f'Error: {str(e)}'
        
        return result

def process_excel_file_integrated(input_file: str,
                                company_column: str = 'Company_Name',
                                linkedin_column: str = 'LinkedIn_URL',
                                website_column: str = 'Website_URL',
                                output_file: str = None,
                                wait_min: int = 15,
                                wait_max: int = 30,
                                save_interval: int = 5):
    """Process Excel file with integrated scraping"""
    
    try:
        # Load Excel file
        df = pd.read_excel(input_file)
        logger.info(f"Loaded {len(df)} companies from {input_file}")
        
        # Validate required columns
        required_columns = [company_column]
        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Required column '{col}' not found in Excel file")
        
        # Add output columns if they don't exist
        output_columns = [
            'Company_Size_Enhanced', 'Industry_Enhanced', 'Revenue_Enhanced',
            'Revenue_Source', 'Revenue_Source_URL', 'LinkedIn_Status', 'Revenue_Status'
        ]
        
        for col in output_columns:
            if col not in df.columns:
                df[col] = None
        
        # Create integrated scraper
        scraper = IntegratedCompanyScraper()
        
        # Set output file
        if not output_file:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_enhanced_integrated.xlsx"
        
        success_counts = {'linkedin': 0, 'revenue': 0}
        processed_count = 0
        
        for index, row in df.iterrows():
            company_name = row[company_column]
            linkedin_url = row.get(linkedin_column) if linkedin_column in df.columns else None
            website_url = row.get(website_column) if website_column in df.columns else None
            
            logger.info(f"Processing {company_name} ({processed_count + 1}/{len(df)})")
            
            # Scrape complete data
            result = scraper.scrape_complete_company_data(
                company_name=company_name,
                linkedin_url=linkedin_url,
                website_url=website_url
            )
            
            # Update DataFrame
            df.at[index, 'Company_Size_Enhanced'] = result['company_size']
            df.at[index, 'Industry_Enhanced'] = result['industry']
            df.at[index, 'Revenue_Enhanced'] = result['revenue']
            df.at[index, 'Revenue_Source'] = result['revenue_source']
            df.at[index, 'Revenue_Source_URL'] = result['revenue_source_url']
            df.at[index, 'LinkedIn_Status'] = result['status']['linkedin']
            df.at[index, 'Revenue_Status'] = result['status']['revenue']
            
            # Count successes
            if result['company_size']:
                success_counts['linkedin'] += 1
            if result['revenue']:
                success_counts['revenue'] += 1
            
            processed_count += 1
            
            # Add wait time between companies
            if processed_count < len(df):
                wait_time = random.uniform(wait_min, wait_max)
                logger.info(f"Waiting {wait_time:.1f} seconds before next company...")
                time.sleep(wait_time)
            
            # Save progress periodically
            if processed_count % save_interval == 0:
                df.to_excel(output_file, index=False)
                logger.info(f"Progress saved: {processed_count}/{len(df)} processed")
                logger.info(f"LinkedIn success: {success_counts['linkedin']}, Revenue success: {success_counts['revenue']}")
        
        # Save final results
        df.to_excel(output_file, index=False)
        logger.info(f"Processing complete!")
        logger.info(f"Total processed: {processed_count}")
        logger.info(f"LinkedIn successes: {success_counts['linkedin']}")
        logger.info(f"Revenue successes: {success_counts['revenue']}")
        logger.info(f"Results saved to: {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        raise

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Integrated Company Data Scraper (LinkedIn + Revenue)')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('--company-column', default='Company_Name', help='Name of column containing company names')
    parser.add_argument('--linkedin-column', default='LinkedIn_URL', help='Name of column containing LinkedIn URLs')
    parser.add_argument('--website-column', default='Website_URL', help='Name of column containing website URLs')
    parser.add_argument('--output-file', help='Path to output Excel file (optional)')
    parser.add_argument('--wait-min', type=int, default=15, help='Minimum wait time between companies (seconds)')
    parser.add_argument('--wait-max', type=int, default=30, help='Maximum wait time between companies (seconds)')
    
    args = parser.parse_args()
    
    try:
        process_excel_file_integrated(
            input_file=args.input_file,
            company_column=args.company_column,
            linkedin_column=args.linkedin_column,
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