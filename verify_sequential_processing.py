"""
Verification Script for Sequential File Processing Fix

This script monitors the database to verify that files are being processed
sequentially (one at a time) rather than simultaneously.

Usage: python verify_sequential_processing.py
"""

import psycopg2
import time
import sys
import os
from datetime import datetime
from collections import defaultdict

# Add database_config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'database_config'))

from postgresql_config import PostgreSQLConfig

class ProcessingMonitor:
    def __init__(self):
        self.config = PostgreSQLConfig()
        self.params = self.config.get_connection_params()
        self.processing_history = []
        self.violation_count = 0
        
    def get_connection(self):
        return psycopg2.connect(**self.params)
    
    def check_current_status(self):
        """Check current processing status"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get files in processing status
        cursor.execute("""
            SELECT 
                id, 
                file_name, 
                processing_status,
                uploaded_by,
                upload_date
            FROM file_upload 
            WHERE processing_status IN ('pending', 'processing')
            ORDER BY upload_date ASC
        """)
        
        files = cursor.fetchall()
        
        # Count processing files
        processing_files = [f for f in files if f[2] == 'processing']
        pending_files = [f for f in files if f[2] == 'pending']
        
        cursor.close()
        conn.close()
        
        return {
            'processing': processing_files,
            'pending': pending_files,
            'total_active': len(files)
        }
    
    def display_status(self, status_data):
        """Display current status"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        processing_count = len(status_data['processing'])
        pending_count = len(status_data['pending'])
        
        print(f"\n{'='*80}")
        print(f"⏰ Timestamp: {timestamp}")
        print(f"{'='*80}")
        
        # Check for violations (more than 1 file processing)
        if processing_count > 1:
            self.violation_count += 1
            print(f"⚠️  VIOLATION DETECTED: {processing_count} files processing simultaneously!")
            print(f"   Total violations so far: {self.violation_count}")
        elif processing_count == 1:
            print(f"✅ CORRECT: Only 1 file is processing")
        else:
            print(f"ℹ️  No files currently processing")
        
        print(f"\n📊 Status Summary:")
        print(f"   🔄 Processing: {processing_count} file(s)")
        print(f"   ⏳ Pending: {pending_count} file(s)")
        print(f"   📋 Total Active: {status_data['total_active']} file(s)")
        
        if status_data['processing']:
            print(f"\n🔄 Currently Processing:")
            for file in status_data['processing']:
                file_id, file_name, status, user, upload_date = file
                print(f"   - {file_name} (ID: {file_id}, User: {user})")
        
        if status_data['pending'] and len(status_data['pending']) <= 5:
            print(f"\n⏳ Pending Queue:")
            for file in status_data['pending'][:5]:
                file_id, file_name, status, user, upload_date = file
                print(f"   - {file_name} (ID: {file_id}, User: {user})")
        elif status_data['pending']:
            print(f"\n⏳ Pending Queue: {len(status_data['pending'])} files (showing first 5):")
            for file in status_data['pending'][:5]:
                file_id, file_name, status, user, upload_date = file
                print(f"   - {file_name} (ID: {file_id}, User: {user})")
    
    def get_processing_stats(self):
        """Get overall processing statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                processing_status,
                COUNT(*) as count
            FROM file_upload
            GROUP BY processing_status
            ORDER BY processing_status
        """)
        
        stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return stats
    
    def display_summary(self):
        """Display final summary"""
        stats = self.get_processing_stats()
        
        print(f"\n{'='*80}")
        print(f"📊 FINAL SUMMARY")
        print(f"{'='*80}")
        print(f"Total violation checks: {self.violation_count}")
        
        if self.violation_count == 0:
            print(f"✅ SUCCESS: No violations detected! Files are processing sequentially.")
        else:
            print(f"⚠️  WARNING: {self.violation_count} violations detected!")
            print(f"   Multiple files were processing simultaneously.")
        
        print(f"\n📈 Overall File Status Distribution:")
        for status, count in stats:
            print(f"   {status}: {count} file(s)")
    
    def monitor(self, duration_seconds=300, interval_seconds=5):
        """Monitor processing for specified duration"""
        print(f"🔍 Starting Sequential Processing Monitor")
        print(f"   Duration: {duration_seconds} seconds")
        print(f"   Check Interval: {interval_seconds} seconds")
        print(f"   Press Ctrl+C to stop monitoring early")
        
        start_time = time.time()
        check_count = 0
        
        try:
            while (time.time() - start_time) < duration_seconds:
                check_count += 1
                status_data = self.check_current_status()
                self.display_status(status_data)
                
                # Store history
                self.processing_history.append({
                    'timestamp': datetime.now(),
                    'processing_count': len(status_data['processing']),
                    'pending_count': len(status_data['pending'])
                })
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print(f"\n\n⏹️  Monitoring stopped by user")
        
        print(f"\n\n{'='*80}")
        print(f"Monitoring completed: {check_count} checks performed")
        self.display_summary()

def main():
    """Main entry point"""
    print("="*80)
    print("Sequential File Processing Verification Tool")
    print("="*80)
    
    monitor = ProcessingMonitor()
    
    # Check if there are any active files
    initial_status = monitor.check_current_status()
    
    if initial_status['total_active'] == 0:
        print("\n⚠️  No pending or processing files found in the database.")
        print("   Please upload some files first, then run this script.")
        return
    
    print(f"\n✅ Found {initial_status['total_active']} active file(s)")
    print(f"   Processing: {len(initial_status['processing'])}")
    print(f"   Pending: {len(initial_status['pending'])}")
    
    # Ask user for monitoring duration
    try:
        duration = input("\n⏱️  Enter monitoring duration in seconds (default 300): ")
        duration = int(duration) if duration.strip() else 300
    except ValueError:
        duration = 300
    
    try:
        interval = input("⏱️  Enter check interval in seconds (default 5): ")
        interval = int(interval) if interval.strip() else 5
    except ValueError:
        interval = 5
    
    print("\n" + "="*80)
    monitor.monitor(duration_seconds=duration, interval_seconds=interval)
    print("="*80)

if __name__ == "__main__":
    main()
