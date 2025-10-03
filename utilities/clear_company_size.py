import pandas as pd
import sys

def clear_company_size_column(filename):
    """Clear the Company_Size column to allow re-processing"""
    try:
        # Read the Excel file
        df = pd.read_excel(filename)
        
        # Check if Company_Size column exists
        if 'Company_Size' in df.columns:
            # Clear the Company_Size column
            df['Company_Size'] = ''
            
            # Save to a new file
            new_filename = filename.replace('.xlsx', '_cleared.xlsx')
            df.to_excel(new_filename, index=False)
            
            print(f"✅ Created {new_filename} with empty Company_Size column")
            print(f"📊 Found {len(df)} rows in the file")
            
            # Show first few company names to verify
            if 'Company_Name' in df.columns:
                print(f"🏢 Companies found: {', '.join(df['Company_Name'].head(3).tolist())}...")
            elif 'LinkedIn_URL' in df.columns:
                print(f"🔗 LinkedIn URLs found: {len(df)} URLs")
            
            return new_filename
        else:
            print("❌ No Company_Size column found in the file")
            return None
            
    except Exception as e:
        print(f"❌ Error processing file: {str(e)}")
        return None

if __name__ == '__main__':
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        clear_company_size_column(filename)
    else:
        # Default to Test4.xlsx
        filename = 'Test4.xlsx'
        print(f"🔄 Clearing Company_Size column in {filename}...")
        result = clear_company_size_column(filename)
        
        if result:
            print(f"✨ Now you can re-run the scraper on: {result}")
        else:
            print("💡 Make sure the Excel file exists and has the correct format")