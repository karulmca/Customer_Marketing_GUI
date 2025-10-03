#!/usr/bin/env python3
"""
LinkedIn Company Size Scraper with Maximum Anti-Detection
Each company gets a completely fresh scraper instance
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
import random
from typing import Optional
import sys
import os
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_scraper_stealth.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class StealthLinkedInScraper:
    def __init__(self):
        """Create a completely fresh scraper instance"""
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/118.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        ]
        
    def _create_session(self):
        """Create a completely fresh session"""
        session = requests.Session()
        
        # Random user agent
        user_agent = random.choice(self.user_agents)
        
        # Random referrers
        referrers = [
            'https://www.google.com/search?q=linkedin+company',
            'https://www.bing.com/search?q=company+linkedin',
            'https://duckduckgo.com/?q=linkedin',
            'https://linkedin.com/',
            'https://www.linkedin.com/feed/',
            ''
        ]
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # Add referrer sometimes
        if random.random() < 0.8:
            headers['Referer'] = random.choice(referrers)
            
        session.headers.update(headers)
        return session
    
    def extract_company_size(self, linkedin_url: str) -> Optional[str]:
        """Extract company size with maximum stealth"""
        try:
            # Pre-request delay
            pre_delay = random.uniform(2, 8)
            time.sleep(pre_delay)
            
            # Create fresh session
            session = self._create_session()
            
            # Make request
            response = session.get(linkedin_url, timeout=30)
            
            # Check response
            if response.status_code == 999:
                logger.warning(f"LinkedIn blocked request (999): {linkedin_url}")
                return "Blocked by LinkedIn"
            elif response.status_code != 200:
                logger.warning(f"HTTP {response.status_code}: {linkedin_url}")
                return f"HTTP Error {response.status_code}"
            
            # Parse content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Enhanced patterns for company size - PRIORITIZE LINKEDIN RANGE FORMAT
            patterns = [
                # LinkedIn's standard range categories (HIGHEST PRIORITY)
                r'(1-10|11-50|51-200|201-500|501-1,000|1,001-5,000|5,001-10,000|10,001\+)\s+employees?',
                r'(1-10|11-50|51-200|201-500|501-1000|1001-5000|5001-10000|10000\+)\s+employees?',
                
                # General range patterns
                r'(\d+(?:,\d+)?-\d+(?:,\d+)?)\s+employees?',
                r'(\d+-\d+)\s+employees?',
                r'(\d+\+)\s+employees?',
                
                # Company size section specific
                r'Company size[:\s]*(\d+(?:,\d+)?-\d+(?:,\d+)?)\s+employees?',
                r'Company size[:\s]*(1-10|11-50|51-200|201-500|501-1000|1001-5000|5001-10000|10000\+)\s+employees?',
                
                # Fallback patterns (lower priority)
                r'(\d+(?:,\d+)?)\s+employees?',
                r'(\d+(?:,\d+)?)\s+associates?',
                r'Employees?[:\s]*(\d+(?:,\d+)?)',
                
                # Special cases
                r'(Self-employed)',
                r'(Sole proprietorship)',
            ]
            
            text_content = soup.get_text()
            
            for pattern in patterns:
                matches = re.findall(pattern, text_content, re.IGNORECASE)
                if matches:
                    size = matches[0].strip()
                    # Clean up the size
                    if 'employees' not in size.lower():
                        size = f"{size} employees"
                    logger.info(f"Successfully extracted: {size}")
                    return size
            
            logger.warning(f"No company size found: {linkedin_url}")
            return "Not Found"
            
        except Exception as e:
            logger.error(f"Error scraping {linkedin_url}: {str(e)}")
            return "Error"

def process_with_maximum_stealth(input_file: str, url_column: str = 'LinkedIn_URL', 
                                size_column: str = 'Company_Size', 
                                output_file: str = None,
                                wait_min: int = 60, wait_max: int = 120):
    """Process with maximum stealth - new scraper instance for each company"""
    
    try:
        # Load Excel file
        logger.info(f"Processing Excel file: {input_file}")
        df = pd.read_excel(input_file)
        logger.info(f"Loaded {len(df)} rows from Excel file")
        
        # Set output file
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_stealth_results.xlsx"
        
        processed_count = 0
        success_count = 0
        
        for index, row in df.iterrows():
            linkedin_url = row[url_column]
            
            # Skip if URL is empty
            if pd.isna(linkedin_url) or linkedin_url.strip() == '':
                logger.info(f"Row {index + 1}: Skipping empty URL")
                continue
            
            # Skip if size already exists
            current_size = str(row[size_column]).strip()
            if current_size and current_size not in ['', 'nan', 'None']:
                logger.info(f"Row {index + 1}: Company size already exists ({current_size}), skipping")
                continue
            
            logger.info(f"Row {index + 1}: Processing {linkedin_url}")
            
            # Create completely fresh scraper instance
            scraper = StealthLinkedInScraper()
            
            # Extract company size
            company_size = scraper.extract_company_size(linkedin_url.strip())
            
            if company_size and company_size not in ['Not Found', 'Error', 'Timeout']:
                # Convert to string to avoid pandas dtype warning
                df.at[index, size_column] = str(company_size)
                success_count += 1
                logger.info(f"Row {index + 1}: Successfully updated - {company_size}")
            else:
                df.at[index, size_column] = str(company_size or 'Not Found')
                logger.warning(f"Row {index + 1}: Could not extract company size - {company_size}")
            
            processed_count += 1
            
            # Save progress
            df.to_excel(output_file, index=False)
            
            # Wait between companies (except for the last one)
            if processed_count < len(df):
                wait_time = random.uniform(wait_min, wait_max)
                logger.info(f"Waiting {wait_time:.1f} seconds before next company...")
                time.sleep(wait_time)
        
        logger.info(f"Processing complete! Processed: {processed_count}, Success: {success_count}")
        logger.info(f"Success rate: {(success_count/processed_count)*100:.1f}%")
        logger.info(f"Results saved to: {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        raise

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Stealth LinkedIn Company Size Scraper')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('--url-column', default='LinkedIn_URL', help='Name of column containing LinkedIn URLs')
    parser.add_argument('--size-column', default='Company_Size', help='Name of column to store company sizes')
    parser.add_argument('--output-file', help='Path to output Excel file (optional)')
    parser.add_argument('--wait-min', type=int, default=60, help='Minimum wait time between companies (seconds)')
    parser.add_argument('--wait-max', type=int, default=120, help='Maximum wait time between companies (seconds)')
    
    args = parser.parse_args()
    
    try:
        process_with_maximum_stealth(
            input_file=args.input_file,
            url_column=args.url_column,
            size_column=args.size_column,
            output_file=args.output_file,
            wait_min=args.wait_min,
            wait_max=args.wait_max
        )
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()