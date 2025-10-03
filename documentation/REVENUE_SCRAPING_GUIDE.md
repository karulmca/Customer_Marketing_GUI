# Revenue Scraping Guide

## Overview
This guide explains how to use the revenue scraping functionality to extract company revenue data based on website URLs. The system provides multiple approaches to find revenue information from various sources.

## Available Scripts

### 1. ZoomInfo Revenue Scraper (`zoominfo_revenue_scraper.py`)
- **Purpose**: Scrapes revenue data specifically from ZoomInfo
- **Input**: Company name and website URL
- **Output**: Revenue data with source information

### 2. Integrated Company Scraper (`integrated_company_scraper.py`)
- **Purpose**: Combines LinkedIn data (size, industry) with revenue data from multiple sources
- **Input**: Company name, LinkedIn URL, and website URL
- **Output**: Complete company profile including size, industry, and revenue

### 3. Multi-Source Revenue Scraper (part of integrated scraper)
- **Purpose**: Searches multiple sources for revenue data
- **Sources**: Company website, ZoomInfo, Crunchbase, and others
- **Fallback**: If one source fails, tries the next

## Quick Start

### Option 1: Revenue Only
```bash
# Run standalone revenue scraper
python zoominfo_revenue_scraper.py your_companies.xlsx

# Or use the batch file
run_revenue_scraper.bat your_companies.xlsx
```

### Option 2: Complete Data (LinkedIn + Revenue)
```bash
# Run integrated scraper
python integrated_company_scraper.py your_companies.xlsx

# Or use the batch file
run_integrated_scraper.bat your_companies.xlsx
```

## Required Excel Columns

### For Revenue Scraper:
- `Company_Name`: Name of the company
- `Website_URL`: Company website URL

### For Integrated Scraper:
- `Company_Name`: Name of the company
- `LinkedIn_URL`: LinkedIn company page URL (optional)
- `Website_URL`: Company website URL (optional)

## Output Columns

### Revenue Scraper Adds:
- `Revenue`: Extracted revenue information
- `Revenue_Source`: URL where revenue was found
- `Revenue_Status`: Success/failure status

### Integrated Scraper Adds:
- `Company_Size_Enhanced`: Company size from LinkedIn
- `Industry_Enhanced`: Industry from LinkedIn
- `Revenue_Enhanced`: Revenue from multiple sources
- `Revenue_Source`: Source of revenue data
- `Revenue_Source_URL`: URL where revenue was found
- `LinkedIn_Status`: LinkedIn scraping status
- `Revenue_Status`: Revenue scraping status

## Revenue Sources

The scrapers search for revenue data in the following order:

1. **Company Website**
   - Homepage
   - About/About Us pages
   - Investor Relations pages
   - Press/News sections
   - Financial pages

2. **ZoomInfo**
   - Company profiles
   - Financial information sections

3. **Crunchbase**
   - Company profiles
   - Funding information

## Revenue Pattern Detection

The system recognizes various revenue formats:
- `$50 million`
- `$1.2 billion`
- `100M in revenue`
- `Annual revenue: $500K`
- `€75 million` (European format)
- `Revenue range: $10M - $50M`

## Command Line Options

### Revenue Scraper Options:
```bash
python zoominfo_revenue_scraper.py input_file.xlsx [OPTIONS]

Options:
  --website-column NAME     Column with website URLs (default: Website_URL)
  --company-column NAME     Column with company names (default: Company_Name)
  --revenue-column NAME     Column to store revenue (default: Revenue)
  --output-file PATH        Output file path (optional)
  --wait-min SECONDS        Minimum wait time (default: 15)
  --wait-max SECONDS        Maximum wait time (default: 30)
```

### Integrated Scraper Options:
```bash
python integrated_company_scraper.py input_file.xlsx [OPTIONS]

Options:
  --company-column NAME     Column with company names (default: Company_Name)
  --linkedin-column NAME    Column with LinkedIn URLs (default: LinkedIn_URL)
  --website-column NAME     Column with website URLs (default: Website_URL)
  --output-file PATH        Output file path (optional)
  --wait-min SECONDS        Minimum wait time (default: 15)
  --wait-max SECONDS        Maximum wait time (default: 30)
```

## Testing

### Create Test File:
```bash
python test_revenue_scraper.py --create-test
```

### Run Functionality Test:
```bash
python test_revenue_scraper.py
```

## Example Usage

### 1. Basic Revenue Scraping:
```bash
# Scrape revenue for companies in sample_companies.xlsx
python zoominfo_revenue_scraper.py sample_companies.xlsx
```

### 2. Custom Column Names:
```bash
# If your Excel has different column names
python zoominfo_revenue_scraper.py companies.xlsx \
  --company-column "Business_Name" \
  --website-column "Company_Website" \
  --revenue-column "Annual_Revenue"
```

### 3. Integrated Scraping:
```bash
# Get both LinkedIn and revenue data
python integrated_company_scraper.py companies.xlsx \
  --wait-min 10 \
  --wait-max 20
```

### 4. Custom Output File:
```bash
# Specify output file name
python integrated_company_scraper.py input.xlsx \
  --output-file "complete_company_data.xlsx"
```

## Best Practices

### 1. Rate Limiting
- Use appropriate wait times (15-30 seconds recommended)
- The system automatically adds random delays
- Longer waits reduce the chance of being blocked

### 2. Data Quality
- Ensure website URLs are complete and valid
- Clean company names improve search accuracy
- Remove duplicates before processing

### 3. Monitoring
- Check log files for errors and progress
- Use the save interval feature for large datasets
- Monitor success rates and adjust if needed

### 4. Error Handling
- The system handles common errors gracefully
- Failed attempts are marked with status codes
- Processing continues even if individual companies fail

## Troubleshooting

### Common Issues:

1. **No Revenue Found**
   - Company might not publish revenue publicly
   - Revenue might be in non-standard format
   - Check if website URL is accessible

2. **Rate Limiting**
   - Increase wait times between requests
   - Some sites block automated access
   - Consider running during off-peak hours

3. **Missing Columns**
   - Verify Excel column names match expected names
   - Use command line options to specify custom column names

4. **Network Errors**
   - Check internet connection
   - Some sites might be temporarily unavailable
   - The system will retry failed requests

### Log Files:
- `zoominfo_revenue_scraper.log`: Revenue scraper logs
- `integrated_company_scraper.log`: Integrated scraper logs

## Performance Tips

1. **Batch Processing**: Process companies in smaller batches for better control
2. **Resume Capability**: The system can resume from where it left off
3. **Parallel Processing**: Consider running multiple instances for different company sets
4. **Caching**: Results are saved periodically to prevent data loss

## Legal and Ethical Considerations

1. **Respect robots.txt**: The scrapers respect website policies
2. **Rate Limiting**: Built-in delays prevent server overload
3. **Public Data Only**: Only scrapes publicly available information
4. **Terms of Service**: Ensure compliance with website terms of service
5. **Data Privacy**: Handle scraped data according to privacy regulations

## Integration with Existing Workflow

The revenue scrapers are designed to work alongside your existing LinkedIn scrapers:

1. **Sequential Processing**: Run LinkedIn scraper first, then revenue scraper
2. **Integrated Processing**: Use the integrated scraper for both LinkedIn and revenue data
3. **Data Merging**: Results can be merged with existing company data

## Support and Updates

For issues or feature requests:
1. Check the log files for detailed error information
2. Verify your Excel file format and column names
3. Test with a small sample before processing large datasets
4. Consider adjusting wait times if encountering rate limits

The system is designed to be robust and handle various edge cases, but website structures change frequently, so periodic updates may be needed.