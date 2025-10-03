# LinkedIn Company Size Scraper

This batch process extracts company size information from LinkedIn company pages and updates an Excel file with the results.

## Features

- **Automated Excel Processing**: Reads LinkedIn URLs from Excel and updates company sizes
- **Multiple Scraping Strategies**: Uses various methods to find company size information
- **Progress Tracking**: Logs progress and saves periodically
- **Error Handling**: Robust error handling with detailed logging
- **Backup Creation**: Automatically creates backup of input file
- **Rate Limiting**: Includes delays to avoid being blocked by LinkedIn

## Requirements

- Python 3.7 or higher
- Required Python packages (automatically installed):
  - pandas
  - requests
  - beautifulsoup4
  - openpyxl
  - lxml

## File Structure

```
batch/
├── linkedin_company_scraper.py          # Original LinkedIn scraper
├── linkedin_company_scraper_enhanced.py # Enhanced LinkedIn scraper
├── company_website_scraper.py           # Company website scraper (recommended)
├── linkedin_scraper_gui.py              # GUI interface
├── run_linkedin_scraper.bat             # Run original scraper
├── run_enhanced_scraper.bat             # Run enhanced LinkedIn scraper  
├── run_website_scraper.bat              # Run website scraper (highest success)
├── run_gui.bat                          # Launch GUI
├── setup.bat                            # Setup and install dependencies
├── sample_companies.xlsx                # Sample Excel template
├── config.json                          # Configuration file
├── requirements.txt                     # Python dependencies
├── README.md                            # This file
├── USAGE_GUIDE.md                       # Usage instructions
└── LINKEDIN_LIMITATIONS.md              # Important LinkedIn limitations info
```

## Usage

### Method 1: Using Batch File (Recommended)

1. Double-click `run_linkedin_scraper.bat`
2. Follow the prompts to specify your Excel file and column names

Or run from command line:
```cmd
run_linkedin_scraper.bat "your_companies.xlsx"
```

With custom column names:
```cmd
run_linkedin_scraper.bat "companies.xlsx" "LinkedIn_URL" "Company_Size" "output.xlsx"
```

### Method 2: Using Python Directly

```cmd
python linkedin_company_scraper.py "companies.xlsx" --url-column "LinkedIn_URL" --size-column "Company_Size"
```

## Excel File Format

Your Excel file should have at least one column containing LinkedIn company URLs. For example:

| Company_Name | LinkedIn_URL | Company_Size |
|--------------|--------------|--------------|
| Microsoft | https://www.linkedin.com/company/microsoft/ | |
| Google | https://www.linkedin.com/company/google/ | |
| Apple | https://www.linkedin.com/company/apple/ | |

### Column Requirements:
- **LinkedIn URL Column**: Must contain valid LinkedIn company page URLs
- **Company Size Column**: Will be created/updated with extracted company sizes

## Configuration

Edit `config.json` to customize scraping behavior:

```json
{
    "delay_range": [2, 5],
    "timeout": 30,
    "max_retries": 3,
    "default_columns": {
        "url_column": "LinkedIn_URL",
        "size_column": "Company_Size"
    }
}
```

## Output

The script will:
1. Create a backup of your original Excel file
2. Update the Excel file with company sizes
3. Generate a detailed log file (`linkedin_scraper.log`)
4. Display progress in the console

### Possible Company Size Values:
- `"10,001+ employees"`
- `"1,001-5,000 employees"`
- `"51-200 employees"`
- `"Not Found"` (if company size couldn't be extracted)

## Troubleshooting

### Common Issues:

1. **"Column not found" error**
   - Ensure your Excel file has the correct column names
   - Check for typos in column names

2. **"Not Found" results**
   - LinkedIn may have changed their page structure
   - Some company pages may not display size information
   - Company page might be private or restricted

3. **Rate limiting**
   - The script includes delays to avoid being blocked
   - If you get blocked, wait and try again later
   - Consider increasing delay in config.json

4. **Installation errors**
   - Ensure Python is installed and in PATH
   - Run as administrator if package installation fails

### Log Files:
- Check `linkedin_scraper.log` for detailed error messages
- Log includes timestamps and specific error details

## Best Practices

1. **Test with Small Files**: Start with a few URLs to test the process
2. **Regular Backups**: The script creates backups, but maintain your own as well
3. **Respect Rate Limits**: Don't run multiple instances simultaneously
4. **Valid URLs**: Ensure LinkedIn URLs are correctly formatted
5. **Monitor Progress**: Watch the console output and log files

## Legal Considerations

- This tool is for educational and research purposes
- Respect LinkedIn's Terms of Service and robots.txt
- Consider rate limiting and respectful scraping practices
- Ensure compliance with data protection regulations

## Support

For issues or questions:
1. Check the log file for error details
2. Verify your Excel file format
3. Ensure all requirements are installed
4. Test with the sample Excel file provided