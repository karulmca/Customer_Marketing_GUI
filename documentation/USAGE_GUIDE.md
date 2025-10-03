# LinkedIn Company Size Scraper - Usage Guide

## Quick Start

1. **Setup** (First time only):
   ```cmd
   .\setup.bat
   ```
   Note: In PowerShell, use `.\` prefix for batch files in current directory

2. **Run with GUI** (Easy method):
   ```cmd
   .\run_gui.bat
   ```
   
   **Enhanced GUI** (Company Size + Industry):
   ```cmd
   .\run_enhanced_gui.bat
   ```
   
   **Alternative GUI** (Company Size only):
   ```cmd
   .\run_gui_optimized.bat
   ```

3. **Run with Batch File** (Command line):
   ```cmd
   .\run_linkedin_scraper.bat "your_companies.xlsx"
   ```

## Detailed Instructions

### Method 1: Using the Enhanced GUI (Recommended - extracts Size + Industry)

1. Double-click `run_enhanced_gui.bat`
2. Click "Browse" to select your Excel file
3. Verify column names (LinkedIn_URL, Company_Size, Industry)
4. Click "Start Scraping"
5. Monitor progress in the log window
6. Get both Company Size AND Industry extracted automatically!

### Method 1b: Using the Basic GUI (Company Size only)

1. Double-click `run_gui.bat`
2. Click "Browse" to select your Excel file
3. Verify column names (LinkedIn_URL, Company_Size)
4. Click "Start Scraping"
5. Monitor progress in the log window

### Method 2: Using Batch File

1. Prepare your Excel file with LinkedIn URLs
2. Run: `.\run_linkedin_scraper.bat "path\to\your\file.xlsx"`
3. Follow the prompts
4. Check the results in your Excel file

**Note**: In PowerShell, use `.\` prefix for batch files in current directory

### Method 3: Using Python Directly

```cmd
python linkedin_company_scraper.py "companies.xlsx" --url-column "LinkedIn_URL" --size-column "Company_Size"
```

## Excel File Requirements

Your Excel file must have:
- **LinkedIn URL Column**: Contains company LinkedIn URLs
- **Company Size Column**: Will be filled with extracted sizes (can be empty initially)
- **Industry Column**: Will be filled with extracted industries (optional, can be empty initially)

Example format for Enhanced version:
| Company_Name | LinkedIn_URL | Company_Size | Industry |
|--------------|--------------|--------------|----------|
| Microsoft | https://www.linkedin.com/company/microsoft/ | | |
| Google | https://www.linkedin.com/company/google/ | | |

Example format for Basic version:
| Company_Name | LinkedIn_URL | Company_Size |
|--------------|--------------|--------------|
| Microsoft | https://www.linkedin.com/company/microsoft/ | |
| Google | https://www.linkedin.com/company/google/ | |

## Configuration

Edit `config.json` to customize:
- Delay between requests (to avoid being blocked)
- Column names defaults
- Scraping patterns and selectors

## Files Overview

- `linkedin_company_scraper.py` - Main scraper script
- `linkedin_scraper_gui.py` - GUI version
- `run_linkedin_scraper.bat` - Command line batch file
- `run_gui.bat` - Run GUI version
- `setup.bat` - Install dependencies and create sample files
- `config.json` - Configuration settings
- `requirements.txt` - Python package requirements
- `sample_companies.xlsx` - Sample Excel file (created by setup)

## Troubleshooting

### "Python not found"
- Install Python 3.7+ from python.org
- Make sure "Add Python to PATH" is checked during installation
- Run `setup.bat`

### "Column not found"
- Check column names in your Excel file
- Verify they match the names you specified
- Column names are case-sensitive

### "Not Found" results
- LinkedIn may have changed their page structure
- Some companies don't display size information
- Try different LinkedIn URLs for the same company

### Rate limiting / Blocked
- The script includes delays to avoid this
- If blocked, wait and try again later
- Consider increasing delays in config.json

### GUI not working
- If `run_gui.bat` fails, try `run_gui_optimized.bat`
- Make sure all packages are installed: `pip install pandas requests beautifulsoup4 openpyxl tkinter`
- The optimized GUI extracts exact LinkedIn ranges like "201-500 employees"

## Best Practices

1. **Start Small**: Test with 5-10 companies first
2. **Backup Files**: Script creates backups, but keep your own
3. **Valid URLs**: Ensure LinkedIn URLs are correct and accessible
4. **Monitor Logs**: Watch for errors and warnings
5. **Respect Limits**: Don't run multiple instances simultaneously

## Output Examples

### Enhanced Version (Company Size + Industry):

Successful extractions:
- Company Size: `"201-500 employees"`, Industry: `"Financial Services"`
- Company Size: `"10,001+ employees"`, Industry: `"Technology"`  
- Company Size: `"51-200 employees"`, Industry: `"Healthcare"`
- Company Size: `"11-50 employees"`, Industry: `"Consulting"`

### Basic Version (Company Size only):

Successful extractions:
- `"10,001+ employees"`
- `"1,001-5,000 employees"`
- `"51-200 employees"`
- `"11-50 employees"`

### Failed extractions:
- `"Not Found"` - Could not extract information
- `"Blocked by LinkedIn"` - Request was blocked

## Legal Notice

This tool is for educational and research purposes. Please:
- Respect LinkedIn's Terms of Service
- Use reasonable delays between requests
- Consider data protection regulations
- Don't abuse the service

## Support

1. Check `linkedin_scraper.log` for detailed errors
2. Verify Excel file format with `sample_companies.xlsx`
3. Test with sample file first
4. Ensure all dependencies are installed via `setup.bat`