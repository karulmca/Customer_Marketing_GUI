#!/usr/bin/env python3
"""
Test Alternative Sources Scraper with Known Public Companies
"""

import pandas as pd
from alternative_sources_scraper import AlternativeDataSourcesScraper

def test_with_public_companies():
    """Test with companies that are known to have publicly available revenue data"""
    
    # Create test data with well-known public companies
    test_data = [
        {
            'Company Name': 'Apple Inc.',
            'Company Website': 'https://www.apple.com'
        },
        {
            'Company Name': 'Microsoft Corporation',
            'Company Website': 'https://www.microsoft.com'
        },
        {
            'Company Name': 'Amazon.com Inc.',
            'Company Website': 'https://www.amazon.com'
        },
        {
            'Company Name': 'Alphabet Inc.',
            'Company Website': 'https://www.google.com'
        },
        {
            'Company Name': 'Tesla Inc.',
            'Company Website': 'https://www.tesla.com'
        }
    ]
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Save as Excel for testing
    test_file = 'test_public_companies.xlsx'
    df.to_excel(test_file, index=False)
    
    print(f"Created test file: {test_file}")
    
    # Initialize scraper
    scraper = AlternativeDataSourcesScraper()
    
    # Add result columns
    df['Revenue_Alternative'] = None
    df['Alternative_Source'] = None
    df['Alternative_Source_URL'] = None
    df['Alternative_Status'] = None
    
    print("\nTesting Alternative Sources Scraper with Public Companies")
    print("=" * 65)
    
    for index, row in df.iterrows():
        company_name = row['Company Name']
        website_url = row['Company Website']
        
        print(f"\n{'='*60}")
        print(f"Processing: {company_name}")
        print(f"Website: {website_url}")
        print(f"{'='*60}")
        
        # Get revenue from alternative sources
        result = scraper.get_comprehensive_revenue(company_name, website_url)
        
        # Update dataframe
        df.at[index, 'Revenue_Alternative'] = result['revenue']
        df.at[index, 'Alternative_Source'] = result['source']
        df.at[index, 'Alternative_Source_URL'] = result['source_url']
        df.at[index, 'Alternative_Status'] = result['status']
        
        print(f"\nFINAL RESULT:")
        print(f"Status: {result['status']}")
        if result['revenue']:
            print(f"Revenue: {result['revenue']}")
            print(f"Source: {result['source']}")
        print(f"{'='*60}")
        
        # Only test first 2 companies to save time
        if index >= 1:
            break
    
    # Save results
    output_file = 'test_public_companies_results.xlsx'
    df.to_excel(output_file, index=False)
    
    # Print summary
    success_count = df['Revenue_Alternative'].notna().sum()
    total_count = len(df)
    
    print(f"\n{'='*65}")
    print("PUBLIC COMPANIES TEST RESULTS")
    print(f"{'='*65}")
    print(f"Companies tested: {total_count}")
    print(f"Revenue data found: {success_count}")
    if total_count > 0:
        print(f"Success rate: {(success_count/total_count)*100:.1f}%")
    print(f"Results saved to: {output_file}")
    print(f"{'='*65}")
    
    # Show results table
    print("\nDetailed Results:")
    print(df[['Company Name', 'Revenue_Alternative', 'Alternative_Source', 'Alternative_Status']].to_string())
    
    return df

if __name__ == "__main__":
    test_with_public_companies()