#!/usr/bin/env python3
"""
Alternative Company Size Scraper
Attempts to extract company size from company websites instead of LinkedIn
Often more successful than LinkedIn scraping
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import Optional, List, Dict
import random
from urllib.parse import urlparse, urljoin
import os
import sys
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('company_website_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CompanyWebsiteScraper:
    def __init__(self, delay_range=(1, 3)):
        """
        Initialize scraper for company websites
        Generally more permissive than LinkedIn
        """
        self.delay_range = delay_range
        self.session = requests.Session()
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
    
    def extract_company_info_from_website(self, company_name: str, website_url: str = None) -> Dict[str, str]:
        """
        Extract company information from company website
        
        Args:
            company_name: Name of the company
            website_url: Company website URL (optional)
            
        Returns:
            Dictionary with company size and other info
        """
        result = {
            'company_size': None,
            'employees': None,
            'source_url': None,
            'status': 'Not Found'
        }
        
        try:
            # If no website URL provided, try to find it
            if not website_url:
                website_url = self._find_company_website(company_name)
                if not website_url:
                    result['status'] = 'Website Not Found'
                    return result
            
            logger.info(f"Scraping company website: {website_url}")
            
            # Try multiple pages on the website
            pages_to_try = [
                website_url,
                urljoin(website_url, '/about'),
                urljoin(website_url, '/about-us'),
                urljoin(website_url, '/company'),
                urljoin(website_url, '/careers'),
                urljoin(website_url, '/team'),
            ]
            
            for page_url in pages_to_try:
                try:
                    company_info = self._scrape_page(page_url)
                    if company_info:
                        result.update(company_info)
                        result['source_url'] = page_url
                        result['status'] = 'Success'
                        logger.info(f"Found company info on: {page_url}")
                        return result
                        
                    # Small delay between pages
                    time.sleep(random.uniform(0.5, 1.5))
                    
                except Exception as e:
                    logger.debug(f"Failed to scrape {page_url}: {str(e)}")
                    continue
            
            result['status'] = 'No Information Found'
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {company_name}: {str(e)}")
            result['status'] = f'Error: {str(e)}'
            return result
    
    def _find_company_website(self, company_name: str) -> Optional[str]:
        """
        Try to find company website using search
        Simple implementation - could be enhanced with search APIs
        """
        # Simple heuristics for common company website patterns
        common_patterns = [
            f"https://www.{company_name.lower().replace(' ', '')}.com",
            f"https://{company_name.lower().replace(' ', '')}.com",
            f"https://www.{company_name.lower().replace(' ', '-')}.com",
            f"https://{company_name.lower().replace(' ', '-')}.com",
        ]
        
        for url in common_patterns:
            try:
                response = self.session.head(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Found website for {company_name}: {url}")
                    return url
            except:
                continue
        
        logger.warning(f"Could not find website for {company_name}")
        return None
    
    def _scrape_page(self, url: str) -> Optional[Dict[str, str]]:
        """Scrape a single page for company information"""
        try:
            # Add delay
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for company size information
            company_size = self._extract_company_size(soup)
            
            if company_size:
                return {
                    'company_size': company_size,
                    'employees': self._normalize_employee_count(company_size)
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Error scraping {url}: {str(e)}")
            return None
    
    def _extract_company_size(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract company size from webpage"""
        
        # Strategy 1: Look for specific patterns in text
        text_content = soup.get_text()
        
        # Enhanced patterns for company websites
        patterns = [
            r'(\d{1,3}(?:,\d{3})*\+?\s*(?:-\s*\d{1,3}(?:,\d{3})*\+?)?\s*employees?)',
            r'(over\s+\d{1,3}(?:,\d{3})*\s+employees?)',
            r'(more than\s+\d{1,3}(?:,\d{3})*\s+employees?)',
            r'(\d{1,3}(?:,\d{3})*\+?\s+team members?)',
            r'(\d{1,3}(?:,\d{3})*\+?\s+people)',
            r'(team of\s+\d{1,3}(?:,\d{3})*\+?)',
            r'(staff of\s+\d{1,3}(?:,\d{3})*\+?)',
            r'(workforce of\s+\d{1,3}(?:,\d{3})*\+?)'
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                potential_size = match.group(1).strip()
                if self._is_reasonable_company_size(potential_size):
                    return potential_size
        
        # Strategy 2: Look in specific sections
        sections_to_check = [
            'about', 'company', 'team', 'careers', 'overview', 'facts'
        ]
        
        for section_name in sections_to_check:
            sections = soup.find_all(['section', 'div', 'p'], 
                                   string=re.compile(section_name, re.IGNORECASE))
            
            for section in sections:
                parent = section.parent if section.parent else section
                section_text = parent.get_text()
                
                for pattern in patterns:
                    matches = re.finditer(pattern, section_text, re.IGNORECASE)
                    for match in matches:
                        potential_size = match.group(1).strip()
                        if self._is_reasonable_company_size(potential_size):
                            return potential_size
        
        # Strategy 3: Look for common size ranges
        size_indicators = [
            "startup", "small business", "mid-size", "large enterprise",
            "Fortune 500", "Fortune 1000", "multinational"
        ]
        
        text_lower = text_content.lower()
        for indicator in size_indicators:
            if indicator in text_lower:
                return f"Company type: {indicator}"
        
        return None
    
    def _is_reasonable_company_size(self, size_str: str) -> bool:
        """Check if extracted size is reasonable"""
        try:
            # Extract numbers from the string
            numbers = re.findall(r'\d{1,3}(?:,\d{3})*', size_str.replace(',', ''))
            if numbers:
                num = int(numbers[0])
                # Reasonable range: 1 to 10 million employees
                return 1 <= num <= 10000000
        except:
            pass
        return False
    
    def _normalize_employee_count(self, size_str: str) -> Optional[str]:
        """Normalize employee count to standard format"""
        try:
            # Extract first number found
            numbers = re.findall(r'\d{1,3}(?:,\d{3})*', size_str)
            if numbers:
                return numbers[0]
        except:
            pass
        return None

def process_excel_with_websites(input_file: str, company_column: str, website_column: str = None, 
                               size_column: str = 'Company_Size', output_file: str = None):
    """
    Process Excel file to extract company sizes from company websites
    
    Args:
        input_file: Path to input Excel file
        company_column: Name of column containing company names
        website_column: Name of column containing website URLs (optional)
        size_column: Name of column to store company sizes
        output_file: Path to output Excel file (optional)
    """
    if output_file is None:
        output_file = input_file
    
    logger.info(f"Processing Excel file: {input_file}")
    
    try:
        # Read Excel file
        df = pd.read_excel(input_file)
        logger.info(f"Loaded {len(df)} rows from Excel file")
        
        # Validate columns
        if company_column not in df.columns:
            raise ValueError(f"Column '{company_column}' not found in Excel file")
        
        # Add size column if it doesn't exist
        if size_column not in df.columns:
            df[size_column] = ''
        
        # Ensure string type
        df[size_column] = df[size_column].astype(str).replace('nan', '')
        
        # Initialize scraper
        scraper = CompanyWebsiteScraper()
        
        # Process each row
        processed_count = 0
        success_count = 0
        
        for index, row in df.iterrows():
            company_name = row[company_column]
            
            # Skip if company name is empty
            if pd.isna(company_name) or company_name.strip() == '':
                logger.info(f"Row {index + 1}: Skipping empty company name")
                continue
            
            # Skip if size already exists
            current_size = str(row[size_column]).strip()
            if current_size and current_size not in ['', 'nan', 'None']:
                logger.info(f"Row {index + 1}: Company size already exists, skipping")
                continue
            
            # Get website URL if available
            website_url = None
            if website_column and website_column in df.columns:
                website_url = row[website_column]
                if pd.isna(website_url):
                    website_url = None
            
            # Extract company information
            company_info = scraper.extract_company_info_from_website(
                company_name.strip(), 
                website_url
            )
            
            if company_info['status'] == 'Success' and company_info['company_size']:
                df.at[index, size_column] = company_info['company_size']
                success_count += 1
                logger.info(f"Row {index + 1}: Success - {company_info['company_size']}")
            else:
                df.at[index, size_column] = company_info['status']
                logger.warning(f"Row {index + 1}: {company_info['status']}")
            
            processed_count += 1
            
            # Save progress every 5 companies
            if processed_count % 5 == 0:
                df.to_excel(output_file, index=False)
                logger.info(f"Progress saved: {processed_count} processed, {success_count} successful")
        
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
    
    parser = argparse.ArgumentParser(description='Company Website Scraper for Company Size')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('--company-column', default='Company_Name', help='Column containing company names')
    parser.add_argument('--website-column', help='Column containing website URLs (optional)')
    parser.add_argument('--size-column', default='Company_Size', help='Column to store company sizes')
    parser.add_argument('--output-file', help='Path to output Excel file (optional)')
    
    args = parser.parse_args()
    
    try:
        process_excel_with_websites(
            input_file=args.input_file,
            company_column=args.company_column,
            website_column=args.website_column,
            size_column=args.size_column,
            output_file=args.output_file
        )
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()