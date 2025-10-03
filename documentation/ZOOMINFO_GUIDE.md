# ZoomInfo Revenue Scraper Guide

## Overview

The ZoomInfo Revenue Scraper extracts company revenue data from ZoomInfo based on company website URLs. It provides multiple approaches to find and extract revenue information from ZoomInfo company profiles.

## Features

- **Direct ZoomInfo URL Construction**: Attempts to build ZoomInfo URLs directly from domain names
- **Google Search Integration**: Uses Google search to find ZoomInfo company pages
- **Enhanced Revenue Pattern Detection**: Recognizes various revenue formats and patterns
- **Stealth Browsing**: Rotates user agents and headers to avoid detection
- **Error Handling**: Comprehensive error handling and retry mechanisms
- **Progress Tracking**: Saves progress periodically and provides detailed logging

## Quick Start

### Option 1: ZoomInfo Revenue Only
```bash
# Use the batch file (recommended)
run_zoominfo_revenue_scraper.bat your_companies.xlsx

# Or run Python directly
python zoominfo_revenue_scraper.py your_companies.xlsx
```

### Option 2: Complete Data (LinkedIn + ZoomInfo Revenue)
```bash
# Use the complete scraper batch file
run_complete_scraper.bat your_companies.xlsx

# Or run Python directly
python complete_company_scraper.py your_companies.xlsx
```

## Required Excel Format

Your input Excel file must contain these columns:

### For ZoomInfo Revenue Only:
- `Company_Name`: Name of the company (required)
- `Website_URL`: Company website URL (required)

### For Complete Scraper:
- `Company_Name`: Name of the company (required)
- `LinkedIn_URL`: LinkedIn company page URL (optional)
- `Website_URL`: Company website URL (optional)

## Output Columns

### ZoomInfo Revenue Scraper Adds:
- `Revenue`: Extracted revenue information
- `Revenue_Source`: Always "ZoomInfo" 
- `Revenue_Source_URL`: URL of the ZoomInfo page where revenue was found
- `Revenue_Status`: Status of the scraping attempt

### Complete Scraper Adds:
- `Company_Size_Complete`: Company size from LinkedIn
- `Industry_Complete`: Industry from LinkedIn  
- `Revenue_Complete`: Revenue from ZoomInfo
- `LinkedIn_Status_Complete`: LinkedIn scraping status
- `Revenue_Status_Complete`: ZoomInfo scraping status
- `LinkedIn_Source_URL`: Original LinkedIn URL
- `Revenue_Source_URL`: ZoomInfo URL where revenue was found

## Revenue Pattern Detection

The scraper recognizes various revenue formats:

- **Standard Formats**: `$50 million`, `$1.2 billion`, `100M in revenue`
- **Annual Revenue**: `Annual revenue: $500K`, `2023 revenue: $75M`
- **Revenue Ranges**: `$10M - $50M`, `Between $5M and $25M`
- **European Formats**: `€75 million`, `£100 million`
- **Context-Based**: `Generates approximately $50M`, `Estimated revenue $25M`

## Command Line Options

### ZoomInfo Revenue Scraper
```bash
python zoominfo_revenue_scraper.py input_file.xlsx [OPTIONS]

Options:
  --company-column TEXT     Column name for company names (default: Company_Name)
  --website-column TEXT     Column name for website URLs (default: Website_URL)
  --output-file TEXT        Output Excel file path (optional)
  --wait-min INTEGER        Minimum wait time between requests in seconds (default: 5)
  --wait-max INTEGER        Maximum wait time between requests in seconds (default: 10)
```

### Complete Company Scraper
```bash
python complete_company_scraper.py input_file.xlsx [OPTIONS]

Options:
  --company-column TEXT     Column name for company names (default: Company_Name)
  --linkedin-column TEXT    Column name for LinkedIn URLs (default: LinkedIn_URL)
  --website-column TEXT     Column name for website URLs (default: Website_URL)
  --output-file TEXT        Output Excel file path (optional)
  --wait-min INTEGER        Minimum wait time between companies in seconds (default: 10)
  --wait-max INTEGER        Maximum wait time between companies in seconds (default: 20)
```

## Examples

