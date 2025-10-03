#!/usr/bin/env python3
"""
Real-time Progress Monitor for LinkedIn Scraper
"""

import pandas as pd
import os
import time
from datetime import datetime

def monitor_progress():
    """Monitor the progress of the stealth scraper"""
    result_file = "Test4_stealth_results.xlsx"
    log_file = "linkedin_scraper_stealth.log"
    
    print("🚀 LINKEDIN STEALTH SCRAPER - LIVE MONITOR")
    print("=" * 50)
    print(f"📊 Monitoring: {result_file}")
    print(f"📝 Log file: {log_file}")
    print("=" * 50)
    
    last_size = 0
    processed_companies = []
    
    while True:
        try:
            # Check if result file exists
            if os.path.exists(result_file):
                # Read current results
                df = pd.read_excel(result_file)
                
                # Count processed entries
                processed = 0
                successful = 0
                
                for index, row in df.iterrows():
                    size = str(row.get('Company_Size', '')).strip()
                    if size and size not in ['', 'nan', 'None']:
                        processed += 1
                        if size not in ['Not Found', 'Error', 'Blocked by LinkedIn']:
                            successful += 1
                            company_url = row.get('LinkedIn_URL', '')
                            if company_url not in processed_companies:
                                processed_companies.append(company_url)
                                print(f"✅ SUCCESS: Row {index+1} - {size}")
                
                # Show current status
                total_companies = len(df)
                if processed > last_size:
                    print(f"\n📈 PROGRESS UPDATE:")
                    print(f"   Processed: {processed}/{total_companies}")
                    print(f"   Successful: {successful}")
                    print(f"   Success Rate: {(successful/processed)*100:.1f}%" if processed > 0 else "0%")
                    print(f"   Time: {datetime.now().strftime('%H:%M:%S')}")
                    last_size = processed
                
                # Check if complete
                if processed >= total_companies:
                    print(f"\n🎉 PROCESSING COMPLETE!")
                    print(f"📊 Final Results:")
                    print(f"   Total Companies: {total_companies}")
                    print(f"   Successful: {successful}")
                    print(f"   Success Rate: {(successful/total_companies)*100:.1f}%")
                    print(f"   Results saved to: {result_file}")
                    break
            
            # Check log file for latest activity
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    if lines:
                        last_line = lines[-1].strip()
                        if "Waiting" in last_line:
                            wait_time = last_line.split("Waiting")[1].split("seconds")[0].strip()
                            print(f"⏳ Waiting {wait_time} seconds before next company...")
            
            time.sleep(10)  # Check every 10 seconds
            
        except KeyboardInterrupt:
            print("\n\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"⚠️ Monitor error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    monitor_progress()