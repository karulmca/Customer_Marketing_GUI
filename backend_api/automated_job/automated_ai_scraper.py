"""
Automated wrapper for AI/Revenue estimation scraper used in scheduled jobs.
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

class AutomatedAIScraper:
    def __init__(self):
        self.scraper = None

    def initialize(self):
        try:
            # The scraper in scrapers/linkedin_openai_scraper.py exposes OpenAICompanyScraper
            from linkedin_openai_scraper import OpenAICompanyScraper
            self.scraper = OpenAICompanyScraper()
            logger.info("AutomatedAIScraper: Initialized")
        except Exception as e:
            logger.error(f"AutomatedAIScraper: Failed to initialize: {e}")
            self.scraper = None

    def analyze(self, df):
        if self.scraper is None:
            self.initialize()
            if self.scraper is None:
                raise RuntimeError("AI scraper not available for automated job")
        try:
            # OpenAICompanyScraper.process_companies signature supports linkedin_column, website_column, company_name_column, use_openai
            processed = self.scraper.process_companies(df, use_openai=True)
            return processed
        except Exception as e:
            logger.error(f"AutomatedAIScraper: Processing failed: {e}")
            raise
