@echo off
echo Running LinkedIn Scraper with Extended Wait Times...
echo This will process companies with 30-60 second delays between each company
echo to maximize success rate and avoid LinkedIn's anti-bot detection.
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause

python linkedin_company_scraper_enhanced.py "%1" --url-column "LinkedIn_URL" --size-column "Company_Size" --wait-min 30 --wait-max 60 --output-file "%~n1_results_slow.xlsx"

echo.
echo Processing complete! Check the results file.
pause