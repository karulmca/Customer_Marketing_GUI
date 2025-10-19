"""
Automated wrapper for revenue scraper used in scheduled jobs.
"""
import logging
import os
import sys

logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scrapers_dir = os.path.join(parent_dir, '..', 'scrapers')
if scrapers_dir not in sys.path:
    sys.path.insert(0, scrapers_dir)

class AutomatedRevenueScraper:
    def __init__(self):
        self.scraper = None

    def initialize(self):
        try:
            from multi_source_revenue_scraper import MultiSourceRevenueScraper
            self.scraper = MultiSourceRevenueScraper()
            logger.info("AutomatedRevenueScraper: Initialized")
        except Exception as e:
            logger.error(f"AutomatedRevenueScraper: Failed to initialize: {e}")
            self.scraper = None

    def estimate_revenue(self, company_row):
        if self.scraper is None:
            self.initialize()
            if self.scraper is None:
                raise RuntimeError("Revenue scraper not available for automated job")
        # The underlying MultiSourceRevenueScraper exposes get_company_revenue
        try:
            name = company_row.get('Company Name') if isinstance(company_row, dict) else None
            website = None
            if isinstance(company_row, dict):
                website = company_row.get('Website') or company_row.get('Website_URL') or company_row.get('Company_Website')
            result = self.scraper.get_company_revenue(name or '', website or '')
            return result.get('revenue')
        except Exception as e:
            logger.debug(f"estimate_revenue fallback failed: {e}")
            raise

    def process_companies(self, df, company_name_column='Company Name'):
        if self.scraper is None:
            self.initialize()
            if self.scraper is None:
                raise RuntimeError("Revenue scraper not available for automated job")
        try:
            # The MultiSourceRevenueScraper does not provide a batch `process_companies` method.
            # Implement a simple rowwise adapter that uses `get_company_revenue`.
            # Add/ensure revenue columns exist
            rev_col = 'Revenue_MultiSource'
            src_col = 'Revenue_Source'
            src_url_col = 'Revenue_Source_URL'
            status_col = 'Revenue_Status'

            for c in [rev_col, src_col, src_url_col, status_col]:
                if c not in df.columns:
                    df[c] = None

            for idx, row in df.iterrows():
                company_name = row.get(company_name_column, '')
                website = row.get('Website') or row.get('Website_URL') or row.get('Company_Website') or ''
                try:
                    result = self.scraper.get_company_revenue(company_name, website)
                    df.at[idx, rev_col] = result.get('revenue')
                    df.at[idx, src_col] = result.get('source')
                    df.at[idx, src_url_col] = result.get('source_url')
                    df.at[idx, status_col] = result.get('status')
                except Exception as e:
                    logger.debug(f"Revenue lookup failed for {company_name}: {e}")
                    df.at[idx, status_col] = f"Error: {e}"

            return df
        except Exception as e:
            logger.error(f"AutomatedRevenueScraper: Processing failed: {e}")
            raise
