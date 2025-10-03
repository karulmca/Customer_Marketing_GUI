#!/usr/bin/env python3
"""
Mixed Strategy Revenue Scraper
Combines LinkedIn data + Alternative sources + Manual ZoomInfo mapping
"""

import pandas as pd
from linkedin_company_scraper_enhanced import EnhancedLinkedInScraper
from alternative_sources_scraper import AlternativeDataSourcesScraper
import logging
import time
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MixedStrategyRevenueScraper:
    def __init__(self):
        self.linkedin_scraper = EnhancedLinkedInScraper()
        self.alternative_scraper = AlternativeDataSourcesScraper()
        
        # Manual revenue data for companies where you've found it manually
        self.manual_revenue_data = {
            "AIMA - The Alternative Investment Management Association": "$55.2 Million",
            "aima.org": "$55.2 Million",
            # Add more as you find them manually from ZoomInfo or other sources
        }
    
    def get_manual_revenue(self, company_name: str, website_url: str) -> dict:
        """Check if we have manual revenue data for this company"""
        domain = website_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
        
        if company_name in self.manual_revenue_data:
            return {
                'revenue': self.manual_revenue_data[company_name],
                'source': 'Manual Data (ZoomInfo)',
                'source_url': 'Manually collected',
                'status': 'Success (Manual)'
            }
        elif domain in self.manual_revenue_data:
            return {
                'revenue': self.manual_revenue_data[domain],
                'source': 'Manual Data (ZoomInfo)',
                'source_url': 'Manually collected',
                'status': 'Success (Manual)'
            }
        
        return None
    
    def scrape_complete_company_data(self, company_name: str, linkedin_url: str = None, website_url: str = None) -> dict:
        """Scrape complete company data using mixed strategy"""
        
        result = {
            'company_name': company_name,
            'company_size': None,
            'industry': None,
            'revenue': None,
            'linkedin_status': 'Not Attempted',
            'revenue_status': 'Not Attempted',
            'revenue_source': None,
            'revenue_source_url': None
        }
        
        # 1. Try LinkedIn data first
        if linkedin_url:
            try:
                logger.info(f"Getting LinkedIn data for {company_name}")
                
                company_size = self.linkedin_scraper.extract_company_size(linkedin_url)
                industry = self.linkedin_scraper.extract_industry(linkedin_url)
                
                if company_size and company_size not in ['Invalid URL', 'Blocked by LinkedIn', 'Rate Limited']:
                    result['company_size'] = company_size
                    result['linkedin_status'] = 'Success'
                else:
                    result['linkedin_status'] = company_size or 'Failed'
                
                if industry and industry not in ['Invalid URL', 'Blocked by LinkedIn', 'Rate Limited']:
                    result['industry'] = industry
                
                # Add delay after LinkedIn
                time.sleep(random.uniform(2, 4))
                
            except Exception as e:
                logger.error(f"LinkedIn scraping failed: {str(e)}")
                result['linkedin_status'] = f'Error: {str(e)}'
        
        # 2. Try revenue from multiple sources
        if website_url:
            # 2a. Check manual data first
            manual_result = self.get_manual_revenue(company_name, website_url)
            if manual_result:
                result['revenue'] = manual_result['revenue']
                result['revenue_status'] = manual_result['status']
                result['revenue_source'] = manual_result['source']
                result['revenue_source_url'] = manual_result['source_url']
                logger.info(f"✓ Using manual revenue data for {company_name}: {manual_result['revenue']}")
            else:
                # 2b. Try alternative sources
                try:
                    logger.info(f"Searching alternative sources for revenue: {company_name}")
                    alt_result = self.alternative_scraper.get_comprehensive_revenue(company_name, website_url)
                    
                    result['revenue'] = alt_result['revenue']
                    result['revenue_status'] = alt_result['status']
                    result['revenue_source'] = alt_result['source']
                    result['revenue_source_url'] = alt_result['source_url']
                    
                    # Add delay after revenue search
                    time.sleep(random.uniform(3, 6))
                    
                except Exception as e:
                    logger.error(f"Alternative revenue search failed: {str(e)}")
                    result['revenue_status'] = f'Error: {str(e)}'
        
        return result

