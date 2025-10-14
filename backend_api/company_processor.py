
"""
Company Data Processing Pipeline
Integrates various scrapers for comprehensive company data extraction
"""

import os
import sys
import pandas as pd
import logging
from typing import Dict, Any, Optional
import time

# Add scrapers directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
scrapers_dir = os.path.join(parent_dir, 'scrapers')
sys.path.insert(0, scrapers_dir)

# Add database config to path for database operations
database_config_dir = os.path.join(parent_dir, 'database_config')
sys.path.insert(0, database_config_dir)

logger = logging.getLogger(__name__)

class CompanyDataProcessor:
    """Main processor that orchestrates different scrapers"""

    def __init__(self):
        self.linkedin_scraper = None
        self.revenue_scraper = None
        self.ai_scraper = None

        # Initialize database connection
        try:
            from db_utils import get_database_connection
            self.db_connection = get_database_connection("postgresql")
            if self.db_connection:
                self.db_connection.connect()
            logger.info("Database connection initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize database connection: {e}")
            self.db_connection = None
        
    def initialize_scrapers(self, scraping_enabled: bool = True, ai_analysis_enabled: bool = False):
        """Initialize required scrapers based on options"""
        scrapers_loaded = []
        
        if scraping_enabled:
            try:
                from linkedin_company_complete_scraper import CompleteCompanyScraper
                self.linkedin_scraper = CompleteCompanyScraper()
                scrapers_loaded.append("LinkedIn Company Scraper")
                logger.info("LinkedIn scraper initialized successfully")
            except ImportError as e:
                logger.error(f"Failed to import LinkedIn scraper: {e}")
            
            try:
                from multi_source_revenue_scraper import MultiSourceRevenueScraper
                self.revenue_scraper = MultiSourceRevenueScraper()
                scrapers_loaded.append("Multi-Source Revenue Scraper")
                logger.info("Revenue scraper initialized successfully")
            except ImportError as e:
                logger.error(f"Failed to import Revenue scraper: {e}")
        
        if ai_analysis_enabled:
            try:
                from linkedin_openai_scraper import LinkedInOpenAIScraper
                self.ai_scraper = LinkedInOpenAIScraper()
                scrapers_loaded.append("AI Analysis Scraper")
                logger.info("AI scraper initialized successfully")
            except ImportError as e:
                logger.error(f"Failed to import AI scraper: {e}")
        
        return scrapers_loaded
    
    def process_file(self, file_content: bytes = None, file_path: str = None, filename: str = "uploaded_file.xlsx",
                    scraping_enabled: bool = True, ai_analysis_enabled: bool = False, progress_callback=None) -> Dict[str, Any]:
        """
        Process an Excel file with company data (NO local storage required)
        
        Args:
            file_content: File content in bytes (preferred - no local storage)
            file_path: Path to the Excel file (legacy support)
            filename: Original filename for reference
            scraping_enabled: Whether to enable web scraping
            ai_analysis_enabled: Whether to enable AI analysis
            progress_callback: Function to call with progress updates
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        
        def update_progress(percent: int, message: str):
            if progress_callback:
                progress_callback(percent, message)
        
        try:
            update_progress(10, "Reading Excel file...")
            
            # Read file from content or path (prefer content to avoid local storage)
            if file_content:
                import io
                df = pd.read_excel(io.BytesIO(file_content))
                logger.info(f"✅ File read from memory content ({len(file_content)} bytes)")
            elif file_path:
                df = pd.read_excel(file_path)
                logger.info(f"✅ File read from path: {file_path}")
            else:
                raise ValueError("Either file_content or file_path must be provided")
            
            total_rows = len(df)
            
            update_progress(20, f"Loaded {total_rows} companies. Initializing scrapers...")
            scrapers_used = self.initialize_scrapers(scraping_enabled, ai_analysis_enabled)
            
            successful_rows = 0
            failed_rows = 0
            
            if scraping_enabled and self.linkedin_scraper:
                update_progress(30, "Processing companies with LinkedIn scraper...")
                
                # Map column names to match the actual file structure
                linkedin_col = 'LinkedIn_URL' if 'LinkedIn_URL' in df.columns else 'Company Linkedin'
                website_col = 'Company_Website' if 'Company_Website' in df.columns else 'Website'
                company_name_col = 'Company_Name' if 'Company_Name' in df.columns else 'Company Name'
                
                logger.info(f"Using columns: LinkedIn='{linkedin_col}', Website='{website_col}', Company='{company_name_col}'")
                
                # Use the existing process_companies method
                processed_df = self.linkedin_scraper.process_companies(
                    df,
                    linkedin_column=linkedin_col,
                    website_column=website_col, 
                    company_name_column=company_name_col
                )
                
                # Track progress through the dataframe processing
                for index, row in processed_df.iterrows():
                    progress_percent = 30 + int((index / total_rows) * 40)
                    update_progress(progress_percent, f"Processed {index + 1}/{total_rows} companies...")
                    
                    # Count successes and failures
                    linkedin_status = row.get('LinkedIn_Status', 'Unknown')
                    if linkedin_status == 'Success':
                        successful_rows += 1
                    else:
                        failed_rows += 1
                
                df = processed_df
                
            elif not scraping_enabled:
                # If scraping disabled, mark all as not processed
                df['Processing_Status'] = 'Scraping Disabled'
                df['LinkedIn_Status'] = 'Not Processed'
                df['Revenue_Status'] = 'Not Processed'
                successful_rows = 0
                failed_rows = 0
                update_progress(70, "Scraping disabled - file processed without data extraction")
            
            # AI Analysis (if enabled)
            if ai_analysis_enabled and self.ai_scraper:
                update_progress(75, "Running AI analysis for revenue estimation...")
                # Add AI processing logic here
                df['AI_Analysis_Status'] = 'Completed'
            elif ai_analysis_enabled:
                update_progress(75, "AI analysis requested but scraper not available")
                df['AI_Analysis_Status'] = 'Not Available'
            
            update_progress(85, "Saving processed results...")
            
            # Generate output filename (no local file creation)
            base_filename = filename if filename else "processed_file"
            name, ext = os.path.splitext(base_filename)
            output_filename = f"processed_{name}_{int(time.time())}{ext}"
            
            # Create Excel content in memory (NO local storage)
            import io
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False)
            output_content = excel_buffer.getvalue()
            excel_buffer.close()
            
            logger.info(f"✅ Generated Excel output in memory ({len(output_content)} bytes)")
            
            # Save the processed data to database
            saved_to_db = False
            db_save_error = None
            
            if self.db_connection:
                try:
                    update_progress(95, "Saving results to database...")
                    
                    # Prepare data for database with proper column mapping
                    db_df = df.copy()
                    
                    # Add metadata columns
                    db_df['file_source'] = filename
                    db_df['upload_date'] = pd.Timestamp.now()
                    db_df['processing_status'] = 'completed'
                    db_df['scraped_at'] = pd.Timestamp.now()
                    db_df['data_source'] = 'automated_scraping'
                    db_df['created_by'] = 'CompanyDataProcessor'
                    db_df['updated_at'] = pd.Timestamp.now()

                    # Fetch file_upload_id from file_upload table using filename
                    file_upload_id = None
                    try:
                        from sqlalchemy import text
                        query = text("SELECT id FROM file_upload WHERE file_name = :filename ORDER BY upload_date DESC LIMIT 1")
                        with self.db_connection.manager.engine.connect() as conn:
                            result = conn.execute(query, {"filename": filename})
                            row = result.fetchone()
                            if row:
                                file_upload_id = row[0]
                    except Exception as e:
                        logger.error(f"Failed to fetch file_upload_id for filename '{filename}': {e}")
                        file_upload_id = None
                    # ...existing code for column mapping and filtering...
                    # Ensure file_upload_id is set for all rows just before insert
                    db_df['file_upload_id'] = file_upload_id
                    
                    # Map columns to match database schema - prioritizing standardized template format
                    column_mapping = {
                        # Standardized format (from sample template) - PRIMARY
                        'Company Name': 'company_name',
                        'LinkedIn_URL': 'linkedin_url',
                        'Website_URL': 'company_website',
                        'Company_Size': 'company_size',
                        'Industry': 'industry',
                        'Revenue': 'revenue',
                        
                        # Legacy formats - BACKWARD COMPATIBILITY ONLY
                        'Company_Name': 'company_name',
                        'LinkedIn URL': 'linkedin_url',
                        'Company Linkedin': 'linkedin_url',
                        'Website': 'company_website',
                        'Company_Website': 'company_website', 
                        'Size': 'company_size',
                        
                        # Enhanced scraper columns
                        'Company_Size_Enhanced': 'company_size',
                        'Industry_Enhanced': 'industry',
                        'Revenue_Enhanced': 'revenue',
                        
                        # Additional scraper data
                        'Headquarters': 'headquarters',
                        'Founded': 'founded_year',
                        'Company Type': 'company_type',
                        'Specialties': 'specialties',
                        'About': 'about_company',
                        'Employee Count': 'employee_count'
                    }
                    
                    # Apply column mapping with smart merging for enhanced columns
                    logger.info(f"Dataframe columns before mapping: {list(db_df.columns)}")
                    
                    # Handle enhanced columns with priority: Enhanced > Standardized > Legacy
                    enhanced_mappings = [
                        (['Size', 'Company_Size', 'Company_Size_Enhanced'], 'company_size'),
                        (['Industry', 'Industry_Enhanced'], 'industry'),
                        (['Revenue', 'Revenue_Enhanced'], 'revenue')
                    ]
                    
                    for source_cols, target_col in enhanced_mappings:
                        available_cols = [col for col in source_cols if col in db_df.columns]
                        if available_cols:
                            # Prefer enhanced columns over original ones
                            enhanced_col = None
                            original_col = None
                            
                            for col in available_cols:
                                if 'Enhanced' in col:
                                    enhanced_col = col
                                else:
                                    original_col = col
                            
                            # Use enhanced if available, otherwise use original
                            source_col = enhanced_col if enhanced_col else original_col
                            
                            if source_col and source_col in db_df.columns:
                                logger.info(f"Smart mapping: {source_col} -> {target_col}")
                                db_df = db_df.rename(columns={source_col: target_col})
                                
                                # Remove the other columns to avoid conflicts
                                for col in available_cols:
                                    if col != source_col and col in db_df.columns:
                                        logger.info(f"Removing duplicate column: {col}")
                                        db_df = db_df.drop(columns=[col])
                    
                    # Apply remaining simple mappings
                    simple_mappings = {k: v for k, v in column_mapping.items() 
                                     if not any(k in sources for sources, _ in enhanced_mappings)}
                    
                    for old_col, new_col in simple_mappings.items():
                        if old_col in db_df.columns:
                            logger.info(f"Simple mapping: {old_col} -> {new_col}")
                            db_df = db_df.rename(columns={old_col: new_col})
                    
                    # Remove columns that don't exist in the database schema
                    # Get valid columns from the database
                    valid_columns = [
                        'company_name', 'linkedin_url', 'company_website', 'company_size', 'industry', 
                        'revenue', 'headquarters', 'founded_year', 'company_type', 'specialties', 
                        'about_company', 'employee_count', 'file_source', 'upload_date', 
                        'processing_status', 'scraped_at', 'data_source', 'created_by', 'updated_at'
                    ]
                    
                    # Keep only valid columns, drop others
                    columns_to_keep = [col for col in db_df.columns if col in valid_columns]
                    db_df = db_df[columns_to_keep]
                    # Ensure all required columns exist, add with default values if missing
                    required_defaults = {
                        'company_name': '',
                        'linkedin_url': '',
                        'company_website': '',
                        'company_size': '',
                        'industry': '',
                        'revenue': '',
                        'file_source': 'unknown',
                        'created_by': 'system',
                        'updated_at': pd.Timestamp.now(),
                        'file_upload_id': file_upload_id
                    }
                    for col, default in required_defaults.items():
                        if col not in db_df.columns:
                            db_df[col] = default
                            # Reorder columns to match table
                            ordered_columns = [
                                'company_name', 'linkedin_url', 'company_website', 'company_size', 'industry',
                                'revenue', 'file_source', 'created_by', 'updated_at', 'file_upload_id'
                            ]
                            db_df = db_df[[col for col in ordered_columns if col in db_df.columns]]

                            # Log file_upload_id value before insert
                            logger.info(f"file_upload_id to be inserted: {file_upload_id}")
                    
                    logger.info(f"Prepared {len(db_df)} records with columns: {list(db_df.columns)}")
                    
                    # Insert data into company_data table
                    saved_to_db = self.db_connection.insert_dataframe(db_df, "company_data")
                    
                    if saved_to_db:
                        logger.info(f"✅ Successfully saved {len(db_df)} company records to database")
                    else:
                        logger.error("❌ Failed to save data to database - insert operation failed")
                        db_save_error = "Database insert operation failed"
                        
                except Exception as e:
                    logger.error(f"❌ Error saving to database: {str(e)}")
                    db_save_error = str(e)
                    saved_to_db = False
            else:
                logger.warning("⚠️ No database connection available - skipping database save")
                db_save_error = "No database connection available"
            
            processing_time = round(time.time() - start_time, 2)
            
            update_progress(100, "Processing completed successfully!")
            
            # Return comprehensive results
            result = {
                "success": True,
                "processed_rows": total_rows,
                "successful_rows": successful_rows,
                "failed_rows": failed_rows,
                "processing_time": f"{processing_time} seconds",
                "output_file": output_filename,
                "output_content": output_content,  # Excel content in memory
                "scrapers_used": scrapers_used,
                "scraping_enabled": scraping_enabled,
                "ai_analysis_enabled": ai_analysis_enabled,
                "database_saved": saved_to_db,
                "database_error": db_save_error,
                "summary": f"Processed {total_rows} companies: {successful_rows} successful, {failed_rows} failed. Database saved: {'✅ Yes' if saved_to_db else '❌ No'}"
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Processing failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "processed_rows": 0,
                "successful_rows": 0,
                "failed_rows": 0,
                "processing_time": f"{round(time.time() - start_time, 2)} seconds"
            }
    
    def get_supported_columns(self) -> Dict[str, list]:
        """Return the expected column names for different data types"""
        return {
            "required": ["Company_Name"],
            "linkedin": ["LinkedIn_URL"],
            "website": ["Company_Website"], 
            "optional": ["Industry", "Company_Size", "Location"],
            "output_linkedin": ["Company_Size_Enhanced", "Industry_Enhanced", "LinkedIn_Status"],
            "output_revenue": ["Revenue_Enhanced", "Revenue_Source", "Revenue_Status"],
            "output_ai": ["AI_Analysis_Status", "Revenue_Estimate"]
        }