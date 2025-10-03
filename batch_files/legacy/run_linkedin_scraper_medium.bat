@echo off
echo Running LinkedIn Scraper with Medium Wait Times...
echo This will process companies with 20-40 second delays between each company
echo for a balance between speed and success rate.
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause

python linkedin_company_scraper_enhanced.py "%1" --url-column "LinkedIn_URL" --size-column "Company_Size" --wait-min 20 --wait-max 40 --output-file "%~n1_results_medium.xlsx"

echo.
echo Processing complete! Check the results file.
pause