def process_excel_with_mixed_strategy(input_file: str,
                                     company_column: str = 'Company Name',
                                     linkedin_column: str = 'LinkedIn_URL', 
                                     website_column: str = 'Company Website',
                                     output_file: str = None):
    """Process Excel file with mixed strategy approach"""
    
    # Read input file
    df = pd.read_excel(input_file)
    logger.info(f"Processing {len(df)} companies with Mixed Strategy approach")
    
    # Prepare output file
    if not output_file:
        output_file = input_file.replace('.xlsx', '_mixed_strategy_results.xlsx')
    
    # Initialize scraper
    scraper = MixedStrategyRevenueScraper()
    
    # Add result columns
    new_columns = [
        'Company_Size_Mixed', 'Industry_Mixed', 'Revenue_Mixed',
        'LinkedIn_Status_Mixed', 'Revenue_Status_Mixed', 
        'Revenue_Source_Mixed', 'Revenue_Source_URL_Mixed'
    ]
    
    for col in new_columns:
        if col not in df.columns:
            df[col] = None
    
    # Track statistics
    stats = {
        'processed': 0,
        'linkedin_success': 0,
        'revenue_success': 0,
        'manual_revenue': 0,
        'alternative_revenue': 0
    }
    
    print("\nProcessing with Mixed Strategy Approach")
    print("=" * 50)
    
    for index, row in df.iterrows():
        company_name = row.get(company_column)
        linkedin_url = row.get(linkedin_column) if linkedin_column in df.columns else None
        website_url = row.get(website_column) if website_column in df.columns else None
        
        if pd.isna(company_name):
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing: {company_name}")
        if not pd.isna(linkedin_url):
            print(f"LinkedIn: {linkedin_url}")
        if not pd.isna(website_url):
            print(f"Website: {website_url}")
        print(f"{'='*60}")
        
        # Scrape complete data
        result = scraper.scrape_complete_company_data(
            company_name=str(company_name),
            linkedin_url=str(linkedin_url) if not pd.isna(linkedin_url) else None,
            website_url=str(website_url) if not pd.isna(website_url) else None
        )
        
        # Update DataFrame
        df.at[index, 'Company_Size_Mixed'] = result['company_size']
        df.at[index, 'Industry_Mixed'] = result['industry']
        df.at[index, 'Revenue_Mixed'] = result['revenue']
        df.at[index, 'LinkedIn_Status_Mixed'] = result['linkedin_status']
        df.at[index, 'Revenue_Status_Mixed'] = result['revenue_status']
        df.at[index, 'Revenue_Source_Mixed'] = result['revenue_source']
        df.at[index, 'Revenue_Source_URL_Mixed'] = result['revenue_source_url']
        
        # Update statistics
        stats['processed'] += 1
        if result['company_size'] or result['industry']:
            stats['linkedin_success'] += 1
        if result['revenue']:
            stats['revenue_success'] += 1
            if 'Manual' in result['revenue_source']:
                stats['manual_revenue'] += 1
            else:
                stats['alternative_revenue'] += 1
        
        # Print results
        print(f"\nRESULTS:")
        print(f"LinkedIn Status: {result['linkedin_status']}")
        if result['company_size']:
            print(f"Company Size: {result['company_size']}")
        if result['industry']:
            print(f"Industry: {result['industry']}")
        print(f"Revenue Status: {result['revenue_status']}")
        if result['revenue']:
            print(f"Revenue: {result['revenue']}")
            print(f"Revenue Source: {result['revenue_source']}")
        
        # Save progress
        if stats['processed'] % 2 == 0:
            df.to_excel(output_file, index=False)
            logger.info(f"Progress saved: {stats['processed']} companies processed")
    
    # Save final results
    df.to_excel(output_file, index=False)
    
    # Print final statistics
    print(f"\n{'='*70}")
    print("MIXED STRATEGY SCRAPING RESULTS")
    print(f"{'='*70}")
    print(f"Total companies processed: {stats['processed']}")
    print(f"LinkedIn data found: {stats['linkedin_success']} ({(stats['linkedin_success']/stats['processed']*100):.1f}%)")
    print(f"Revenue data found: {stats['revenue_success']} ({(stats['revenue_success']/stats['processed']*100):.1f}%)")
    print(f"  - Manual revenue data: {stats['manual_revenue']}")
    print(f"  - Alternative sources: {stats['alternative_revenue']}")
    print(f"Results saved to: {output_file}")
    print(f"{'='*70}")
    
    return df

if __name__ == "__main__":
    # Process Test5.xlsx with mixed strategy
    process_excel_with_mixed_strategy('Test5.xlsx')