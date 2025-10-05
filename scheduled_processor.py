#!/usr/bin/env python3
"""
Scheduled Job Processor for JSON File Upload Workflow
Processes pending files from file_upload table using LinkedIn scraping logic
"""

import os
import sys
import json
import pandas as pd
import subprocess
import tempfile
import logging
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
    from database_config.config_loader import get_scheduler_interval, is_single_job_per_user_enabled
    DATABASE_AVAILABLE = True
except ImportError as e:
    print(f"❌ Database dependencies not available: {e}")
    DATABASE_AVAILABLE = False

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduled_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ScheduledJobProcessor:
    """Scheduled job processor for file uploads"""
    
    def __init__(self):
        self.processor = None
        self.db_connection = None
        self.initialize()
        
    def initialize(self):
        """Initialize processor and database connection"""
        if not PROCESSOR_AVAILABLE:
            logger.error("File upload processor not available")
            return False
            
        try:
            self.processor = FileUploadProcessor()
            self.db_connection = get_database_connection("postgresql")
            
            if not self.db_connection or not self.db_connection.test_connection():
                logger.error("Database connection failed")
                return False
                
            logger.info("✅ Scheduled job processor initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize processor: {e}")
            return False
    
    def process_pending_files(self):
        """Process all pending file uploads"""
        if not self.processor:
            logger.error("Processor not initialized")
            return False
            
        try:
            logger.info("🔄 Starting scheduled processing of pending files...")
            
            # Get pending uploads with single job per user logic
            if is_single_job_per_user_enabled():
                pending_uploads = self.processor.get_pending_uploads_by_user_queue()
                logger.info("🔒 Using single job per user processing")
            else:
                pending_uploads = self.processor.get_pending_uploads()
                logger.info("🔓 Using multi-job processing")
            
            if pending_uploads is None or pending_uploads.empty:
                logger.info("ℹ️ No pending uploads found")
                return True
            
            logger.info(f"📋 Found {len(pending_uploads)} pending uploads")
            
            success_count = 0
            failure_count = 0
            
            for _, upload in pending_uploads.iterrows():
                file_upload_id = upload['id']
                file_name = upload['file_name']
                
                logger.info(f"🔄 Processing: {file_name} (ID: {file_upload_id})")
                
                try:
                    if self.processor.process_uploaded_file(file_upload_id):
                        success_count += 1
                        logger.info(f"✅ Completed: {file_name}")
                    else:
                        failure_count += 1
                        logger.error(f"❌ Failed: {file_name}")
                        
                except Exception as e:
                    failure_count += 1
                    logger.error(f"❌ Error processing {file_name}: {e}")
            
            # Log summary
            total = success_count + failure_count
            logger.info(f"📊 Batch processing complete:")
            logger.info(f"   ✅ Successful: {success_count}")
            logger.info(f"   ❌ Failed: {failure_count}")
            logger.info(f"   📋 Total: {total}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"❌ Error in scheduled processing: {e}")
            return False
    
    def process_single_file(self, file_upload_id):
        """Process a single file upload by ID"""
        if not self.processor:
            logger.error("Processor not initialized")
            return False
            
        try:
            logger.info(f"🔄 Processing single file: ID {file_upload_id}")
            
            if self.processor.process_uploaded_file(file_upload_id):
                logger.info(f"✅ Successfully processed file ID {file_upload_id}")
                return True
            else:
                logger.error(f"❌ Failed to process file ID {file_upload_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error processing file ID {file_upload_id}: {e}")
            return False
    
    def get_processing_statistics(self):
        """Get and log processing statistics"""
        if not self.processor:
            logger.error("Processor not initialized")
            return {}
            
        try:
            stats = self.processor.get_upload_statistics()
            
            logger.info("📊 Processing Statistics:")
            logger.info(f"   📁 Total Uploads: {stats.get('total_uploads', 0)}")
            logger.info(f"   ⏳ Pending: {stats.get('pending_uploads', 0)}")
            logger.info(f"   ✅ Completed: {stats.get('completed_uploads', 0)}")
            logger.info(f"   ❌ Failed: {stats.get('failed_uploads', 0)}")
            logger.info(f"   🏢 Total Records: {stats.get('total_processed_records', 0)}")
            
            return stats
            
        except Exception as e:
            logger.error(f"❌ Error getting statistics: {e}")
            return {}
    
    def cleanup_old_logs(self, days_to_keep=30):
        """Clean up old log files"""
        try:
            log_dir = os.path.dirname(log_file)
            current_time = time.time()
            days_in_seconds = days_to_keep * 24 * 60 * 60
            
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(log_dir, filename)
                    if os.path.getmtime(file_path) < (current_time - days_in_seconds):
                        os.remove(file_path)
                        logger.info(f"🗑️ Cleaned up old log file: {filename}")
                        
        except Exception as e:
            logger.error(f"❌ Error cleaning up logs: {e}")

def run_scheduled_processing():
    """Main function for scheduled processing"""
    logger.info("🚀 Starting scheduled file processing job")
    logger.info(f"📅 Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    processor = ScheduledJobProcessor()
    
    if not processor.processor:
        logger.error("❌ Failed to initialize processor - exiting")
        return False
    
    # Process pending files
    success = processor.process_pending_files()
    
    # Get statistics
    processor.get_processing_statistics()
    
    # Cleanup old logs
    processor.cleanup_old_logs()
    
    logger.info(f"🏁 Scheduled processing completed: {'✅ Success' if success else '❌ No files processed'}")
    logger.info(f"📅 End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success

def run_continuous_processing(interval_minutes=None):
    """Run continuous processing with configurable interval"""
    if interval_minutes is None:
        interval_minutes = get_scheduler_interval()
    """Run continuous processing with specified interval"""
    logger.info(f"🔄 Starting continuous processing mode (interval: {interval_minutes} minutes)")
    
    while True:
        try:
            run_scheduled_processing()
            
            logger.info(f"⏰ Waiting {interval_minutes} minutes before next run...")
            time.sleep(interval_minutes * 60)
            
        except KeyboardInterrupt:
            logger.info("⏹️ Continuous processing stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in continuous processing: {e}")
            logger.info(f"⏰ Waiting {interval_minutes} minutes before retry...")
            time.sleep(interval_minutes * 60)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scheduled File Upload Processor")
    parser.add_argument("--mode", choices=["single", "continuous"], default="single",
                       help="Processing mode: single run or continuous")
    parser.add_argument("--interval", type=int, default=2,
                       help="Interval in minutes for continuous mode (default: 2)")
    parser.add_argument("--file-id", type=int,
                       help="Process specific file ID (single file mode)")
    
    args = parser.parse_args()
    
    if args.file_id:
        # Process single file
        logger.info(f"🎯 Single file processing mode - File ID: {args.file_id}")
        processor = ScheduledJobProcessor()
        if processor.processor:
            processor.process_single_file(args.file_id)
            processor.get_processing_statistics()
        
    elif args.mode == "continuous":
        # Continuous processing mode
        run_continuous_processing(args.interval)
        
    else:
        # Single run mode (default)
        run_scheduled_processing()
    
    logger.info("🏁 Scheduled processor finished")