### Basic Usage
```bash
# ZoomInfo revenue only
run_zoominfo_revenue_scraper.bat companies.xlsx

# Complete data (LinkedIn + ZoomInfo)
run_complete_scraper.bat companies.xlsx
```

### Custom Column Names
```bash
# If your Excel has different column names
python zoominfo_revenue_scraper.py companies.xlsx \
  --company-column "Company Name" \
  --website-column "Website"
```

### Faster Processing (with caution)
```bash
# Reduce wait times (may increase blocking risk)
python zoominfo_revenue_scraper.py companies.xlsx \
  --wait-min 2 \
  --wait-max 5
```

### Custom Output File
```bash
python zoominfo_revenue_scraper.py companies.xlsx \
  --output-file "results_with_revenue.xlsx"
```

## How It Works

### ZoomInfo Search Strategy

1. **Direct URL Construction**: Attempts to build ZoomInfo URLs using the pattern `https://www.zoominfo.com/c/domain-name`

2. **Google Search**: Searches Google for ZoomInfo pages using queries like:
   - `"Company Name" site:zoominfo.com`
   - `"domain.com" site:zoominfo.com`
   - `Company Name revenue site:zoominfo.com`

3. **Content Extraction**: Once ZoomInfo pages are found, extracts revenue data using multiple methods:
   - Structured data sections
   - General content scanning
   - Specific ZoomInfo data elements

### Anti-Detection Features

- **User Agent Rotation**: Uses multiple realistic browser user agents
- **Random Delays**: Implements random wait times between requests
- **Session Management**: Creates fresh sessions to avoid tracking
- **Header Randomization**: Varies HTTP headers for more realistic browsing
- **Referrer Simulation**: Adds realistic referrer headers

## Testing

### Test with Sample Companies
```bash
# Create a test file and run basic tests
python test_zoominfo_scraper.py --create-test-file
python test_zoominfo_scraper.py --test-single
```

### Manual Testing
```bash
# Test individual companies
python -c "
from zoominfo_revenue_scraper import ZoomInfoRevenueScraper
scraper = ZoomInfoRevenueScraper()
result = scraper.get_revenue_from_zoominfo('Microsoft', 'https://www.microsoft.com')
print(result)
"
```

## Troubleshooting

### Common Issues

1. **"No ZoomInfo pages found"**
   - Try variations of the company name
   - Check if the website URL is correct
   - Some companies may not have ZoomInfo profiles

2. **"Rate Limited" or "Blocked"**
   - Increase wait times: `--wait-min 10 --wait-max 20`
   - Use a VPN or different IP address
   - Wait before retrying

3. **"Revenue not found in ZoomInfo pages"**
   - ZoomInfo may have the company but not revenue data
   - Revenue data might be behind a paywall
   - Try the complete scraper which checks multiple sources

### Log Files

Check these log files for detailed information:
- `zoominfo_revenue_scraper.log`: ZoomInfo scraper logs
- `complete_company_scraper.log`: Complete scraper logs

### Performance Tips

1. **Optimal Wait Times**: 5-10 seconds for ZoomInfo only, 10-20 seconds for complete scraping
2. **Batch Size**: Process 20-50 companies at a time for best results
3. **Peak Hours**: Avoid peak business hours for better success rates

## Success Rates

Typical success rates depend on several factors:

- **ZoomInfo Coverage**: ~30-60% of companies have ZoomInfo profiles
- **Revenue Data Availability**: ~40-70% of ZoomInfo profiles contain revenue data
- **Overall Success Rate**: ~20-40% for finding revenue data from ZoomInfo

## Integration with LinkedIn Scraper

The complete scraper combines:
- **LinkedIn Data**: Company size, industry information
- **ZoomInfo Data**: Revenue information
- **Comprehensive Results**: All data in one output file

Use `run_complete_scraper.bat` for the best overall results.

## Legal and Ethical Considerations

- **Respect robots.txt**: The scraper respects website policies
- **Rate Limiting**: Built-in delays prevent server overload
- **Data Usage**: Use scraped data responsibly and in compliance with terms of service
- **Commercial Use**: Ensure compliance with ZoomInfo's terms of service for commercial usage

## Support

For issues or questions:
1. Check the log files for error details
2. Try the test scripts to isolate problems
3. Adjust wait times and retry mechanisms
4. Consider using the integrated scraper for multiple data sources