#!/usr/bin/env python3
"""
Complete Company Data Scraper
Combines LinkedIn data (company size, industry) with ZoomInfo revenue data
"""

import pandas as pd
import logging
import time
import random
import os
import sys
from typing import Dict, Optional

# Import our scrapers
from linkedin_company_scraper_enhanced import EnhancedLinkedInScraper
from zoominfo_revenue_scraper import ZoomInfoRevenueScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('complete_company_scraper.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class CompleteCompanyScraper:
    def __init__(self):
        """Initialize the complete company scraper"""
        self.linkedin_scraper = EnhancedLinkedInScraper()
        self.zoominfo_scraper = ZoomInfoRevenueScraper()
    
    def scrape_complete_data(self, company_name: str, linkedin_url: str = None, website_url: str = None) -> Dict:
        """Scrape complete company data from LinkedIn and ZoomInfo"""
        result = {
            'company_name': company_name,
            'company_size': None,
            'industry': None,
            'revenue': None,
            'linkedin_status': 'Not Attempted',
            'revenue_status': 'Not Attempted',
            'linkedin_source_url': linkedin_url,
            'revenue_source_url': None
        }
        
        # Scrape LinkedIn data if URL provided
        if linkedin_url:
            try:
                logger.info(f"Scraping LinkedIn data for {company_name}")
                
                company_size = self.linkedin_scraper.extract_company_size(linkedin_url)
                industry = self.linkedin_scraper.extract_industry(linkedin_url)
                
                if company_size and company_size not in ['Invalid URL', 'Blocked by LinkedIn', 'Rate Limited']:
                    result['company_size'] = company_size
                    result['linkedin_status'] = 'Success - Size Found'
                else:
                    result['linkedin_status'] = company_size or 'Failed'
                
                if industry and industry not in ['Invalid URL', 'Blocked by LinkedIn', 'Rate Limited']:
                    result['industry'] = industry
                    if result['linkedin_status'] == 'Success - Size Found':
                        result['linkedin_status'] = 'Success - Size & Industry Found'
                    else:
                        result['linkedin_status'] = 'Success - Industry Found'
                
                # Add a delay after LinkedIn scraping
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"LinkedIn scraping failed for {company_name}: {str(e)}")
                result['linkedin_status'] = f'Error: {str(e)}'
        
        # Scrape ZoomInfo revenue data if website URL provided
        if website_url:
            try:
                logger.info(f"Scraping ZoomInfo revenue for {company_name}")
                
                revenue_result = self.zoominfo_scraper.get_revenue_from_zoominfo(company_name, website_url)
                
                result['revenue'] = revenue_result['revenue']
                result['revenue_status'] = revenue_result['status']
                result['revenue_source_url'] = revenue_result['source_url']
                
                # Add a delay after ZoomInfo scraping
                time.sleep(random.uniform(3, 6))
                
            except Exception as e:
                logger.error(f"ZoomInfo scraping failed for {company_name}: {str(e)}")
                result['revenue_status'] = f'Error: {str(e)}'
        
        return result

