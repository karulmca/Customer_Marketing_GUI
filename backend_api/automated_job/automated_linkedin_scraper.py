"""
Automated LinkedIn scraper wrapper for scheduled/automated jobs.
This module intentionally duplicates behaviour used by manual processing but keeps it isolated so manual code remains untouched.

Class: AutomatedLinkedInScraper
- initialize(scraping_enabled=True): initializes underlying scraper
- process_companies(df, linkedin_column, website_column, company_name_column): returns processed DataFrame
"""
import logging
import os
import sys
from typing import Optional

logger = logging.getLogger(__name__)

# Add scrapers directory to path (same pattern used by company_processor)
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scrapers_dir = os.path.join(parent_dir, '..', 'scrapers')
if scrapers_dir not in sys.path:
    sys.path.insert(0, scrapers_dir)

class AutomatedLinkedInScraper:
    def __init__(self):
        self.scraper = None

    def initialize(self):
        """Import and initialize the CompleteCompanyScraper for automated jobs"""
        try:
            from linkedin_company_complete_scraper import CompleteCompanyScraper
            self.scraper = CompleteCompanyScraper()
            logger.info("AutomatedLinkedInScraper: Initialized CompleteCompanyScraper")
        except Exception as e:
            logger.error(f"AutomatedLinkedInScraper: Failed to initialize scraper: {e}")
            self.scraper = None

    def process_companies(self, df, linkedin_column: str, website_column: str, company_name_column: str):
        """Run the underlying scraper against the DataFrame and return processed DataFrame"""
        if self.scraper is None:
            self.initialize()
            if self.scraper is None:
                raise RuntimeError("LinkedIn scraper not available for automated job")

        # Delegate to the same method used by manual path
        try:
            processed_df = self.scraper.process_companies(
                df,
                linkedin_column=linkedin_column,
                website_column=website_column,
                company_name_column=company_name_column
            )
            logger.info("AutomatedLinkedInScraper: Processing completed")
            return processed_df
        except Exception as e:
            logger.error(f"AutomatedLinkedInScraper: Processing failed: {e}")
            raise
