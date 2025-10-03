@echo off
echo ===============================================
echo    Enhanced LinkedIn Scraper - Size + Industry
echo ===============================================
echo.
echo This version extracts BOTH Company Size AND Industry:
echo • Company Size: "1-10", "11-50", "201-500 employees"
echo • Industry: "Financial Services", "Technology", etc.
echo.
echo Uses advanced pattern matching for maximum accuracy!
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause

python linkedin_data_scraper.py "%1" --url-column "LinkedIn_URL" --size-column "Company_Size" --industry-column "Industry" --output-file "%~n1_enhanced_results.xlsx"

echo.
echo ===============================================
echo Processing complete! Check the enhanced results file.
echo Both Company Size and Industry have been extracted.
echo ===============================================
pause