def process_excel_file_complete(input_file: str, 
                               company_column: str = 'Company_Name',
                               linkedin_column: str = 'LinkedIn_URL',
                               website_column: str = 'Website_URL',
                               output_file: str = None,
                               wait_min: int = 10,
                               wait_max: int = 20) -> pd.DataFrame:
    """Process Excel file to extract complete company data"""
    
    try:
        # Read input file
        logger.info(f"Reading input file: {input_file}")
        df = pd.read_excel(input_file)
        logger.info(f"Found {len(df)} companies to process")
        
        # Validate required columns
        if company_column not in df.columns:
            raise ValueError(f"Required column '{company_column}' not found in Excel file")
        
        # Prepare output file name
        if not output_file:
            base_name = os.path.splitext(input_file)[0]
            output_file = f"{base_name}_complete_results.xlsx"
        
        # Initialize scraper
        scraper = CompleteCompanyScraper()
        
        # Add new columns for results
        new_columns = [
            'Company_Size_Complete', 'Industry_Complete', 'Revenue_Complete',
            'LinkedIn_Status_Complete', 'Revenue_Status_Complete',
            'LinkedIn_Source_URL', 'Revenue_Source_URL'
        ]
        
        for col in new_columns:
            if col not in df.columns:
                df[col] = None
        
        # Track statistics
        stats = {
            'processed': 0,
            'linkedin_success': 0,
            'revenue_success': 0,
            'complete_success': 0
        }
        
        # Process each company
        for index, row in df.iterrows():
            company_name = row.get(company_column)
            linkedin_url = row.get(linkedin_column) if linkedin_column in df.columns else None
            website_url = row.get(website_column) if website_column in df.columns else None
            
            if pd.isna(company_name):
                logger.warning(f"Skipping row {index + 1}: Missing company name")
                continue
            
            # Skip if both URLs are missing
            if pd.isna(linkedin_url) and pd.isna(website_url):
                logger.warning(f"Skipping {company_name}: No LinkedIn or Website URL provided")
                continue
            
            logger.info(f"Processing {company_name} ({stats['processed'] + 1}/{len(df)})")
            
            # Scrape complete data
            result = scraper.scrape_complete_data(
                company_name=str(company_name),
                linkedin_url=str(linkedin_url) if not pd.isna(linkedin_url) else None,
                website_url=str(website_url) if not pd.isna(website_url) else None
            )
            
            # Update DataFrame
            df.at[index, 'Company_Size_Complete'] = result['company_size']
            df.at[index, 'Industry_Complete'] = result['industry']
            df.at[index, 'Revenue_Complete'] = result['revenue']
            df.at[index, 'LinkedIn_Status_Complete'] = result['linkedin_status']
            df.at[index, 'Revenue_Status_Complete'] = result['revenue_status']
            df.at[index, 'LinkedIn_Source_URL'] = result['linkedin_source_url']
            df.at[index, 'Revenue_Source_URL'] = result['revenue_source_url']
            
            # Update statistics
            stats['processed'] += 1
            if result['company_size'] or result['industry']:
                stats['linkedin_success'] += 1
            if result['revenue']:
                stats['revenue_success'] += 1
            if (result['company_size'] or result['industry']) and result['revenue']:
                stats['complete_success'] += 1
            
            # Add wait time between companies
            if stats['processed'] < len(df):
                wait_time = random.uniform(wait_min, wait_max)
                logger.info(f"Waiting {wait_time:.1f} seconds before next company...")
                time.sleep(wait_time)
            
            # Save progress periodically
            if stats['processed'] % 5 == 0:
                df.to_excel(output_file, index=False)
                logger.info(f"Progress saved: {stats['processed']}/{len(df)} processed")
                logger.info(f"LinkedIn success: {stats['linkedin_success']}, Revenue success: {stats['revenue_success']}")
        
        # Save final results
        df.to_excel(output_file, index=False)
        
        # Print final statistics
        logger.info("=" * 60)
        logger.info("COMPLETE COMPANY SCRAPING RESULTS")
        logger.info("=" * 60)
        logger.info(f"Total companies processed: {stats['processed']}")
        logger.info(f"LinkedIn data found: {stats['linkedin_success']} ({(stats['linkedin_success']/stats['processed']*100):.1f}%)")
        logger.info(f"Revenue data found: {stats['revenue_success']} ({(stats['revenue_success']/stats['processed']*100):.1f}%)")
        logger.info(f"Complete data found: {stats['complete_success']} ({(stats['complete_success']/stats['processed']*100):.1f}%)")
        logger.info(f"Results saved to: {output_file}")
        logger.info("=" * 60)
        
        return df
        
    except Exception as e:
        logger.error(f"Error processing Excel file: {str(e)}")
        raise

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Complete Company Data Scraper (LinkedIn + ZoomInfo)')
    parser.add_argument('input_file', help='Path to input Excel file')
    parser.add_argument('--company-column', default='Company_Name', help='Name of column containing company names')
    parser.add_argument('--linkedin-column', default='LinkedIn_URL', help='Name of column containing LinkedIn URLs')
    parser.add_argument('--website-column', default='Website_URL', help='Name of column containing website URLs')
    parser.add_argument('--output-file', help='Path to output Excel file (optional)')
    parser.add_argument('--wait-min', type=int, default=10, help='Minimum wait time between companies (seconds)')
    parser.add_argument('--wait-max', type=int, default=20, help='Maximum wait time between companies (seconds)')
    
    args = parser.parse_args()
    
    try:
        process_excel_file_complete(
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