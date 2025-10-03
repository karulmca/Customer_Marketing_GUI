#!/usr/bin/env python3
"""
Create sample Excel file for LinkedIn Company Scraper
"""

import pandas as pd

# Sample data
data = {
    'Company_Name': [
        'Microsoft',
        'Google',
        'Apple',
        'Amazon',
        'Meta',
        'Tesla',
        'Nike',
        'Coca-Cola',
        'McDonald\'s',
        'IBM'
    ],
    'LinkedIn_URL': [
        'https://www.linkedin.com/company/microsoft/',
        'https://www.linkedin.com/company/google/',
        'https://www.linkedin.com/company/apple/',
        'https://www.linkedin.com/company/amazon/',
        'https://www.linkedin.com/company/meta/',
        'https://www.linkedin.com/company/tesla-motors/',
        'https://www.linkedin.com/company/nike/',
        'https://www.linkedin.com/company/the-coca-cola-company/',
        'https://www.linkedin.com/company/mcdonald-s-corporation/',
        'https://www.linkedin.com/company/ibm/'
    ],
    'Company_Size': [''] * 10,  # Empty column to be filled
    'Industry': [
        'Technology',
        'Technology',
        'Technology',
        'E-commerce',
        'Technology',
        'Automotive',
        'Retail',
        'Beverages',
        'Food Service',
        'Technology'
    ],
    'Location': [
        'Redmond, WA',
        'Mountain View, CA',
        'Cupertino, CA',
        'Seattle, WA',
        'Menlo Park, CA',
        'Austin, TX',
        'Beaverton, OR',
        'Atlanta, GA',
        'Chicago, IL',
        'Armonk, NY'
    ]
}

# Create DataFrame
df = pd.DataFrame(data)

# Save to Excel
df.to_excel('sample_companies.xlsx', index=False, sheet_name='Companies')

print("Sample Excel file 'sample_companies.xlsx' created successfully!")
print(f"Contains {len(df)} sample companies")