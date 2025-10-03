#!/usr/bin/env python3
"""
Enhanced Scheduled Processor with LinkedIn Integration
Processes JSON files using the same logic as linkedin_data_scraper_gui_fixed.py
"""

import os
import sys
import json
import pandas as pd
import subprocess
import tempfile
import logging
import time
from datetime import datetime
from typing import Optional, Dict, Any, List
import argparse

# Add database_config to path
current_dir = os.path.dirname(os.path.abspath(__file__))
database_config_path = os.path.join(current_dir, 'database_config')
if database_config_path not in sys.path:
    sys.path.insert(0, database_config_path)

try:
    from database_config.file_upload_processor import FileUploadProcessor
    from database_config.db_utils import get_database_connection
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Database dependencies not available: {e}")
    DATABASE_AVAILABLE = False

# Setup logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/enhanced_scheduled_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LinkedInDataProcessor:
    """Enhanced processor using LinkedIn scraper logic"""
    
    def __init__(self):
        if not DATABASE_AVAILABLE:
            raise Exception("Database dependencies not available")
            
        self.db_connection = get_database_connection("postgresql")
        if self.db_connection:
            self.db_connection.connect()
    
    def detect_column_mapping(self, columns: List[str]) -> Dict[str, str]:
        """Detect column mappings for LinkedIn scraper"""
        mapping = {
            'linkedin_column': 'LinkedIn_URL',
            'website_column': 'Company_Website', 
            'company_column': 'Company_Name'
        }
        
        # Convert to lowercase for matching
        columns_lower = [col.lower() for col in columns]
        
        # LinkedIn URL detection
        linkedin_patterns = ['linkedin', 'linkedin_url', 'linkedin url', 'linkedin profile']
        for pattern in linkedin_patterns:
            for i, col in enumerate(columns_lower):
                if pattern in col:
                    mapping['linkedin_column'] = columns[i]
                    break
        
        # Website detection  
        website_patterns = ['website', 'company_website', 'company website', 'url', 'web']
        for pattern in website_patterns:
            for i, col in enumerate(columns_lower):
                if pattern in col and 'linkedin' not in col:
                    mapping['website_column'] = columns[i]
                    break
        
        # Company name detection
        company_patterns = ['company', 'company_name', 'company name', 'name', 'organization']
        for pattern in company_patterns:
            for i, col in enumerate(columns_lower):
                if pattern in col:
                    mapping['company_column'] = columns[i]
                    break
        
        return mapping
    
    def process_json_data(self, json_data: Dict[Any, Any], file_upload_id: int, 
                         scraper_type: str = "complete", progress_callback=None) -> bool:
        """Process JSON data using LinkedIn scraping logic with detailed stage tracking"""
        try:
            logger.info(f"🚀 Starting comprehensive processing for file_upload_id: {file_upload_id}")
            
            # Stage 1: Data Preparation
            if progress_callback:
                progress_callback(file_upload_id, "Data Preparation", 1, 4)
            
            # Extract data from JSON
            columns = json_data.get('columns', [])
            data_records = json_data.get('data', [])
            
            if not data_records:
                logger.warning(f"No data records found in file_upload_id: {file_upload_id}")
                return True  # Empty file is considered successful
            
            # Create DataFrame from JSON
            df = pd.DataFrame(data_records, columns=columns)
            logger.info(f"📊 Stage 1 Complete - DataFrame created: {len(df)} rows, {len(df.columns)} columns")
            
            # Detect column mappings
            column_mapping = self.detect_column_mapping(df.columns.tolist())
            logger.info(f"🔍 Column mapping detected: {column_mapping}")
            
            # Stage 2: File Preparation
            if progress_callback:
                progress_callback(file_upload_id, "File Preparation", 2, 4)
            
            # Create temporary Excel file for processing
            with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as temp_file:
                temp_input_path = temp_file.name
                df.to_excel(temp_input_path, index=False)
                
            # Create temporary output file
            temp_output_path = tempfile.mktemp(suffix='_processed.xlsx')
            logger.info(f"📁 Stage 2 Complete - Temporary files prepared")
            
            try:
                # Stage 3: LinkedIn Scraping (Company Size + Industry + Revenue)
                if progress_callback:
                    progress_callback(file_upload_id, "LinkedIn Scraping", 3, 4)
                
                logger.info(f"🔍 Stage 3 Starting - LinkedIn scraping with {scraper_type} scraper")
                logger.info(f"📋 Processing {len(df)} companies for:")
                logger.info(f"   • Company Size extraction from LinkedIn")
                logger.info(f"   • Industry identification from LinkedIn")
                logger.info(f"   • Revenue data from company websites")
                
                # Process using LinkedIn scraper with detailed logging
                success = self.run_linkedin_scraper_with_progress(
                    input_file=temp_input_path,
                    output_file=temp_output_path,
                    column_mapping=column_mapping,
                    scraper_type=scraper_type,
                    file_upload_id=file_upload_id,
                    progress_callback=progress_callback
                )
                
                if success and os.path.exists(temp_output_path):
                    # Read processed results
                    processed_df = pd.read_excel(temp_output_path)
                    logger.info(f"✅ Stage 3 Complete - LinkedIn scraping successful")
                    logger.info(f"📊 Scraped data summary:")
                    
                    # Log scraping results
                    self.log_scraping_results(processed_df)
                    
                    # Stage 4: Database Storage
                    if progress_callback:
                        progress_callback(file_upload_id, "Database Storage", 4, 4)
                    
                    # Insert processed data into company_data table
                    inserted_count = self.insert_company_data(processed_df, file_upload_id)
                    logger.info(f"✅ Stage 4 Complete - Inserted {inserted_count} records into database")
                    
                    # Note: Job status updates are handled by the calling EnhancedScheduledProcessor
                    
                    # Final success status
                    if progress_callback:
                        progress_callback(file_upload_id, "Completed Successfully", 4, 4)
                    
                    return True
                else:
                    logger.error(f"❌ Stage 3 Failed - LinkedIn scraping unsuccessful")
                    return False
                    
            finally:
                # Clean up temporary files
                if os.path.exists(temp_input_path):
                    os.unlink(temp_input_path)
                if os.path.exists(temp_output_path):
                    os.unlink(temp_output_path)
                    
        except Exception as e:
            logger.error(f"❌ Error in comprehensive processing: {str(e)}")
            return False
    
    def log_scraping_results(self, df: pd.DataFrame):
        """Log detailed scraping results"""
        try:
            total_companies = len(df)
            
            # Count successful extractions using correct column names
            company_size_extracted = 0
            industry_extracted = 0
            revenue_extracted = 0
            
            # Check for enhanced column names (from complete scraper)
            if 'Company_Size_Enhanced' in df.columns:
                company_size_extracted = ((df['Company_Size_Enhanced'].notna()) & 
                                        (df['Company_Size_Enhanced'] != 'Not Processed') &
                                        (df['Company_Size_Enhanced'] != '')).sum()
            elif 'Company_Size' in df.columns:
                company_size_extracted = df['Company_Size'].notna().sum()
                
            if 'Industry_Enhanced' in df.columns:
                industry_extracted = ((df['Industry_Enhanced'].notna()) & 
                                    (df['Industry_Enhanced'] != 'Not Processed') &
                                    (df['Industry_Enhanced'] != '')).sum()
            elif 'Industry' in df.columns:
                industry_extracted = df['Industry'].notna().sum()
                
            if 'Revenue_Enhanced' in df.columns:
                revenue_extracted = ((df['Revenue_Enhanced'].notna()) & 
                                   (df['Revenue_Enhanced'] != 'Not Processed') &
                                   (df['Revenue_Enhanced'] != '')).sum()
            elif 'Revenue' in df.columns:
                revenue_extracted = df['Revenue'].notna().sum()
            
            logger.info(f"   📊 Total Companies: {total_companies}")
            logger.info(f"   🏢 Company Size extracted: {company_size_extracted}/{total_companies} ({(company_size_extracted/total_companies)*100:.1f}%)")
            logger.info(f"   🏭 Industry extracted: {industry_extracted}/{total_companies} ({(industry_extracted/total_companies)*100:.1f}%)")
            logger.info(f"   💰 Revenue extracted: {revenue_extracted}/{total_companies} ({(revenue_extracted/total_companies)*100:.1f}%)")
            
        except Exception as e:
            logger.error(f"❌ Error logging scraping results: {e}")
    
    def run_linkedin_scraper_with_progress(self, input_file: str, output_file: str,
                                         column_mapping: Dict[str, str], scraper_type: str,
                                         file_upload_id: int, progress_callback=None) -> bool:
        """Run LinkedIn scraper with progress tracking"""
        try:
            logger.info(f"🚀 Starting LinkedIn scraper: {scraper_type}")
            logger.info(f"📋 Scraping stages:")
            logger.info(f"   1. Company Size extraction from LinkedIn profiles")
            logger.info(f"   2. Industry identification from LinkedIn pages") 
            logger.info(f"   3. Revenue data extraction from company websites")
            
            # Build command based on scraper type (same as before)
            if scraper_type == "openai":
                script_path = "scrapers/linkedin_openai_scraper.py"
                cmd = [
                    sys.executable, script_path, input_file,
                    "--use-openai",
                    "--linkedin-column", column_mapping.get('linkedin_column', 'LinkedIn_URL'),
                    "--website-column", column_mapping.get('website_column', 'Company_Website'),
                    "--company-column", column_mapping.get('company_column', 'Company_Name'),
                    "--wait-min", "10",
                    "--wait-max", "20",
                    "--output-file", output_file
                ]
                
            elif scraper_type == "complete":
                script_path = "scrapers/linkedin_company_complete_scraper.py"
                cmd = [
                    sys.executable, script_path, input_file,
                    "--linkedin-column", column_mapping.get('linkedin_column', 'LinkedIn_URL'),
                    "--website-column", column_mapping.get('website_column', 'Company_Website'),
                    "--company-column", column_mapping.get('company_column', 'Company_Name'),
                    "--wait-min", "10",
                    "--wait-max", "20",
                    "--output-file", output_file
                ]
                
            else:  # linkedin only
                script_path = "scrapers/linkedin_company_scraper_enhanced.py"
                cmd = [
                    sys.executable, script_path, input_file,
                    "--linkedin-column", column_mapping.get('linkedin_column', 'LinkedIn_URL'),
                    "--wait-min", "10", 
                    "--wait-max", "20",
                    "--output-file", output_file
                ]
            
            # Check if script exists
            if not os.path.exists(script_path):
                logger.error(f"❌ Scraper script not found: {script_path}")
                return False
            
            logger.info(f"🔧 Executing scraper command...")
            
            # Run the scraper with real-time output monitoring
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Monitor progress in real-time
            company_count = 0
            total_companies = 0
            
            for line in iter(process.stdout.readline, ''):
                if not line:
                    break
                    
                line = line.strip()
                if line:
                    logger.info(f"🔍 Scraper: {line}")
                    
                    # Parse progress from scraper output
                    if "Processing company" in line and "/" in line:
                        try:
                            # Extract "Processing company X/Y" format
                            parts = line.split("Processing company ")[1].split("/")
                            if len(parts) >= 2:
                                current = int(parts[0])
                                total = int(parts[1].split(":")[0])
                                
                                if total_companies == 0:
                                    total_companies = total
                                
                                if progress_callback:
                                    stage_progress = f"Scraping Company {current}/{total}"
                                    progress_callback(file_upload_id, stage_progress, current, total)
                        except (ValueError, IndexError):
                            pass
            
            # Wait for completion
            return_code = process.wait()
            
            if return_code == 0:
                logger.info(f"✅ LinkedIn scraper completed successfully")
                return True
            else:
                logger.error(f"❌ LinkedIn scraper failed with return code: {return_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running LinkedIn scraper with progress: {str(e)}")
            return False
    
    def run_linkedin_scraper(self, input_file: str, output_file: str,
                           column_mapping: Dict[str, str], scraper_type: str = "complete") -> bool:
        """Run LinkedIn scraper using subprocess - same as GUI"""
        try:
            logger.info(f"🚀 Starting LinkedIn scraper: {scraper_type}")
            
            # Build command based on scraper type (same as GUI logic)
            if scraper_type == "openai":
                script_path = "scrapers/linkedin_openai_scraper.py"
                cmd = [
                    sys.executable, script_path, input_file,
                    "--use-openai",
                    "--linkedin-column", column_mapping.get('linkedin_column', 'LinkedIn_URL'),
                    "--website-column", column_mapping.get('website_column', 'Company_Website'),
                    "--company-column", column_mapping.get('company_column', 'Company_Name'),
                    "--wait-min", "10",
                    "--wait-max", "20",
                    "--output-file", output_file
                ]
                
            elif scraper_type == "complete":
                script_path = "scrapers/linkedin_company_complete_scraper.py"
                cmd = [
                    sys.executable, script_path, input_file,
                    "--linkedin-column", column_mapping.get('linkedin_column', 'LinkedIn_URL'),
                    "--website-column", column_mapping.get('website_column', 'Company_Website'),
                    "--company-column", column_mapping.get('company_column', 'Company_Name'),
                    "--wait-min", "10",
                    "--wait-max", "20",
                    "--output-file", output_file
                ]
                
            else:  # linkedin only
                script_path = "scrapers/linkedin_company_scraper_enhanced.py"
                cmd = [
                    sys.executable, script_path, input_file,
                    "--linkedin-column", column_mapping.get('linkedin_column', 'LinkedIn_URL'),
                    "--wait-min", "10", 
                    "--wait-max", "20",
                    "--output-file", output_file
                ]
            
            # Check if script exists
            if not os.path.exists(script_path):
                logger.error(f"❌ Scraper script not found: {script_path}")
                return False
            
            logger.info(f"🔧 Running command: {' '.join(cmd)}")
            
            # Run the scraper (same as GUI)
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Capture output
            output, _ = process.communicate()
            
            if process.returncode == 0:
                logger.info(f"✅ LinkedIn scraper completed successfully")
                logger.debug(f"Scraper output: {output}")
                return True
            else:
                logger.error(f"❌ LinkedIn scraper failed with return code: {process.returncode}")
                logger.error(f"Scraper output: {output}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running LinkedIn scraper: {str(e)}")
            return False
    
    def insert_company_data(self, df: pd.DataFrame, file_upload_id: int) -> int:
        """Insert processed company data into company_data table"""
        try:
            if df.empty:
                logger.warning("No data to insert into company_data table")
                return 0
            
            # Get original file info
            file_info = self.get_file_upload_info(file_upload_id)
            file_name = file_info.get('file_name', f'file_{file_upload_id}') if file_info else f'file_{file_upload_id}'
            
            # Prepare data for insertion (matching actual company_data table structure)
            insert_data = []
            
            for index, row in df.iterrows():
                # Clean up nan values and ensure strings
                # Try different column name variations for scraped data
                company_size = str(row.get('Company_Size_Enhanced', 
                                 row.get('Company_Size',
                                 row.get('Company Size', ''))))
                if company_size.lower() in ['nan', 'not processed', '']:
                    company_size = ''
                    
                industry = str(row.get('Industry_Enhanced',
                             row.get('Industry', '')))
                if industry.lower() in ['nan', 'not processed', '']:
                    industry = ''
                    
                revenue = str(row.get('Revenue_Enhanced',
                            row.get('Revenue', '')))
                if revenue.lower() in ['nan', 'not processed', '']:
                    revenue = ''
                
                record = {
                    'company_name': str(row.get('Company_Name', row.get('Company Name', ''))),
                    'linkedin_url': str(row.get('LinkedIn_URL', row.get('LinkedIn URL', ''))),
                    'company_website': str(row.get('Company_Website', row.get('Company Website', ''))),
                    'company_size': company_size,
                    'industry': industry,
                    'revenue': revenue,
                    'upload_date': datetime.now(),
                    'file_source': file_name,
                    'created_by': 'ScheduledProcessor',
                    'updated_at': datetime.now(),
                    'file_upload_id': file_upload_id
                }
                insert_data.append(record)
            
            # Create DataFrame and insert
            insert_df = pd.DataFrame(insert_data)
            success = self.db_connection.insert_dataframe(insert_df, "company_data")
            
            if success:
                logger.info(f"✅ Successfully inserted {len(insert_data)} records into company_data")
                return len(insert_data)
            else:
                logger.error("❌ Failed to insert data into company_data table")
                return 0
                
        except Exception as e:
            logger.error(f"❌ Error inserting company data: {str(e)}")
            return 0
    
    def get_file_upload_info(self, file_upload_id: int) -> Optional[Dict]:
        """Get file upload information"""
        try:
            query = f"SELECT file_name, uploaded_by FROM file_upload WHERE id = '{file_upload_id}'"
            result = self.db_connection.query_to_dataframe(query)
            
            if result is not None and not result.empty:
                return result.iloc[0].to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting file upload info: {e}")
            return None

