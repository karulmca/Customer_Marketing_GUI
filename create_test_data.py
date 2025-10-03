import pandas as pd
import os

# Create test data for the JSON upload system
test_companies = [
    {
        'Company Name': 'Microsoft Corporation',
        'LinkedIn URL': 'https://www.linkedin.com/company/microsoft/',
        'Company Website': 'https://www.microsoft.com',
        'Industry': 'Technology',
        'Company Size': '10001+ employees',
        'Revenue': '$200B+'
    },
    {
        'Company Name': 'Apple Inc.',
        'LinkedIn URL': 'https://www.linkedin.com/company/apple/',
        'Company Website': 'https://www.apple.com',
        'Industry': 'Technology',
        'Company Size': '10001+ employees',
        'Revenue': '$350B+'
    },
    {
        'Company Name': 'Google LLC',
        'LinkedIn URL': 'https://www.linkedin.com/company/google/',
        'Company Website': 'https://www.google.com',
        'Industry': 'Technology',
        'Company Size': '10001+ employees',
        'Revenue': '$280B+'
    },
    {
        'Company Name': 'Amazon.com Inc.',
        'LinkedIn URL': 'https://www.linkedin.com/company/amazon/',
        'Company Website': 'https://www.amazon.com',
        'Industry': 'E-commerce',
        'Company Size': '10001+ employees',
        'Revenue': '$470B+'
    },
    {
        'Company Name': 'Tesla Inc.',
        'LinkedIn URL': 'https://www.linkedin.com/company/tesla-motors/',
        'Company Website': 'https://www.tesla.com',
        'Industry': 'Automotive',
        'Company Size': '5001-10000 employees',
        'Revenue': '$96B+'
    }
]

# Create DataFrame and save as Excel file
df = pd.DataFrame(test_companies)

# Ensure test_data directory exists
os.makedirs('test_data', exist_ok=True)

# Save test file
test_file = 'test_data/json_upload_test.xlsx'
df.to_excel(test_file, index=False)

print(f"✅ Test file created: {test_file}")
print(f"📊 Contains {len(test_companies)} test companies")
print("\n🎯 Next Steps:")
print("1. Run: .\\batch_files\\run_json_upload_gui.bat")
print(f"2. Upload: {test_file}")
print("3. Run: .\\batch_files\\run_scheduled_processor.bat")
print("4. Check results in the GUI!")

# Show the test data structure
print(f"\n📋 Test Data Structure:")
print(df.to_string(index=False))