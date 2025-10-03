#!/usr/bin/env python3
"""
Enhanced Company Website Scraper - Improved to catch company size patterns
Based on user feedback showing "11-50 employees" format
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
from typing import Optional
import random
from urllib.parse import urljoin
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_website_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ImprovedCompanyWebsiteScraper:
    def __init__(self, delay_range=(1, 3)):
        self.delay_range = delay_range
        self.session = requests.Session()
        
        # Set headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
        })
    
    def extract_company_info_from_website(self, company_name: str, website_url: str = None):
        """Enhanced extraction with better patterns"""
        result = {
            'company_size': None,
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
                urljoin(website_url, '/team'),
                urljoin(website_url, '/careers'),
                urljoin(website_url, '/overview'),
            ]
            
            for page_url in pages_to_try:
                try:
                    company_info = self._scrape_page_enhanced(page_url)
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
        """Enhanced website discovery"""
        # Clean company name
        clean_name = company_name.lower().replace(' ', '').replace('-', '').replace('_', '')
        
        common_patterns = [
            f"https://www.{clean_name}.com",
            f"https://{clean_name}.com",
            f"https://www.{company_name.lower().replace(' ', '')}.com",
            f"https://{company_name.lower().replace(' ', '')}.com",
            f"https://www.{company_name.lower().replace(' ', '-')}.com",
            f"https://{company_name.lower().replace(' ', '-')}.com",
            f"https://www.{company_name.lower().replace(' ', '').replace('.', '')}.com",
            # Try .vc for venture capital firms
            f"https://www.{clean_name}.vc",
            f"https://{clean_name}.vc",
            # Try .co
            f"https://www.{clean_name}.co",
            f"https://{clean_name}.co",
        ]
        
        for url in common_patterns:
            try:
                response = self.session.head(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Found website for {company_name}: {url}")
                    return url
            except:
                continue
        
        # Try specific patterns for your companies
        special_cases = {
            '2150': 'https://www.2150.vc',
            '10elms': 'https://www.10elms.com',
            '17capital': 'https://www.17capital.com',
            '1fs wealth': 'https://1fswealth.com',
            '1st2notify': 'https://1st2notify.com'
        }
        
        clean_name_lower = clean_name.lower()
        for key, url in special_cases.items():
            if key in clean_name_lower:
                try:
                    response = self.session.head(url, timeout=10)
                    if response.status_code == 200:
                        logger.info(f"Found special case website for {company_name}: {url}")
                        return url
                except:
                    continue
        
        logger.warning(f"Could not find website for {company_name}")
        return None
    
    def _scrape_page_enhanced(self, url: str):
        """Enhanced page scraping with better patterns"""
        try:
            # Add delay
            delay = random.uniform(*self.delay_range)
            time.sleep(delay)
            
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for company size information with enhanced patterns
            company_size = self._extract_company_size_enhanced(soup)
            
            if company_size:
                return {
                    'company_size': company_size
                }
            
            return None
            
        except Exception as e:
            logger.debug(f"Error scraping {url}: {str(e)}")
            return None
    
    def _extract_company_size_enhanced(self, soup: BeautifulSoup) -> Optional[str]:
        """Enhanced extraction with patterns from screenshot"""
        
        # Get all text content
        text_content = soup.get_text()
        
        # Enhanced patterns based on the screenshot format "11-50 employees"
        enhanced_patterns = [
            # Exact pattern from screenshot
            r'(\d{1,3}-\d{1,4}\s+employees?)',
            r'(\d{1,3}-\d{1,4}\s*employees?)',
            
            # Standard patterns
            r'(\d{1,3}(?:,\d{3})*\+?\s*(?:-\s*\d{1,3}(?:,\d{3})*\+?)?\s*employees?)',
            r'((?:1-10|11-50|51-200|201-500|501-1000|1001-5000|5001-10000|10001\+)\s*employees?)',
            
            # Company size variations
            r'(Company size[:\s]*\d{1,3}-\d{1,4}\s*employees?)',
            r'(Size[:\s]*\d{1,3}-\d{1,4}\s*employees?)',
            
            # Team size patterns
            r'(team of\s+\d{1,3}-\d{1,4})',
            r'(staff of\s+\d{1,3}-\d{1,4})',
            r'(workforce of\s+\d{1,3}-\d{1,4})',
            
            # More flexible patterns
            r'(\d{1,3}\+?\s*(?:-\s*\d{1,4}\+?)?\s*people)',
            r'(\d{1,3}\+?\s*(?:-\s*\d{1,4}\+?)?\s*team members?)',
        ]
        
        # Try each pattern
        for pattern in enhanced_patterns:
            matches = re.finditer(pattern, text_content, re.IGNORECASE)
            for match in matches:
                potential_size = match.group(1).strip()
                logger.info(f"Found potential size with pattern '{pattern}': {potential_size}")
                if self._is_reasonable_company_size_enhanced(potential_size):
                    return potential_size
        
        # Look in specific HTML elements that might contain company info
        specific_selectors = [
            # Common class names for company info
            '[class*="company-size"]',
            '[class*="about"]',
            '[class*="team"]',
            '[class*="overview"]',
            '[class*="info"]',
            # ID selectors
            '#about',
            '#company-info',
            '#team',
            '#overview'
        ]
        
        for selector in specific_selectors:
            try:
                elements = soup.select(selector)
                for element in elements:
                    element_text = element.get_text()
                    for pattern in enhanced_patterns:
                        matches = re.finditer(pattern, element_text, re.IGNORECASE)
                        for match in matches:
                            potential_size = match.group(1).strip()
                            if self._is_reasonable_company_size_enhanced(potential_size):
                                logger.info(f"Found size in element {selector}: {potential_size}")
                                return potential_size
            except:
                continue
        
        # Look for table rows or definition lists (common in company info pages)
        for tag_combo in [('dt', 'dd'), ('th', 'td'), ('label', 'span')]:
            try:
                labels = soup.find_all(tag_combo[0])
                for label in labels:
                    if any(keyword in label.get_text().lower() for keyword in ['size', 'employees', 'team', 'staff']):
                        # Look for corresponding value
                        next_sibling = label.find_next_sibling(tag_combo[1])
                        if next_sibling:
                            text = next_sibling.get_text()
                            for pattern in enhanced_patterns:
                                matches = re.finditer(pattern, text, re.IGNORECASE)
                                for match in matches:
                                    potential_size = match.group(1).strip()
                                    if self._is_reasonable_company_size_enhanced(potential_size):
                                        return potential_size
            except:
                continue
        
        return None
    
    def _is_reasonable_company_size_enhanced(self, size_str: str) -> bool:
        """Enhanced validation for company size"""
        try:
            # Extract numbers from the string
            numbers = re.findall(r'\d+', size_str)
            if numbers:
                # Check if any number is in reasonable range (1 to 1 million)
                for num_str in numbers:
                    num = int(num_str)
                    if 1 <= num <= 1000000:
                        return True
        except:
            pass
        return False

def process_excel_enhanced(input_file: str, company_column: str, website_column: str = None, 
                          size_column: str = 'Company_Size', output_file: str = None):
    """Enhanced Excel processing"""
    if output_file is None:
        output_file = input_file
    
    logger.info(f"Processing Excel file with enhanced scraper: {input_file}")
    
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
        
        # Ensure string type and clear empty/nan values
        df[size_column] = df[size_column].astype(str).replace('nan', '').replace('', '')
        
        # Initialize enhanced scraper
        scraper = ImprovedCompanyWebsiteScraper()
        
        # Process each row
        processed_count = 0
        success_count = 0
        
        for index, row in df.iterrows():
            company_name = row[company_column]
            
            # Skip if company name is empty
            if pd.isna(company_name) or company_name.strip() == '':
                logger.info(f"Row {index + 1}: Skipping empty company name")
                continue
            
            # Skip if size already exists and is not empty
            current_size = str(row[size_column]).strip()
            if current_size and current_size not in ['', 'nan', 'None', 'No Information Found', 'Website Not Found']:
                logger.info(f"Row {index + 1}: Company size already exists ({current_size}), skipping")
                continue
            
            # Get website URL if available
            website_url = None
            if website_column and website_column in df.columns:
                website_url = row[website_column]
                if pd.isna(website_url):
                    website_url = None
            
            # Extract company information
            logger.info(f"Processing {company_name}...")
            company_info = scraper.extract_company_info_from_website(
                company_name.strip(), 
                website_url
            )
            
            if company_info['status'] == 'Success' and company_info['company_size']:
                df.at[index, size_column] = company_info['company_size']
                success_count += 1
                logger.info(f"Row {index + 1}: SUCCESS - {company_info['company_size']}")
            else:
                df.at[index, size_column] = company_info['status']
                logger.warning(f"Row {index + 1}: {company_info['status']}")
            
            processed_count += 1
            
            # Save progress every 3 companies
            if processed_count % 3 == 0:
                df.to_excel(output_file, index=False)
                logger.info(f"Progress saved: {processed_count} processed, {success_count} successful")
        
        # Save final results
        df.to_excel(output_file, index=False)
        logger.info(f"Enhanced processing complete! Processed: {processed_count}, Success: {success_count}")
        logger.info(f"Results saved to: {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced Company Website Scraper')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('--company-column', default='Company Name', help='Column containing company names')
    parser.add_argument('--website-column', help='Column containing website URLs (optional)')
    parser.add_argument('--size-column', default='Company_Size', help='Column to store company sizes')
    parser.add_argument('--output-file', help='Path to output Excel file (optional)')
    
    args = parser.parse_args()
    
    try:
        process_excel_enhanced(
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