class EnhancedScheduledProcessor:
    """Enhanced scheduled processor with LinkedIn integration"""
    
    def __init__(self):
        if not DATABASE_AVAILABLE:
            raise Exception("Database dependencies not available")
            
        self.db_connection = get_database_connection("postgresql")
        if self.db_connection:
            self.db_connection.connect()
            
        self.file_processor = FileUploadProcessor()
        self.data_processor = LinkedInDataProcessor()
    
    def process_pending_job(self, job_id: int, scraper_type: str = "complete") -> bool:
        """Process a specific pending job by job ID for auto-start functionality"""
        try:
            logger.info(f"🚀 Auto-starting processing job ID: {job_id}")
            
            # Get job details
            job_query = """
                SELECT pj.id, pj.file_upload_id, pj.job_status, fu.file_name, fu.raw_data::text as raw_data
                FROM processing_jobs pj
                JOIN file_upload fu ON pj.file_upload_id = fu.id
                WHERE pj.id = %s AND pj.job_status = 'queued'
            """
            
            import pandas as pd
            with self.db_connection.manager.engine.connect() as conn:
                job_result = pd.read_sql_query(job_query, conn, params=(job_id,))
            
            if job_result.empty:
                logger.warning(f"No pending job found with ID: {job_id}")
                return False
            
            job_row = job_result.iloc[0]
            file_upload_id = job_row['file_upload_id']  # Get UUID string directly
            file_name = job_row['file_name']
            raw_data_str = job_row['raw_data']
            
            logger.info(f"📋 Processing file: {file_name} (Upload ID: {file_upload_id})")
            
            # Update job status to 'started'
            self.update_job_status(file_upload_id, 'started')
            
            # Update to 'processing'
            self.update_file_status(file_upload_id, 'processing', 'Auto-started processing with LinkedIn scraping...')
            self.update_job_status(file_upload_id, 'processing', progress_info="LinkedIn scraping initiated automatically")
            
            # Parse JSON data
            if isinstance(raw_data_str, str):
                json_data = json.loads(raw_data_str)
            elif isinstance(raw_data_str, dict):
                json_data = raw_data_str
            else:
                logger.error(f"Unexpected raw_data type: {type(raw_data_str)}")
                return False
            
            # Process the data
            success = self.data_processor.process_json_data(json_data, file_upload_id, scraper_type)
            
            if success:
                # Update job status to completed
                self.update_job_status(file_upload_id, 'completed', progress_info="All processing stages completed successfully")
                self.update_file_status(file_upload_id, 'completed', f'Auto-processing completed successfully with LinkedIn scraping.')
                logger.info(f"✅ Auto-processing completed successfully for job {job_id}")
                return True
            else:
                # Update job status to error
                self.update_job_status(file_upload_id, 'error', error_message="LinkedIn scraping failed")
                self.update_file_status(file_upload_id, 'error', 'Auto-processing failed during LinkedIn scraping.')
                logger.error(f"❌ Auto-processing failed for job {job_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error in process_pending_job: {str(e)}")
            self.update_job_status(file_upload_id if 'file_upload_id' in locals() else 0, 'error', 
                                 error_message=f"Auto-processing error: {str(e)}")
            return False
    
    def process_pending_files(self, scraper_type: str = "complete") -> int:
        """Process all pending files using LinkedIn scraper logic"""
        try:
            logger.info("🔍 Looking for pending files to process...")
            
            # Get pending files with proper JSON handling
            query = "SELECT id, file_name, raw_data::text as raw_data, uploaded_by FROM file_upload WHERE processing_status = 'pending' ORDER BY upload_date ASC"
            pending_files = self.db_connection.query_to_dataframe(query)
            
            if pending_files is None or pending_files.empty:
                logger.info("✅ No pending files found")
                return 0
            
            logger.info(f"📋 Found {len(pending_files)} pending files to process")
            
            processed_count = 0
            
            for index, file_record in pending_files.iterrows():
                file_id = file_record['id']
                file_name = file_record['file_name']
                raw_data_str = file_record['raw_data']
                
                logger.info(f"🔄 Processing file: {file_name} (ID: {file_id})")
                
                try:
                    # Job Status Flow: queued → started → processing → completed/error
                    # Step 1: Update job status to 'started'
                    self.update_job_status(file_id, 'started')
                    
                    # Step 2: Update file status to 'processing' and job status to 'processing'
                    self.update_file_status(file_id, 'processing', 'Starting comprehensive LinkedIn processing...')
                    self.update_job_status(file_id, 'processing', progress_info="LinkedIn scraping pipeline initiated")
                    
                    logger.info(f"🚀 Starting comprehensive processing for {file_name}")
                    logger.info(f"📋 Processing stages:")
                    logger.info(f"   Stage 1: Data Preparation")
                    logger.info(f"   Stage 2: File Preparation")
                    logger.info(f"   Stage 3: LinkedIn Scraping (Company Size + Industry + Revenue)")
                    logger.info(f"   Stage 4: Database Storage")
                    
                    # Parse JSON data - handle both string and dict
                    if isinstance(raw_data_str, str):
                        json_data = json.loads(raw_data_str)
                    elif isinstance(raw_data_str, dict):
                        json_data = raw_data_str
                    else:
                        logger.error(f"Unexpected raw_data type: {type(raw_data_str)}")
                        continue
                    
                    # Process the data using LinkedIn scraper with progress tracking
                    success = self.data_processor.process_json_data(
                        json_data, 
                        file_id, 
                        scraper_type,
                        progress_callback=self.update_processing_progress
                    )
                    
                    if success:
                        # Step 3: Update job status to 'completed' and file status to 'processed'
                        final_msg = f"Successfully processed with LinkedIn data extraction complete"
                        self.update_job_status(file_id, 'completed', progress_info="All processing stages completed successfully")
                        self.update_file_status(file_id, 'processed', final_msg, 100)
                        processed_count += 1
                        logger.info(f"🎉 Successfully completed all stages for file: {file_name}")
                        
                        # Log final summary
                        self.log_processing_summary(file_id, file_name)
                        
                    else:
                        # Step 3: Update job status to 'error' and file status to 'failed'
                        error_msg = 'LinkedIn processing failed during scraping stage'
                        self.update_job_status(file_id, 'error', error_message=error_msg)
                        self.update_file_status(file_id, 'failed', error_msg)
                        logger.error(f"❌ Failed to process file: {file_name}")
                        
                except Exception as e:
                    # Step 3: Update job status to 'error' and file status to 'failed'
                    error_msg = f"Processing error: {str(e)}"
                    self.update_job_status(file_id, 'error', error_message=error_msg)
                    self.update_file_status(file_id, 'failed', error_msg)
                    logger.error(f"❌ Error processing file {file_name}: {str(e)}")
                    logger.exception("Full exception details:")
            
            logger.info(f"🎉 Processing completed. {processed_count}/{len(pending_files)} files processed successfully")
            return processed_count
            
        except Exception as e:
            logger.error(f"❌ Error in process_pending_files: {str(e)}")
            return 0
    
    def log_processing_summary(self, file_id: int, file_name: str):
        """Log comprehensive processing summary"""
        try:
            # Get processing results from database
            query = f"""
            SELECT 
                COUNT(*) as total_records,
                COUNT(CASE WHEN company_size IS NOT NULL AND company_size != '' AND company_size != 'nan' THEN 1 END) as size_extracted,
                COUNT(CASE WHEN industry IS NOT NULL AND industry != '' AND industry != 'nan' THEN 1 END) as industry_extracted,
                COUNT(CASE WHEN revenue IS NOT NULL AND revenue != '' THEN 1 END) as revenue_extracted,
                COUNT(CASE WHEN linkedin_url IS NOT NULL AND linkedin_url != '' THEN 1 END) as linkedin_urls
            FROM company_data 
            WHERE file_upload_id = {file_id}
            """
            
            result = self.db_connection.query_to_dataframe(query)
            
            if result is not None and not result.empty:
                stats = result.iloc[0]
                total = stats['total_records']
                size_count = stats['size_extracted']
                industry_count = stats['industry_extracted'] 
                revenue_count = stats['revenue_extracted']
                linkedin_count = stats['linkedin_urls']
                
                logger.info(f"📊 Processing Summary for {file_name} (File ID: {file_id}):")
                logger.info(f"   📋 Total Records: {total}")
                logger.info(f"   🔗 LinkedIn URLs: {linkedin_count}/{total} ({(linkedin_count/total)*100:.1f}%)")
                logger.info(f"   🏢 Company Size: {size_count}/{total} ({(size_count/total)*100:.1f}%)")
                logger.info(f"   🏭 Industry: {industry_count}/{total} ({(industry_count/total)*100:.1f}%)")
                logger.info(f"   💰 Revenue: {revenue_count}/{total} ({(revenue_count/total)*100:.1f}%)")
                
                # Calculate overall success rate
                total_fields = total * 3  # 3 fields: size, industry, revenue
                extracted_fields = size_count + industry_count + revenue_count
                success_rate = (extracted_fields / total_fields) * 100 if total_fields > 0 else 0
                
                logger.info(f"   ✅ Overall Success Rate: {success_rate:.1f}%")
                
        except Exception as e:
            logger.error(f"❌ Error logging processing summary: {e}")
    
    def update_file_status(self, file_id: int, status: str, error_message: str = None, progress: int = None):
        """Update file processing status with detailed progress tracking"""
        try:
            from sqlalchemy import text
            
            # Prepare update data with named parameters
            update_data = {
                'status': status,
                'processed_date': datetime.now(),
                'file_id': file_id
            }
            
            if error_message:
                update_data['error_message'] = error_message
                sql = """
                UPDATE file_upload 
                SET processing_status = :status, 
                    processed_date = :processed_date,
                    processing_error = :error_message
                WHERE id = :file_id
                """
            else:
                sql = """
                UPDATE file_upload 
                SET processing_status = :status, 
                    processed_date = :processed_date
                WHERE id = :file_id
                """
            
            # Execute update
            if self.db_connection and self.db_connection.manager and self.db_connection.manager.engine:
                with self.db_connection.manager.engine.connect() as conn:
                    conn.execute(text(sql), update_data)
                    conn.commit()
                    
                    status_msg = f"✅ Updated file {file_id} status to: {status}"
                    if progress is not None:
                        status_msg += f" (Progress: {progress}%)"
                    logger.info(status_msg)
            else:
                logger.error(f"❌ Database engine not available for status update")
                
        except Exception as e:
            logger.error(f"❌ Error updating file status: {str(e)}")
    
    def update_job_status(self, file_upload_id: int, job_status: str, error_message: str = None, progress_info: str = None):
        """Update processing job status with comprehensive tracking"""
        try:
            from sqlalchemy import text
            
            # Prepare job update data
            update_data = {
                'job_status': job_status,
                'file_upload_id': file_upload_id
            }
            
            # Set appropriate timestamps based on status
            if job_status == 'started':
                update_data['started_at'] = datetime.now()
                sql = """
                UPDATE processing_jobs 
                SET job_status = :job_status, started_at = :started_at
                WHERE file_upload_id = :file_upload_id AND job_status IN ('queued', 'processing')
                """
            elif job_status == 'processing':
                # Update without changing started_at if already set
                sql = """
                UPDATE processing_jobs 
                SET job_status = :job_status
                WHERE file_upload_id = :file_upload_id AND job_status IN ('queued', 'started', 'processing')
                """
            elif job_status in ['completed', 'processed']:
                update_data['completed_at'] = datetime.now()
                update_data['job_status'] = 'completed'  # Standardize to 'completed'
                sql = """
                UPDATE processing_jobs 
                SET job_status = :job_status, completed_at = :completed_at
                WHERE file_upload_id = :file_upload_id
                """
            elif job_status == 'error':
                update_data['completed_at'] = datetime.now()
                if error_message:
                    update_data['error_message'] = error_message
                    sql = """
                    UPDATE processing_jobs 
                    SET job_status = :job_status, completed_at = :completed_at, error_message = :error_message
                    WHERE file_upload_id = :file_upload_id
                    """
                else:
                    sql = """
                    UPDATE processing_jobs 
                    SET job_status = :job_status, completed_at = :completed_at
                    WHERE file_upload_id = :file_upload_id
                    """
            else:
                # Default update
                sql = """
                UPDATE processing_jobs 
                SET job_status = :job_status
                WHERE file_upload_id = :file_upload_id
                """
            
            # Execute job status update
            if self.db_connection and self.db_connection.manager and self.db_connection.manager.engine:
                with self.db_connection.manager.engine.connect() as conn:
                    result = conn.execute(text(sql), update_data)
                    conn.commit()
                    
                    if result.rowcount > 0:
                        status_msg = f"✅ Updated job for file {file_upload_id} to: {job_status}"
                        if progress_info:
                            status_msg += f" ({progress_info})"
                        logger.info(status_msg)
                    else:
                        logger.warning(f"⚠️ No job found to update for file {file_upload_id}")
            else:
                logger.error(f"❌ Database engine not available for job status update")
                
        except Exception as e:
            logger.error(f"❌ Error updating job status: {str(e)}")

    def update_processing_progress(self, file_id: int, stage: str, current: int, total: int):
        """Update processing progress for a specific stage"""
        progress = int((current / total) * 100) if total > 0 else 0
        status_msg = f"{stage}: Processing {current}/{total} companies"
        
        logger.info(f"🔄 File {file_id} - {status_msg} ({progress}%)")
        
        # Update file status with progress
        self.update_file_status(file_id, 'processing', status_msg, progress)
        
        # Update job status with progress info
        progress_info = f"{stage} - {progress}% complete"
        self.update_job_status(file_id, 'processing', progress_info=progress_info)
        
        return progress
    
    def get_job_status_summary(self):
        """Get comprehensive job status summary"""
        try:
            # Get job status counts
            job_status_query = """
            SELECT 
                job_status,
                COUNT(*) as count,
                COUNT(CASE WHEN started_at IS NOT NULL THEN 1 END) as started_count,
                COUNT(CASE WHEN completed_at IS NOT NULL THEN 1 END) as completed_count
            FROM processing_jobs 
            GROUP BY job_status
            ORDER BY 
                CASE job_status 
                    WHEN 'queued' THEN 1
                    WHEN 'started' THEN 2  
                    WHEN 'processing' THEN 3
                    WHEN 'completed' THEN 4
                    WHEN 'error' THEN 5
                    ELSE 6
                END
            """
            
            job_stats = self.db_connection.query_to_dataframe(job_status_query)
            
            # Get recent job activity
            recent_jobs_query = """
            SELECT 
                pj.id,
                pj.file_upload_id,
                fu.file_name,
                pj.job_status,
                pj.scheduled_at,
                pj.started_at,
                pj.completed_at,
                pj.error_message
            FROM processing_jobs pj
            JOIN file_upload fu ON pj.file_upload_id = fu.id
            ORDER BY pj.scheduled_at DESC
            LIMIT 10
            """
            
            recent_jobs = self.db_connection.query_to_dataframe(recent_jobs_query)
            
            logger.info("📊 Job Status Summary:")
            
            if job_stats is not None and not job_stats.empty:
                for _, row in job_stats.iterrows():
                    status_emoji = {
                        'queued': '⏳',
                        'started': '🔄', 
                        'processing': '⚡',
                        'completed': '✅',
                        'error': '❌'
                    }.get(row['job_status'], '❓')
                    
                    logger.info(f"   {status_emoji} {row['job_status'].upper()}: {row['count']} jobs")
            
            logger.info("📋 Recent Job Activity:")
            if recent_jobs is not None and not recent_jobs.empty:
                for _, job in recent_jobs.iterrows():
                    status_emoji = {
                        'queued': '⏳',
                        'started': '🔄',
                        'processing': '⚡', 
                        'completed': '✅',
                        'error': '❌'
                    }.get(job['job_status'], '❓')
                    
                    logger.info(f"   {status_emoji} {job['file_name']} - {job['job_status']} (ID: {job['file_upload_id']})")
            
            return {
                'job_stats': job_stats.to_dict('records') if job_stats is not None else [],
                'recent_jobs': recent_jobs.to_dict('records') if recent_jobs is not None else []
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting job status summary: {e}")
            return {}

    def get_processing_statistics(self):
        """Get comprehensive processing statistics"""
        try:
            # File upload statistics
            file_stats_query = """
            SELECT 
                processing_status,
                COUNT(*) as count
            FROM file_upload 
            GROUP BY processing_status
            ORDER BY processing_status
            """
            
            file_stats = self.db_connection.query_to_dataframe(file_stats_query)
            
            # Company data statistics
            company_stats_query = """
            SELECT 
                COUNT(*) as total_companies,
                COUNT(CASE WHEN company_size IS NOT NULL AND company_size != '' AND company_size != 'nan' THEN 1 END) as with_size,
                COUNT(CASE WHEN industry IS NOT NULL AND industry != '' AND industry != 'nan' THEN 1 END) as with_industry,
                COUNT(CASE WHEN revenue IS NOT NULL AND revenue != '' THEN 1 END) as with_revenue
            FROM company_data
            """
            
            company_stats = self.db_connection.query_to_dataframe(company_stats_query)
            
            logger.info("📊 Processing Statistics:")
            logger.info("📁 File Upload Status:")
            
            if file_stats is not None and not file_stats.empty:
                for _, row in file_stats.iterrows():
                    logger.info(f"   {row['processing_status']}: {row['count']} files")
            
            logger.info("🏢 Company Data Extraction:")
            if company_stats is not None and not company_stats.empty:
                stats = company_stats.iloc[0]
                total = stats['total_companies']
                logger.info(f"   Total Companies: {total}")
                logger.info(f"   Company Size: {stats['with_size']}/{total} ({(stats['with_size']/total)*100:.1f}%)" if total > 0 else "   Company Size: 0/0")
                logger.info(f"   Industry: {stats['with_industry']}/{total} ({(stats['with_industry']/total)*100:.1f}%)" if total > 0 else "   Industry: 0/0")  
                logger.info(f"   Revenue: {stats['with_revenue']}/{total} ({(stats['with_revenue']/total)*100:.1f}%)" if total > 0 else "   Revenue: 0/0")
            
            return {
                'file_stats': file_stats.to_dict('records') if file_stats is not None else [],
                'company_stats': company_stats.to_dict('records')[0] if company_stats is not None and not company_stats.empty else {}
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting processing statistics: {e}")
            return {}

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Enhanced Scheduled Processor with LinkedIn Integration')
    parser.add_argument('--mode', choices=['single', 'continuous'], default='single',
                      help='Processing mode: single run or continuous')
    parser.add_argument('--interval', type=int, default=30,
                      help='Interval in minutes for continuous mode (default: 30)')
    parser.add_argument('--scraper-type', choices=['linkedin', 'complete', 'openai'], default='complete',
                      help='LinkedIn scraper type to use (default: complete)')
    parser.add_argument('--file-id', type=int,
                      help='Process specific file ID only')
    
    args = parser.parse_args()
    
    logger.info("🚀 Starting Enhanced Scheduled Processor with LinkedIn Integration...")
    logger.info(f"Mode: {args.mode}, Scraper: {args.scraper_type}")
    
    try:
        processor = EnhancedScheduledProcessor()
        
        if args.file_id:
            logger.info(f"🎯 Processing specific file ID: {args.file_id}")
            # Process specific file (implement if needed)
            logger.info("Specific file processing not implemented yet")
        elif args.mode == 'single':
            logger.info("🔄 Running single processing cycle...")
            
            # Show initial statistics
            logger.info("📊 Initial Processing Statistics:")
            processor.get_processing_statistics()
            
            processed = processor.process_pending_files(args.scraper_type)
            
            # Show final statistics
            logger.info("📈 Final Processing Statistics:")
            processor.get_processing_statistics()
            
            logger.info(f"✅ Single cycle completed. Processed {processed} files.")
        elif args.mode == 'continuous':
            logger.info(f"🔄 Running continuous processing every {args.interval} minutes...")
            
            # Show initial statistics
            logger.info("📊 Initial Processing Statistics:")
            processor.get_processing_statistics()
            
            while True:
                try:
                    logger.info(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Starting processing cycle...")
                    processed = processor.process_pending_files(args.scraper_type)
                    
                    # Show current statistics after processing
                    logger.info("📈 Current Processing Statistics:")
                    processor.get_processing_statistics()
                    
                    logger.info(f"✅ Cycle completed. Processed {processed} files. Next cycle in {args.interval} minutes.")
                    time.sleep(args.interval * 60)  # Convert minutes to seconds
                except KeyboardInterrupt:
                    logger.info("⏹️ Continuous processing stopped by user")
                    break
                except Exception as e:
                    logger.error(f"❌ Error in continuous processing cycle: {str(e)}")
                    time.sleep(60)  # Wait 1 minute before retrying
        
    except Exception as e:
        logger.error(f"❌ Fatal error in enhanced scheduled processor: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()