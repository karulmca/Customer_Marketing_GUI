# Company Data Upload Template Guide

## Required Columns

Your Excel/CSV file must contain these exact column names:

### ✅ Required Columns
- **Company Name**: Full company name (e.g., "Acme Corporation")
- **Company Linkedin**: LinkedIn company URL (e.g., "https://www.linkedin.com/company/acme")

### ⚡ Optional Columns (Enhanced Automatically)
- **Website**: Company website URL
- **Size**: Current company size (will be enhanced with LinkedIn data)
- **Revenue**: Current revenue info (will be enhanced with scraped data)
- **Zoominfo ID**: Optional identifier for tracking

## Sample Data Format

```csv
Company Name,Size,Revenue,Website,Company Linkedin,Zoominfo ID
Acme Corporation,51-200 employees,$5M,https://www.acme.com,https://www.linkedin.com/company/acme-corp,12345
Tech Solutions Ltd,11-50 employees,$2M,https://www.techsolutions.com,https://www.linkedin.com/company/tech-solutions,67890
```

## What Happens During Processing

1. **File Upload**: Your file is stored as JSON in the database
2. **LinkedIn Scraping**: System automatically extracts:
   - Accurate company size
   - Industry information
   - Company description
   - Additional company details
3. **Data Enhancement**: Your original data is enhanced with scraped information
4. **Database Storage**: All processed data is saved for future reference

## Column Name Flexibility

The system supports both naming conventions:
- `Company Name` or `Company_Name`
- `Company Linkedin` or `LinkedIn_URL`
- `Website` or `Company_Website`

## Tips for Best Results

- Ensure LinkedIn URLs are complete and valid
- Use the exact column names from the template
- Keep company names consistent and accurate
- Include website URLs when available for additional data sources

## Download Sample Template

Use the "Download Sample Template" button in the UI to get a properly formatted Excel file with sample data.