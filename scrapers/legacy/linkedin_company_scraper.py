#!/usr/bin/env python3
"""
LinkedIn Company Size Scraper
Extracts company size information from LinkedIn company pages and updates Excel file
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

class LinkedInCompanyScraper:
    def __init__(self, config=None):
        """
        Initialize the scraper with configuration
        
        Args:
            config: Configuration dictionary (optional)
        """
        self.config = config or load_config()
        scraper_settings = self.config.get('scraper_settings', {})
        
        self.delay_range = tuple(scraper_settings.get('delay_range', [2, 5]))
        self.timeout = scraper_settings.get('timeout', 30)
        self.max_retries = scraper_settings.get('max_retries', 3)
        
        self.session = requests.Session()
        
        # Set headers to mimic a real browser
        user_agent = scraper_settings.get('user_agent', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Load patterns and selectors from config
        self.size_patterns = self.config.get('company_size_patterns', [
            r'(\d{1,3}(?:,\d{3})*\+?\s*(?:-\s*\d{1,3}(?:,\d{3})*\+?)?\s*employees?)',
            r'((?:\d{1,3}(?:,\d{3})*\+?)\s*(?:-\s*(?:\d{1,3}(?:,\d{3})*\+?))?\s*employees?)',
            r'(Company size[:\s]*\d{1,3}(?:,\d{3})*\+?\s*(?:-\s*\d{1,3}(?:,\d{3})*\+?)?\s*employees?)',
        ])
        
        self.linkedin_selectors = self.config.get('linkedin_selectors', [
            'dd[class*="company-size"]',
            'span[class*="company-size"]',
            'div[class*="company-size"]',
            '.org-top-card-summary-info-list__info-item',
            '.org-about-company-module__company-size-definition'
        ])
    
    def extract_company_size(self, linkedin_url: str) -> Optional[str]:
        """
        Extract company size from LinkedIn company page
        
        Args:
            linkedin_url: LinkedIn company page URL
            
        Returns:
            Company size string or None if not found
        """
        try:
            logger.info(f"Scraping: {linkedin_url}")
            
            # Add random delay to avoid being blocked
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            response = self.session.get(linkedin_url, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Multiple strategies to find company size
            company_size = self._find_company_size_strategy1(soup)
            
            if not company_size:
                company_size = self._find_company_size_strategy2(soup)
            
            if not company_size:
                company_size = self._find_company_size_strategy3(soup)
            
            if company_size:
                logger.info(f"Found company size: {company_size}")
                return company_size
            else:
                logger.warning(f"Company size not found for: {linkedin_url}")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Request error for {linkedin_url}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error for {linkedin_url}: {str(e)}")
            return None
    
    def _find_company_size_strategy1(self, soup: BeautifulSoup) -> Optional[str]:
        """Strategy 1: Look for company size in specific LinkedIn selectors"""
        for selector in self.linkedin_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                if self._is_company_size_text(text):
                    return text
        return None
    
    def _find_company_size_strategy2(self, soup: BeautifulSoup) -> Optional[str]:
        """Strategy 2: Look for text patterns that indicate company size"""
        text_content = soup.get_text()
        
        for pattern in self.size_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                return match.group(1).strip()
        
        return None
    
    def _find_company_size_strategy3(self, soup: BeautifulSoup) -> Optional[str]:
        """Strategy 3: Look for specific keywords followed by numbers"""
        keywords = ['employees', 'company size', 'team size', 'workforce']
        
        for keyword in keywords:
            # Find elements containing the keyword (using 'string' instead of deprecated 'text')
            elements = soup.find_all(string=re.compile(keyword, re.IGNORECASE))
            
            for element in elements:
                # Look at the parent element and nearby text
                parent = element.parent if element.parent else element
                text = parent.get_text(strip=True)
                
                # Extract numbers that might represent company size
                numbers = re.findall(r'\d{1,3}(?:,\d{3})*\+?(?:\s*-\s*\d{1,3}(?:,\d{3})*\+?)?', text)
                
                if numbers:
                    # Return the first reasonable number found
                    for num in numbers:
                        if self._is_reasonable_company_size(num):
                            return f"{num} employees"
        
        return None
    
    def _is_company_size_text(self, text: str) -> bool:
        """Check if text appears to be company size information"""
        text_lower = text.lower()
        return (
            'employee' in text_lower and
            any(char.isdigit() for char in text) and
            len(text) < 100  # Reasonable length
        )
    
    def _is_reasonable_company_size(self, size_str: str) -> bool:
        """Check if the extracted number is a reasonable company size"""
        try:
            # Remove commas and convert to int
            num_str = size_str.replace(',', '').replace('+', '')
            if '-' in num_str:
                num_str = num_str.split('-')[0]  # Take the lower bound
            
            num = int(num_str)
            # Reasonable range for company size
            return 1 <= num <= 10000000
        except:
            return False

def process_excel_file(input_file: str, url_column: str, size_column: str, output_file: str = None):
    """
    Process Excel file to extract company sizes from LinkedIn URLs
    
    Args:
        input_file: Path to input Excel file
        url_column: Name of column containing LinkedIn URLs
        size_column: Name of column to store company sizes
        output_file: Path to output Excel file (optional, defaults to input_file)
    """
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
        
        # Ensure the size column is of string type to avoid dtype warnings
        df[size_column] = df[size_column].astype(str)
        
        # Load configuration and initialize scraper
        config = load_config()
        scraper = LinkedInCompanyScraper(config)
        
        # Get save interval from config
        save_interval = config.get('excel_settings', {}).get('save_progress_interval', 10)
        
        # Process each row
        processed_count = 0
        success_count = 0
        
        for index, row in df.iterrows():
            linkedin_url = row[url_column]
            
            # Skip if URL is empty or size already exists
            if pd.isna(linkedin_url) or linkedin_url.strip() == '':
                logger.info(f"Row {index + 1}: Skipping empty URL")
                continue
            
            if pd.notna(row[size_column]) and row[size_column].strip() != '':
                logger.info(f"Row {index + 1}: Company size already exists, skipping")
                continue
            
            # Extract company size
            company_size = scraper.extract_company_size(linkedin_url.strip())
            
            if company_size:
                df.at[index, size_column] = company_size
                success_count += 1
                logger.info(f"Row {index + 1}: Successfully updated company size")
            else:
                df.at[index, size_column] = 'Not Found'
                logger.warning(f"Row {index + 1}: Could not extract company size")
            
            processed_count += 1
            
            # Save progress periodically
            if processed_count % save_interval == 0:
                df.to_excel(output_file, index=False)
                logger.info(f"Progress saved: {processed_count} rows processed")
        
        # Save final results
        df.to_excel(output_file, index=False)
        logger.info(f"Processing complete! Processed: {processed_count}, Success: {success_count}")
        logger.info(f"Results saved to: {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        raise

def main():
    """Main function to run the scraper"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Extract company sizes from LinkedIn URLs in Excel file')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('--url-column', default='LinkedIn_URL', help='Name of column containing LinkedIn URLs')
    parser.add_argument('--size-column', default='Company_Size', help='Name of column to store company sizes')
    parser.add_argument('--output-file', help='Path to output Excel file (optional)')
    
    args = parser.parse_args()
    
    try:
        process_excel_file(
            input_file=args.input_file,
            url_column=args.url_column,
            size_column=args.size_column,
            output_file=args.output_file
        )
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()