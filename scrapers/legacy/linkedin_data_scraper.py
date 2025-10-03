#!/usr/bin/env python3
"""
LinkedIn Company Data Scraper - Enhanced Version
Extracts Company Size AND Industry in LinkedIn's exact formats
"""

import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
import logging
import random
from typing import Optional, Dict, Tuple
import sys
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('linkedin_data_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LinkedInDataScraper:
    def __init__(self):
        """Enhanced scraper for LinkedIn company data (size + industry)"""
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
        ]
        
    def _create_session(self):
        """Create a fresh session with realistic headers"""
        session = requests.Session()
        user_agent = random.choice(self.user_agents)
        
        session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        })
        return session
    
    def extract_company_data(self, linkedin_url: str) -> Dict[str, str]:
        """Extract both company size and industry from LinkedIn"""
        try:
            logger.info(f"Attempting to scrape: {linkedin_url}")
            
            # Pre-request delay
            time.sleep(random.uniform(3, 8))
            
            # Create fresh session
            session = self._create_session()
            
            # Make request
            response = session.get(linkedin_url, timeout=30)
            
            if response.status_code == 999:
                logger.warning(f"LinkedIn blocked request (999): {linkedin_url}")
                return {"company_size": "Blocked by LinkedIn", "industry": "Blocked by LinkedIn"}
            elif response.status_code != 200:
                logger.warning(f"HTTP {response.status_code}: {linkedin_url}")
                return {"company_size": f"HTTP Error {response.status_code}", "industry": f"HTTP Error {response.status_code}"}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text()
            
            # Extract company size
            company_size = self._extract_company_size(text_content)
            
            # Extract industry
            industry = self._extract_industry(text_content)
            
            result = {
                "company_size": company_size or "Not Found",
                "industry": industry or "Not Found"
            }
            
            logger.info(f"Successfully extracted - Size: {result['company_size']}, Industry: {result['industry']}")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping {linkedin_url}: {str(e)}")
            return {"company_size": "Error", "industry": "Error"}
    
    def _extract_company_size(self, text_content: str) -> Optional[str]:
        """Extract company size in LinkedIn's exact range format"""
        
        # LinkedIn's EXACT range patterns (highest priority)
        linkedin_ranges = [
            r'(1-10)\s+employees?',
            r'(11-50)\s+employees?', 
            r'(51-200)\s+employees?',
            r'(201-500)\s+employees?',
            r'(501-1,000)\s+employees?',
            r'(501-1000)\s+employees?',
            r'(1,001-5,000)\s+employees?',
            r'(1001-5000)\s+employees?',
            r'(5,001-10,000)\s+employees?',
            r'(5001-10000)\s+employees?',
            r'(10,001\+)\s+employees?',
            r'(10000\+)\s+employees?'
        ]
        
        # Try LinkedIn's standard ranges first
        for pattern in linkedin_ranges:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                size = matches[0].strip()
                return f"{size} employees"
        
        # Fallback: look for Company size section specifically
        company_size_patterns = [
            r'Company size[:\s]*(1-10|11-50|51-200|201-500|501-1,?000|1,?001-5,?000|5,?001-10,?000|10,?000\+)\s+employees?',
            r'Company size[:\s]*(\d+(?:,\d+)?-\d+(?:,\d+)?)\s+employees?'
        ]
        
        for pattern in company_size_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                size = matches[0].strip()
                return f"{size} employees"
        
        # Last resort: any range pattern
        general_patterns = [
            r'(\d+(?:,\d+)?-\d+(?:,\d+)?)\s+employees?',
            r'(\d+-\d+)\s+employees?'
        ]
        
        for pattern in general_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE)
            if matches:
                size = matches[0].strip()
                return f"{size} employees"
        
        return None
    
    def _extract_industry(self, text_content: str) -> Optional[str]:
        """Extract industry information from LinkedIn"""
        
        # Industry patterns - LinkedIn typically shows this after "Industry"
        industry_patterns = [
            # Direct industry patterns
            r'Industry\s+([^\n\r]+?)(?:\s+Company size|\s+Headquarters|\s+Type|\s+Founded|\s+Specialties|$)',
            r'Industry[:\s]+([^\n\r]+?)(?:\s+Company|\s+Headquarters|\s+Type|\s+Founded|\s+Specialties|$)',
            
            # Alternative patterns
            r'Industry[:\s]*([^\n\r]{3,50})(?:\s+(?:Company size|Headquarters|Type|Founded|Specialties))',
            
            # More flexible patterns
            r'Industry\s*[:]\s*([^\n\r]{3,100}?)(?:\s+[A-Z])',
            r'Industry\s+([A-Za-z\s&,.-]{3,50}?)(?:\s+(?:Company|Headquarters|Type|Founded|Specialties))',
        ]
        
        for pattern in industry_patterns:
            matches = re.findall(pattern, text_content, re.IGNORECASE | re.MULTILINE)
            if matches:
                industry = matches[0].strip()
                # Clean up the industry string
                industry = re.sub(r'\s+', ' ', industry)  # Remove extra whitespace
                industry = industry.strip('.,;')  # Remove trailing punctuation
                
                # Skip if it's too short or looks like other data
                if len(industry) >= 3 and not re.match(r'^\d+', industry):
                    return industry
        
        return None

