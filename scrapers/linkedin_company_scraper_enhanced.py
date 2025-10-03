#!/usr/bin/env python3
"""
Enhanced LinkedIn Company Size Scraper with better error handling
and alternative data sources
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import Optional, List, Dict
import random
from urllib.parse import urlparse
import os
import sys
import json
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

def load_config(config_file='config.json'):
    """Load configuration from JSON file"""
    try:
        with open(config_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Config file {config_file} not found, using defaults")
        return {}
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in config file {config_file}, using defaults")
        return {}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class EnhancedLinkedInScraper:
    def __init__(self, config=None):
        """Enhanced scraper with better session management and anti-detection"""
        self.config = config or load_config()
        scraper_settings = self.config.get('scraper_settings', {})
        
        self.delay_range = tuple(scraper_settings.get('delay_range', [10, 20]))
        self.timeout = scraper_settings.get('timeout', 30)
        self.max_retries = scraper_settings.get('max_retries', 3)
        
        # Don't create a persistent session - create fresh ones for each request
        self.session = None
        
        # Rotate user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59'
        ]
        
        self.current_user_agent = random.choice(self.user_agents)
        
    def _create_fresh_session(self):
        """Create a fresh session for each request to avoid detection"""
        # Create new session
        session = requests.Session()
        
        # Setup retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Rotate user agent for each request
        user_agent = random.choice(self.user_agents)
        
        # Add realistic headers with randomization
        referrers = [
            'https://www.google.com/',
            'https://www.bing.com/',
            'https://duckduckgo.com/',
            'https://linkedin.com/',
            ''  # Sometimes no referrer
        ]
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
        }
        
        # Add referrer sometimes
        if random.random() < 0.7:  # 70% chance to have referrer
            headers['Referer'] = random.choice(referrers)
            
        session.headers.update(headers)
        
        return session
    
    def extract_company_size(self, linkedin_url: str) -> Optional[str]:
        """Extract company size with enhanced error handling"""
        try:
            logger.info(f"Attempting to scrape: {linkedin_url}")
            
            # Validate URL
            if not self._is_valid_linkedin_url(linkedin_url):
                logger.warning(f"Invalid LinkedIn URL: {linkedin_url}")
                return "Invalid URL"
            
            # Random delay 
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            # Create fresh session for each request to avoid detection
            session = self._create_fresh_session()
            
            # Make request with fresh session
            response = session.get(linkedin_url, timeout=self.timeout)
            
            # Check for common blocking responses
            if response.status_code == 999:
                logger.warning(f"LinkedIn blocked request (999): {linkedin_url}")
                return "Blocked by LinkedIn"
            elif response.status_code == 429:
                logger.warning(f"Rate limited (429): {linkedin_url}")
                return "Rate Limited"
            elif response.status_code != 200:
                logger.warning(f"HTTP {response.status_code}: {linkedin_url}")
                return f"HTTP Error {response.status_code}"
            
            # Check if we got a login page (common when blocked)
            if "authwall" in response.url or "login" in response.url:
                logger.warning(f"Redirected to login page: {linkedin_url}")
                return "Login Required"
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try multiple extraction strategies
            company_size = self._extract_size_multiple_strategies(soup)
            
            if company_size:
                logger.info(f"Successfully extracted: {company_size}")
                return company_size
            else:
                # Try alternative approaches
                alt_size = self._try_alternative_extraction(soup, linkedin_url)
                if alt_size:
                    logger.info(f"Alternative extraction successful: {alt_size}")
                    return alt_size
                
                logger.warning(f"No company size found: {linkedin_url}")
                return "Not Found"
                
        except requests.exceptions.Timeout:
            logger.error(f"Request timeout: {linkedin_url}")
            return "Timeout"
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error: {linkedin_url}")
            return "Connection Error"
        except Exception as e:
            logger.error(f"Unexpected error for {linkedin_url}: {str(e)}")
            return "Error"
    
    def _is_valid_linkedin_url(self, url: str) -> bool:
        """Validate LinkedIn company URL"""
        try:
            parsed = urlparse(url)
            return (
                parsed.netloc.lower() in ['linkedin.com', 'www.linkedin.com'] and
                '/company/' in parsed.path.lower()
            )
        except:
            return False
    
    def _extract_size_multiple_strategies(self, soup: BeautifulSoup) -> Optional[str]:
        """Try multiple extraction strategies"""
        strategies = [
            self._strategy_meta_tags,
            self._strategy_json_ld,
            self._strategy_text_patterns,
            self._strategy_css_selectors,
            self._strategy_about_section
        ]
        
        for strategy in strategies:
            try:
                result = strategy(soup)
                if result:
                    return result
            except Exception as e:
                logger.debug(f"Strategy {strategy.__name__} failed: {str(e)}")
                continue
        
        return None
    
    def _strategy_meta_tags(self, soup: BeautifulSoup) -> Optional[str]:
        """Look for company size in meta tags"""
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            content = tag.get('content', '')
            if content and self._contains_employee_info(content):
                return self._extract_employee_count(content)
        return None
    
    def _strategy_json_ld(self, soup: BeautifulSoup) -> Optional[str]:
        """Look for JSON-LD structured data"""
        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string or '')
                if isinstance(data, dict):
                    # Look for numberOfEmployees or similar fields
                    employees = data.get('numberOfEmployees')
                    if employees:
                        return f"{employees} employees"
            except:
                continue
        return None
    
    def _strategy_text_patterns(self, soup: BeautifulSoup) -> Optional[str]:
        """Look for text patterns indicating company size"""
        text_content = soup.get_text()
        
        # Enhanced patterns - prioritize LinkedIn's exact format from screenshot
        patterns = [
            # EXACT LinkedIn format: "11-50 employees"
            r'(\d{1,3}-\d{1,4}\s+employees?)',
            r'(\d{1,3}-\d{1,4}\s*employees?)',
            
            # LinkedIn's standard ranges
            r'((?:1-10|11-50|51-200|201-500|501-1000|1001-5000|5001-10000|10001\+)\s*employees?)',
            
            # General patterns
            r'(\d{1,3}(?:,\d{3})*\+?\s*(?:-\s*\d{1,3}(?:,\d{3})*\+?)?\s*employees?)',
            r'(Company size[:\s]*\d{1,3}(?:,\d{3})*\+?(?:\s*-\s*\d{1,3}(?:,\d{3})*\+?)?\s*employees?)',
            r'(Team size[:\s]*\d{1,3}(?:,\d{3})*\+?(?:\s*-\s*\d{1,3}(?:,\d{3})*\+?)?\s*employees?)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                return match.group(1).strip()
        
        return None
    
    def _strategy_css_selectors(self, soup: BeautifulSoup) -> Optional[str]:
        """Look using CSS selectors"""
        selectors = [
            '[data-test-id*="company-size"]',
            '[class*="company-size"]',
            '[class*="org-top-card"]',
            '.org-about-company-module__company-size',
            '.company-info-list__item',
            '.org-top-card-summary-info-list__info-item'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if self._contains_employee_info(text):
                    return self._extract_employee_count(text)
        
        return None
    
    def _strategy_about_section(self, soup: BeautifulSoup) -> Optional[str]:
        """Look specifically in about sections"""
        about_sections = soup.find_all(['section', 'div'], string=re.compile(r'about', re.IGNORECASE))
        
        for section in about_sections:
            parent = section.parent if section.parent else section
            text = parent.get_text()
            
            if self._contains_employee_info(text):
                return self._extract_employee_count(text)
        
        return None
    
    def _try_alternative_extraction(self, soup: BeautifulSoup, url: str) -> Optional[str]:
        """Try alternative extraction methods"""
        # Look for any numbers that might represent company size
        all_text = soup.get_text()
        
        # Common size ranges
        size_ranges = [
            "1-10", "11-50", "51-200", "201-500", "501-1000", 
            "1001-5000", "5001-10000", "10001+"
        ]
        
        for size_range in size_ranges:
            if size_range in all_text:
                return f"{size_range} employees"
        
        # Look for specific keywords near numbers
        lines = all_text.split('\n')
        for line in lines:
            line = line.strip().lower()
            if any(keyword in line for keyword in ['employee', 'staff', 'team', 'workforce']):
                numbers = re.findall(r'\d{1,3}(?:,\d{3})*', line)
                if numbers:
                    return f"{numbers[0]} employees (estimated)"
        
        return None
    
    def _contains_employee_info(self, text: str) -> bool:
        """Check if text contains employee information"""
        text_lower = text.lower()
        keywords = ['employee', 'employees', 'staff', 'team size', 'workforce', 'company size']
        return any(keyword in text_lower for keyword in keywords) and any(char.isdigit() for char in text)
    
    def _extract_employee_count(self, text: str) -> Optional[str]:
        """Extract employee count from text"""
        # Look for patterns like "1,000 employees", "51-200 employees", etc.
        patterns = [
            r'(\d{1,3}(?:,\d{3})*\+?)\s*(?:-\s*(\d{1,3}(?:,\d{3})*\+?))?\s*employees?',
            r'((?:1-10|11-50|51-200|201-500|501-1000|1001-5000|5001-10000|10001\+))\s*employees?'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group().strip()
        
        return None

def process_excel_file_enhanced(input_file: str, url_column: str, size_column: str, output_file: str = None, wait_min: int = 15, wait_max: int = 30):
    """Enhanced Excel processing with better error handling"""
    if output_file is None:
        output_file = input_file
    
    logger.info(f"Processing Excel file: {input_file}")
    
    try:
        # Read Excel file
        df = pd.read_excel(input_file)
        logger.info(f"Loaded {len(df)} rows from Excel file")
        
        # Validate columns exist
        if url_column not in df.columns:
            raise ValueError(f"Column '{url_column}' not found in Excel file")
        
        # Add size column if it doesn't exist
        if size_column not in df.columns:
            df[size_column] = ''
        
        # Ensure the size column is of string type
        df[size_column] = df[size_column].astype(str).replace('nan', '')
        
        # Initialize scraper
        config = load_config()
        scraper = EnhancedLinkedInScraper(config)
        
        # Get save interval from config
        save_interval = config.get('excel_settings', {}).get('save_progress_interval', 5)
        
        # Process each row
        processed_count = 0
        success_count = 0
        
        for index, row in df.iterrows():
            linkedin_url = row[url_column]
            
            # Skip if URL is empty or size already exists
            if pd.isna(linkedin_url) or linkedin_url.strip() == '':
                logger.info(f"Row {index + 1}: Skipping empty URL")
                continue
            
            current_size = str(row[size_column]).strip()
            if current_size and current_size not in ['', 'nan', 'None']:
                logger.info(f"Row {index + 1}: Company size already exists ({current_size}), skipping")
                continue
            
            # Extract company size
            company_size = scraper.extract_company_size(linkedin_url.strip())
            
            if company_size and company_size not in ['Not Found', 'Error', 'Timeout', 'Connection Error']:
                df.at[index, size_column] = company_size
                success_count += 1
                logger.info(f"Row {index + 1}: Successfully updated - {company_size}")
            else:
                df.at[index, size_column] = company_size or 'Not Found'
                logger.warning(f"Row {index + 1}: Could not extract company size - {company_size}")
            
            processed_count += 1
            
            # Add wait time between companies to avoid rate limiting
            if processed_count < len(df):  # Don't wait after the last company
                wait_time = random.uniform(wait_min, wait_max)  # Random wait between specified range
                logger.info(f"Waiting {wait_time:.1f} seconds before next company...")
                time.sleep(wait_time)
            
            # Save progress periodically
            if processed_count % save_interval == 0:
                df.to_excel(output_file, index=False)
                logger.info(f"Progress saved: {processed_count} rows processed, {success_count} successful")
        
        # Save final results
        df.to_excel(output_file, index=False)
        logger.info(f"Processing complete! Processed: {processed_count}, Success: {success_count}")
        logger.info(f"Results saved to: {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        raise

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced LinkedIn Company Size Scraper')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('--url-column', default='LinkedIn_URL', help='Name of column containing LinkedIn URLs')
    parser.add_argument('--size-column', default='Company_Size', help='Name of column to store company sizes')
    parser.add_argument('--output-file', help='Path to output Excel file (optional)')
    parser.add_argument('--wait-min', type=int, default=15, help='Minimum wait time between companies (seconds)')
    parser.add_argument('--wait-max', type=int, default=30, help='Maximum wait time between companies (seconds)')
    
    args = parser.parse_args()
    
    try:
        process_excel_file_enhanced(
            input_file=args.input_file,
            url_column=args.url_column,
            size_column=args.size_column,
            output_file=args.output_file,
            wait_min=args.wait_min,
            wait_max=args.wait_max
        )
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()