import pandas as pd
import pytz
from datetime import datetime
from .db_utils import get_database_connection
from config_loader import ConfigLoader
from .file_upload_processor import FileUploadProcessor

class AutomatedFileUploadProcessor(FileUploadProcessor):
    """
    Automated job processor for scheduled tasks. Inherits all logic from FileUploadProcessor.
    Only overrides or extends methods as needed for automated jobs.
    """
    def process_uploaded_file_auto(self, file_upload_id: str) -> bool:
        # Always use a valid user_id for automated jobs
        default_user_id = 1
        try:
            # Ensure user_id is always set to default_user_id
            self.update_processing_status(file_upload_id, 'processing', user_id=default_user_id)
            self.mark_job_as_started(file_upload_id, user_id=default_user_id)
            print(f"🔄 [Automated] Started processing file_upload_id: {file_upload_id} (user_id={default_user_id})")
            upload_info = self.get_upload_data(file_upload_id)
            if not upload_info:
                self.mark_job_as_failed(file_upload_id, 'No data found in database', user_id=default_user_id)
                self.update_processing_status(file_upload_id, 'failed', 'No data found in database', user_id=default_user_id)
                return False
            raw_data = upload_info['raw_data']
            file_name = upload_info['file_name']
            df = pd.DataFrame(raw_data['data'])
            mapped_df = self.apply_column_mapping(df)
            # Standardize column names to match database schema
            column_rename_map = {
                'Company Name': 'company_name',
                'LinkedIn_URL': 'linkedin_url',
                'Website_URL': 'company_website',
                'Company_Size': 'company_size',
                'Industry': 'industry',
                'Revenue': 'revenue',
            }
            mapped_df = mapped_df.rename(columns=column_rename_map)
            if 'industry' in mapped_df.columns:
                mapped_df['industry'] = mapped_df['industry'].astype(str).str.slice(0, 200)
            mapped_df['file_source'] = file_name
            mapped_df['file_upload_id'] = file_upload_id
            mapped_df['created_by'] = 'automated_job'
            # Drop columns not present in company_data table
            valid_columns = [
                'file_upload_id', 'file_source', 'created_by', 'industry', 'company_name', 'company_size',
                'company_website', 'linkedin_url', 'revenue', 'processing_status', 'processed_date'
            ]
            if 'user_id' in mapped_df.columns:
                mapped_df = mapped_df.drop(columns=['user_id'])
            mapped_df = mapped_df[[col for col in mapped_df.columns if col in valid_columns]]
            # Retry logic for database insertion
            max_db_retries = 3
            for db_attempt in range(max_db_retries):
                success = self.db_connection.insert_dataframe(mapped_df, "company_data")
                if success:
                    break
                print(f"[WARN] Database insertion failed (attempt {db_attempt+1}/{max_db_retries})")
                if db_attempt == max_db_retries - 1:
                    self.sync_processing_completion(file_upload_id, 'failed', 0, 'Database insertion failed', user_id=default_user_id)
                    return False
            self.update_processing_status(file_upload_id, 'processing', 'LinkedIn scraping in progress', user_id=default_user_id)
            # LinkedIn scraping logic (if available)
            scraped_count = 0
            if hasattr(self, 'LINKEDIN_SCRAPER_AVAILABLE') and self.LINKEDIN_SCRAPER_AVAILABLE:
                max_scraper_retries = 3
                for scraper_attempt in range(max_scraper_retries):
                    try:
                        import threading
                        result = {}
                        def run_scraper():
                            result['count'] = self._perform_linkedin_scraping(file_upload_id, mapped_df)
                        scraper_thread = threading.Thread(target=run_scraper)
                        scraper_thread.start()
                        scraper_thread.join(timeout=30)
                        if scraper_thread.is_alive():
                            print(f"[WARN] Scraper timeout (attempt {scraper_attempt+1}/{max_scraper_retries}) - retrying...")
                            continue
                        scraped_count = result.get('count', 0)
                        break
                    except Exception as e:
                        print(f"[WARN] Scraper error (attempt {scraper_attempt+1}/{max_scraper_retries}): {e}")
                        if scraper_attempt == max_scraper_retries - 1:
                            self.sync_processing_completion(file_upload_id, 'failed', len(mapped_df), f'Scraper failed: {e}', user_id=default_user_id)
                            return False
            self.mark_job_as_completed(file_upload_id, len(mapped_df), user_id=default_user_id)
            self.sync_processing_completion(file_upload_id, 'completed', len(mapped_df), f'Successfully processed and scraped {scraped_count} companies', user_id=default_user_id)
            print(f"✅ [Automated] Successfully processed file_upload_id: {file_upload_id} (scraped: {scraped_count})")
            return True
        except Exception as e:
            error_msg = f"[Automated] Processing error: {str(e)}"
            self.mark_job_as_failed(file_upload_id, error_msg, user_id=default_user_id)
            self.sync_processing_completion(file_upload_id, 'failed', 0, error_msg, user_id=default_user_id)
            print(f"❌ {error_msg}")
            return False
