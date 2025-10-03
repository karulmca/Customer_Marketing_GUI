@echo off
echo ===============================================
echo    OPTIMIZED LinkedIn Scraper - Exact Format
echo ===============================================
echo.
echo This version extracts LinkedIn ranges exactly as shown:
echo "1-10 employees", "11-50 employees", "201-500 employees"
echo.
echo Perfect for matching LinkedIn's display format!
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause

python linkedin_scraper_optimized.py "%1" --url-column "LinkedIn_URL" --size-column "Company_Size" --output-file "%~n1_optimized_results.xlsx"

echo.
echo ===============================================
echo Processing complete! Check the results file.
echo Results will show exact LinkedIn format ranges.
echo ===============================================
pause