def process_enhanced(input_file: str, url_column: str = 'LinkedIn_URL', 
                    size_column: str = 'Company_Size', industry_column: str = 'Industry',
                    output_file: str = None, wait_min: int = 45, wait_max: int = 75):
    """Process with enhanced data extraction (size + industry)"""
    
    try:
        logger.info(f"Processing Excel file: {input_file}")
        df = pd.read_excel(input_file)
        logger.info(f"Loaded {len(df)} rows from Excel file")
        
        if output_file is None:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_enhanced_results.xlsx"
        
        # Ensure industry column exists
        if industry_column not in df.columns:
            df[industry_column] = ''
            logger.info(f"Added new column: {industry_column}")
        
        processed_count = 0
        size_success_count = 0
        industry_success_count = 0
        
        for index, row in df.iterrows():
            linkedin_url = row[url_column]
            
            if pd.isna(linkedin_url) or linkedin_url.strip() == '':
                logger.info(f"Row {index + 1}: Skipping empty URL")
                continue
            
            # Check if both size and industry already exist
            current_size = str(row[size_column]).strip()
            current_industry = str(row[industry_column]).strip()
            
            if (current_size and current_size not in ['', 'nan', 'None'] and 
                current_industry and current_industry not in ['', 'nan', 'None']):
                logger.info(f"Row {index + 1}: Both size and industry already exist, skipping")
                continue
            
            logger.info(f"Row {index + 1}: Processing {linkedin_url}")
            
            # Create fresh scraper instance
            scraper = LinkedInDataScraper()
            data = scraper.extract_company_data(linkedin_url.strip())
            
            # Update company size if needed
            if not current_size or current_size in ['', 'nan', 'None']:
                df.at[index, size_column] = str(data['company_size'])
                if data['company_size'] not in ['Not Found', 'Error', 'Timeout', 'Blocked by LinkedIn']:
                    size_success_count += 1
                    logger.info(f"✅ Row {index + 1}: Company Size - {data['company_size']}")
                else:
                    logger.warning(f"❌ Row {index + 1}: Company Size - {data['company_size']}")
            
            # Update industry if needed
            if not current_industry or current_industry in ['', 'nan', 'None']:
                df.at[index, industry_column] = str(data['industry'])
                if data['industry'] not in ['Not Found', 'Error', 'Timeout', 'Blocked by LinkedIn']:
                    industry_success_count += 1
                    logger.info(f"✅ Row {index + 1}: Industry - {data['industry']}")
                else:
                    logger.warning(f"❌ Row {index + 1}: Industry - {data['industry']}")
            
            processed_count += 1
            
            # Save progress
            df.to_excel(output_file, index=False)
            
            # Wait between companies
            if processed_count < len(df):
                wait_time = random.uniform(wait_min, wait_max)
                logger.info(f"Waiting {wait_time:.1f} seconds before next company...")
                time.sleep(wait_time)
        
        logger.info(f"Processing complete! Processed: {processed_count}")
        logger.info(f"Company Size Success: {size_success_count}/{processed_count}")
        logger.info(f"Industry Success: {industry_success_count}/{processed_count}")
        logger.info(f"Results saved to: {output_file}")
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        raise

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhanced LinkedIn Company Data Scraper (Size + Industry)')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('--url-column', default='LinkedIn_URL', help='Name of column containing LinkedIn URLs')
    parser.add_argument('--size-column', default='Company_Size', help='Name of column to store company sizes')
    parser.add_argument('--industry-column', default='Industry', help='Name of column to store industries')
    parser.add_argument('--output-file', help='Path to output Excel file (optional)')
    parser.add_argument('--wait-min', type=int, default=45, help='Minimum wait time between companies (seconds)')
    parser.add_argument('--wait-max', type=int, default=75, help='Maximum wait time between companies (seconds)')
    
    args = parser.parse_args()
    
    try:
        process_enhanced(
            input_file=args.input_file,
            url_column=args.url_column,
            size_column=args.size_column,
            industry_column=args.industry_column,
            output_file=args.output_file,
            wait_min=args.wait_min,
            wait_max=args.wait_max
        )
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()