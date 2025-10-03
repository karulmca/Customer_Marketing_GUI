@echo off
echo ===============================================
echo    STEALTH LinkedIn Scraper - Maximum Success
echo ===============================================
echo.
echo This version uses MAXIMUM anti-detection measures:
echo - Fresh scraper instance for each company
echo - Random user agents and headers
echo - 60-120 second delays between requests
echo - Realistic browsing patterns
echo.
echo This will take longer but has the highest success rate!
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause

python linkedin_scraper_stealth.py "%1" --url-column "LinkedIn_URL" --size-column "Company_Size" --output-file "%~n1_stealth_results.xlsx"

echo.
echo ===============================================
echo Processing complete! Check the results file.
echo ===============================================
pause