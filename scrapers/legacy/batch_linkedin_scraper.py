#!/usr/bin/env python3
"""
Batch LinkedIn Scraper - Process companies in small batches to avoid blocking
"""

import pandas as pd
import time
import logging
from linkedin_company_scraper_enhanced import process_excel_file_enhanced

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def process_in_batches(input_file, batch_size=2, delay_between_batches=60):
    """
    Process LinkedIn companies in small batches with delays
    
    Args:
        input_file: Excel file with LinkedIn URLs
        batch_size: Number of companies per batch (default: 2)
        delay_between_batches: Seconds to wait between batches (default: 60)
    """
    try:
        # Read the full file
        df = pd.read_excel(input_file)
        total_companies = len(df)
        
        logger.info(f"Processing {total_companies} companies in batches of {batch_size}")
        
        # Process in batches
        for batch_start in range(0, total_companies, batch_size):
            batch_end = min(batch_start + batch_size, total_companies)
            batch_num = (batch_start // batch_size) + 1
            
            logger.info(f"Starting batch {batch_num}: companies {batch_start+1} to {batch_end}")
            
            # Create batch file
            batch_df = df.iloc[batch_start:batch_end].copy()
            batch_file = f"batch_{batch_num}.xlsx"
            batch_df.to_excel(batch_file, index=False)
            
            # Process batch
            try:
                process_excel_file_enhanced(
                    input_file=batch_file,
                    url_column='LinkedIn_URL',
                    size_column='Company_Size',
                    output_file=f"batch_{batch_num}_results.xlsx"
                )
                
                # Read results and update main file
                batch_results = pd.read_excel(f"batch_{batch_num}_results.xlsx")
                for i, result_row in batch_results.iterrows():
                    original_index = batch_start + i
                    df.at[original_index, 'Company_Size'] = result_row['Company_Size']
                
                logger.info(f"Batch {batch_num} completed successfully")
                
            except Exception as e:
                logger.error(f"Batch {batch_num} failed: {str(e)}")
            
            # Save progress
            df.to_excel(input_file.replace('.xlsx', '_batch_results.xlsx'), index=False)
            
            # Wait before next batch (except for last batch)
            if batch_end < total_companies:
                logger.info(f"Waiting {delay_between_batches} seconds before next batch...")
                time.sleep(delay_between_batches)
        
        # Save final results
        final_output = input_file.replace('.xlsx', '_final_results.xlsx')
        df.to_excel(final_output, index=False)
        
        # Show summary
        successful = df[df['Company_Size'].notna() & 
                       ~df['Company_Size'].isin(['Blocked by LinkedIn', 'Not Found', 'Error', ''])].shape[0]
        
        logger.info(f"BATCH PROCESSING COMPLETE!")
        logger.info(f"Total processed: {total_companies}")
        logger.info(f"Successful extractions: {successful}")
        logger.info(f"Success rate: {successful/total_companies*100:.1f}%")
        logger.info(f"Final results saved to: {final_output}")
        
        return final_output
        
    except Exception as e:
        logger.error(f"Batch processing failed: {str(e)}")
        return None

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        batch_size = int(sys.argv[2]) if len(sys.argv) > 2 else 2
        delay = int(sys.argv[3]) if len(sys.argv) > 3 else 60
        
        process_in_batches(input_file, batch_size, delay)
    else:
        print("Usage: python batch_linkedin_scraper.py <excel_file> [batch_size] [delay_seconds]")
        print("Example: python batch_linkedin_scraper.py Test4_cleared.xlsx 2 60")